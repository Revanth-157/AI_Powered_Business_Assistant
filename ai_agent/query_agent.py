"""
Query Understanding Agent - parses user intent and extracts entities.
"""
import json
from typing import Optional
from datetime import datetime, timedelta
from .schema import (
    AgentState, StructuredIntent, Entity, Intent
)


class QueryUnderstandingAgent:
    """
    Understands user intent, extracts entities, and classifies business use-case.
    """
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.intent_keywords = {
            Intent.PROMO_PERFORMANCE: ["promotion", "promo", "discount", "sale", "campaign"],
            Intent.INVENTORY_MOVEMENT: ["inventory", "stock", "stockout", "movement", "qty"],
            Intent.REGIONAL_SALES: ["region", "regional", "store", "channel", "area"],
            Intent.CAMPAIGN_IMPACT: ["campaign", "impact", "lift", "effectiveness", "performance"],
            Intent.KPI_DASHBOARD: ["dashboard", "summary", "overview", "snapshot", "kpi"],
        }
        
    def process(self, state: AgentState) -> AgentState:
        """
        Main entry point - processes user message and produces structured intent.
        """
        try:
            user_msg = state.user_message.lower()
            
            # 1. Detect intent from keywords
            detected_intent = self._detect_intent(user_msg)
            
            # 2. Extract entities
            entities = self._extract_entities(user_msg, state)
            
            # 3. Parse time range
            time_range = self._extract_time_range(user_msg)
            
            # 4. Extract filters (region, category, etc.)
            filters = self._extract_filters(user_msg, state)
            
            # 5. Determine if clarification needed
            confidence = self._calculate_confidence(user_msg, entities)
            needs_clarification = confidence < 0.6 or not entities
            clarification_q = self._generate_clarification_question(detected_intent, entities) if needs_clarification else None
            
            # Assemble structured intent
            structured_intent = StructuredIntent(
                intent=detected_intent,
                entities=entities,
                time_range=time_range,
                filters=filters,
                clarification_needed=needs_clarification,
                clarification_question=clarification_q,
                confidence=confidence,
            )
            
            state.structured_intent = structured_intent
            state.updated_at = datetime.utcnow()
            
            if needs_clarification:
                state.requires_clarification = True
                state.clarification_question = clarification_q
                state.response_text = f"I need a bit more info: {clarification_q}"
                
            return state
        
        except Exception as e:
            state.error_messages.append(f"Query Understanding Error: {str(e)}")
            state.structured_intent = StructuredIntent(
                intent=Intent.UNKNOWN,
                entities=[],
                confidence=0.0,
            )
            return state
    
    def _detect_intent(self, user_msg: str) -> Intent:
        """Classify user message into a business intent."""
        for intent, keywords in self.intent_keywords.items():
            if any(kw in user_msg for kw in keywords):
                return intent
        return Intent.UNKNOWN
    
    def _extract_entities(self, user_msg: str, state: AgentState) -> list:
        """Extract entities like time, region, product category."""
        entities = []
        
        # Time entities
        time_patterns = {
            "last week": ("last_week", 0.9),
            "last month": ("last_month", 0.9),
            "last quarter": ("last_quarter", 0.9),
            "last year": ("last_year", 0.9),
            "ytd": ("ytd", 0.9),
            "this quarter": ("this_quarter", 0.9),
        }
        for pattern, (ent_val, conf) in time_patterns.items():
            if pattern in user_msg:
                entities.append(Entity(type="time_period", value=ent_val, confidence=conf))
        
        # Region entities
        regions = ["north", "south", "east", "west"]
        for region in regions:
            if region in user_msg:
                entities.append(Entity(type="region", value=region, confidence=0.85))
        
        # Category entities
        categories = ["carbonated", "juice", "water", "dairy", "energy"]
        for cat in categories:
            if cat in user_msg:
                entities.append(Entity(type="category", value=cat, confidence=0.85))
        
        # Store format
        formats = ["hypermarket", "supermarket", "convenience", "discounters"]
        for fmt in formats:
            if fmt in user_msg:
                entities.append(Entity(type="store_format", value=fmt, confidence=0.85))
        
        return entities
    
    def _extract_time_range(self, user_msg: str) -> Optional[dict]:
        """Parse time range from message."""
        today = datetime.utcnow().date()
        
        if "last week" in user_msg:
            start = today - timedelta(days=7)
            return {"start": start.isoformat(), "end": today.isoformat()}
        elif "last month" in user_msg:
            start = today - timedelta(days=30)
            return {"start": start.isoformat(), "end": today.isoformat()}
        elif "last quarter" in user_msg:
            start = today - timedelta(days=90)
            return {"start": start.isoformat(), "end": today.isoformat()}
        elif "last year" in user_msg:
            start = today - timedelta(days=365)
            return {"start": start.isoformat(), "end": today.isoformat()}
        
        return None
    
    def _extract_filters(self, user_msg: str, state: AgentState) -> dict:
        """Extract filter predicates from message."""
        filters = {}
        
        # Apply role-based region restriction
        if state.accessible_regions:
            filters["regions"] = state.accessible_regions
        
        # Extract region filter
        regions = ["north", "south", "east", "west"]
        for region in regions:
            if region in user_msg:
                filters["region"] = region
                break
        
        # Extract category filter
        categories = ["carbonated", "juice", "water", "dairy", "energy"]
        for cat in categories:
            if cat in user_msg:
                filters["category"] = cat
                break
        
        return filters
    
    def _calculate_confidence(self, user_msg: str, entities: list) -> float:
        """Estimate confidence in the extracted intent."""
        base = 0.5
        if len(user_msg) > 10:
            base += 0.15
        if len(entities) > 0:
            base += 0.25
        if "?" not in user_msg:
            base += 0.1
        return min(base, 1.0)
    
    def _generate_clarification_question(self, intent: Intent, entities: list) -> str:
        """Generate a clarifying question for the user."""
        if not entities:
            return "Could you specify a time period or dimension (e.g., region, category)?"
        if intent == Intent.UNKNOWN:
            return "Are you asking about promotions, inventory, regional sales, campaigns, or general KPIs?"
        return "Can you provide more details about what metric you'd like to see?"
