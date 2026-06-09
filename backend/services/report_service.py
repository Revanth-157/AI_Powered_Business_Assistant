"""
Report service - handles report generation and management.
"""
import logging
import json
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
import uuid

from database.models import ReportModel, UserModel
from schemas.schemas import ReportCreate, ReportResponse, ReportListResponse

logger = logging.getLogger(__name__)


class ReportService:
    """Service for managing reports."""
    
    @staticmethod
    def create_report(
        db: Session,
        user_id: str,
        session_id: Optional[str],
        ai_result: Optional[object],
        report_request: ReportCreate
    ) -> ReportResponse:
        """Create a new report from AI results."""
        
        # Extract data from AI result
        if ai_result:
            kpis = ai_result.response_data.get("kpis", [])
            insights = ai_result.response_data.get("insight", {})
            visualizations = ai_result.response_data.get("visualizations", [])
        else:
            kpis = []
            insights = {}
            visualizations = []
        
        # Create report record
        report = ReportModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id,
            title=report_request.title,
            summary=f"Report generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
            executive_summary=insights.get("summary", ""),
            kpis=json.dumps(kpis),
            insights=json.dumps(insights),
            visualizations=json.dumps(visualizations),
            intent=report_request.intent,
            report_type=report_request.report_type
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        logger.info(f"Created report {report.id} for user {user_id}")
        
        return ReportResponse(
            id=report.id,
            user_id=report.user_id,
            title=report.title,
            summary=report.summary,
            executive_summary=report.executive_summary,
            kpis=kpis,
            insights=insights,
            visualizations=visualizations,
            report_type=report.report_type,
            is_shared=report.is_shared,
            is_public=report.is_public,
            created_at=report.created_at,
            updated_at=report.updated_at
        )
    
    @staticmethod
    def get_report(
        db: Session,
        user_id: str,
        report_id: str
    ) -> Optional[ReportResponse]:
        """Retrieve a report (check ownership)."""
        
        report = db.query(ReportModel).filter(
            ReportModel.id == report_id,
            ReportModel.user_id == user_id
        ).first()
        
        if not report:
            return None
        
        return ReportResponse(
            id=report.id,
            user_id=report.user_id,
            title=report.title,
            summary=report.summary,
            executive_summary=report.executive_summary,
            kpis=json.loads(report.kpis) if report.kpis else [],
            insights=json.loads(report.insights) if report.insights else {},
            visualizations=json.loads(report.visualizations) if report.visualizations else [],
            report_type=report.report_type,
            is_shared=report.is_shared,
            is_public=report.is_public,
            created_at=report.created_at,
            updated_at=report.updated_at
        )
    
    @staticmethod
    def list_user_reports(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[ReportListResponse], int]:
        """List all reports for a user."""
        
        # Get total count
        total = db.query(ReportModel).filter(
            ReportModel.user_id == user_id
        ).count()
        
        # Get paginated results
        reports = db.query(ReportModel).filter(
            ReportModel.user_id == user_id
        ).order_by(
            ReportModel.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        responses = [
            ReportListResponse(
                id=r.id,
                title=r.title,
                report_type=r.report_type,
                created_at=r.created_at,
                updated_at=r.updated_at,
                is_shared=r.is_shared
            )
            for r in reports
        ]
        
        return responses, total
    
    @staticmethod
    def share_report(
        db: Session,
        user_id: str,
        report_id: str,
        share_with_user_ids: List[str],
        is_public: bool = False
    ) -> Optional[ReportResponse]:
        """Share a report with other users."""
        
        report = db.query(ReportModel).filter(
            ReportModel.id == report_id,
            ReportModel.user_id == user_id
        ).first()
        
        if not report:
            return None
        
        report.is_shared = True
        report.is_public = is_public
        report.shared_with = share_with_user_ids
        
        db.commit()
        db.refresh(report)
        
        logger.info(f"Shared report {report_id} with {len(share_with_user_ids)} users")
        
        return ReportResponse(
            id=report.id,
            user_id=report.user_id,
            title=report.title,
            summary=report.summary,
            executive_summary=report.executive_summary,
            report_type=report.report_type,
            is_shared=report.is_shared,
            is_public=report.is_public,
            created_at=report.created_at,
            updated_at=report.updated_at
        )
    
    @staticmethod
    def export_report(
        report: ReportResponse,
        format: str = "json"
    ) -> str:
        """
        Export report in different formats.
        
        Args:
            report: ReportResponse object
            format: "json", "csv", "excel" (excel requires additional setup)
        
        Returns:
            Formatted report string
        """
        
        if format == "json":
            return json.dumps(report.dict(), indent=2, default=str)
        
        elif format == "csv":
            # Simple CSV format with KPIs
            lines = [
                f"Report: {report.title}",
                f"Created: {report.created_at}",
                "",
                "KPIs:"
            ]
            
            if report.kpis:
                lines.append("Metric,Value,Unit")
                for kpi in report.kpis:
                    lines.append(f'"{kpi.metric_name}",{kpi.value},"{kpi.unit or ""}"')
            
            return "\n".join(lines)
        
        else:
            logger.warning(f"Unsupported export format: {format}")
            return json.dumps(report.dict(), indent=2, default=str)
    
    @staticmethod
    def delete_report(
        db: Session,
        user_id: str,
        report_id: str
    ) -> bool:
        """Delete a report (owner only)."""
        
        report = db.query(ReportModel).filter(
            ReportModel.id == report_id,
            ReportModel.user_id == user_id
        ).first()
        
        if not report:
            return False
        
        db.delete(report)
        db.commit()
        
        logger.info(f"Deleted report {report_id}")
        return True
