"""
Chat/Conversation service - handles user interactions with AI agents.
"""
import logging
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.models import ConversationModel, SessionModel
from schemas.schemas import (
    ConversationRequest, ConversationResponse, SessionResponse,
    EntityExtraction, KPIResult, InsightResult, VisualizationResult
)

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat interactions."""
    
    @staticmethod
    def get_or_create_session(
        db: Session,
        user_id: str,
        session_id: Optional[str] = None,
        title: Optional[str] = None
    ) -> SessionModel:
        """Get existing session or create new one."""
        
        if session_id:
            session = db.query(SessionModel).filter(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id
            ).first()
            if session:
                return session
        
        # Create new session
        session = SessionModel(
            user_id=user_id,
            title=title or "New Conversation",
            is_active=True
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"Created new session {session.id} for user {user_id}")
        return session
    
    @staticmethod
    def process_conversation(
        db: Session,
        user_id: str,
        request: ConversationRequest,
        workflow: Any  # FMCGAgentWorkflow
    ) -> ConversationResponse:
        """
        Process user message through AI agents and store conversation.
        """
        start_time = time.time()
        
        # Get or create session
        session = ChatService.get_or_create_session(
            db, user_id, request.session_id
        )
        
        # Call AI workflow
        try:
            ai_result = workflow.process(
                user_message=request.message,
                session_id=session.id,
                user_id=user_id
            )
        except Exception as e:
            logger.error(f"AI workflow error: {str(e)}")
            error_msg = f"AI processing failed: {str(e)}"
            ai_result = None
        
        # Parse AI results
        if ai_result:
            # Extract data from AI result
            kpis_data = ai_result.response_data.get("kpis", [])
            insights_data = ai_result.response_data.get("insight", {})
            viz_data = ai_result.response_data.get("visualizations", [])
            
            # Convert to schema format
            kpis = [
                KPIResult(
                    metric_name=k.get("metric_name", "Unknown"),
                    value=k.get("value"),
                    unit=k.get("unit"),
                    dimensions=k.get("dimensions")
                )
                for k in (kpis_data if isinstance(kpis_data, list) else [kpis_data])
            ]
            
            insights = InsightResult(
                summary=insights_data.get("summary", ""),
                narrative=insights_data.get("narrative", ""),
                anomalies=insights_data.get("anomalies", []),
                recommendations=insights_data.get("recommendations", []),
                confidence=insights_data.get("confidence", 0.0)
            ) if insights_data else None
            
            visualizations = [
                VisualizationResult(
                    chart_type=v.get("chart_type", "unknown"),
                    title=v.get("title", "Chart"),
                    data=v.get("data", []),
                    vega_spec=v.get("vega_spec")
                )
                for v in (viz_data if isinstance(viz_data, list) else [])
            ]
            
            assistant_response = ai_result.response_text
            entities = [
                EntityExtraction(
                    type=e.type,
                    value=e.value,
                    confidence=e.confidence
                )
                for e in (ai_result.structured_intent.entities if ai_result.structured_intent else [])
            ]
            error_msg = None
        else:
            kpis = []
            insights = None
            visualizations = []
            assistant_response = "Unable to process your request. Please try again."
            entities = []
            error_msg = error_msg
        
        # Store conversation in database
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        conversation = ConversationModel(
            session_id=session.id,
            user_id=user_id,
            user_message=request.message,
            assistant_response=assistant_response,
            intent=request.intent or (ai_result.structured_intent.intent.value if ai_result and ai_result.structured_intent else None),
            entities=json.dumps([e.dict() for e in entities]) if entities else None,
            kpis=json.dumps([k.dict() for k in kpis]) if kpis else None,
            confidence_score=ai_result.structured_intent.confidence if ai_result and ai_result.structured_intent else None,
            processing_time_ms=processing_time_ms,
            error_message=error_msg
        )
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Conversation {conversation.id} stored for user {user_id}")
        
        # Build response
        response = ConversationResponse(
            id=conversation.id,
            session_id=session.id,
            user_message=request.message,
            assistant_response=assistant_response,
            intent=ai_result.structured_intent.intent.value if ai_result and ai_result.structured_intent else None,
            entities=entities,
            kpis=kpis if kpis else None,
            insights=insights,
            visualizations=visualizations if visualizations else None,
            confidence_score=ai_result.structured_intent.confidence if ai_result and ai_result.structured_intent else None,
            processing_time_ms=processing_time_ms,
            error_message=error_msg,
            created_at=conversation.created_at
        )
        
        return response
    
    @staticmethod
    def get_session_history(
        db: Session,
        user_id: str,
        session_id: str,
        limit: int = 50
    ) -> list:
        """Get conversation history for a session."""
        
        # Verify user owns session
        session = db.query(SessionModel).filter(
            SessionModel.id == session_id,
            SessionModel.user_id == user_id
        ).first()
        
        if not session:
            return []
        
        conversations = db.query(ConversationModel).filter(
            ConversationModel.session_id == session_id
        ).order_by(
            ConversationModel.created_at.desc()
        ).limit(limit).all()
        
        return conversations
    
    @staticmethod
    def get_user_sessions(
        db: Session,
        user_id: str,
        limit: int = 20
    ) -> list:
        """Get all sessions for a user."""
        
        sessions = db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.is_active == True
        ).order_by(
            SessionModel.updated_at.desc()
        ).limit(limit).all()
        
        return sessions
