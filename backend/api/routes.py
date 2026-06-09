"""
FastAPI routes for FMCG BI Assistant backend.
"""
import logging
from typing import Optional, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from schemas.schemas import (
    TokenRequest, TokenResponse, UserResponse, UserCreate,
    ConversationRequest, ConversationResponse,
    AnalyticsRequest, AnalyticsResponse,
    ReportCreate, ReportResponse, ReportListResponse, ReportExportRequest,
    PaginationParams, ErrorResponse,
    TextToSQLRequest, TextToSQLResponse, SchemaInfoResponse,
    SampleQueriesResponse, QueryExplanationResponse,
    InsightReport, InsightGenerationRequest, ActionPlan
)
from auth import (
    hash_password, verify_password, verify_token,
    create_access_token, create_refresh_token, extract_token_from_header
)
from services.user_service import UserService
from services.chat_service import ChatService
from services.analytics_service import AnalyticsService
from services.report_service import ReportService
from services.text_to_sql_service import TextToSQLService
from services.insight_service import InsightService
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix=settings.API_PREFIX)

# Global workflow (will be set in main.py)
workflow = None


# ==================== Authentication Routes ====================

@router.post("/auth/register", response_model=UserResponse, tags=["auth"])
async def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        return UserService.create_user(db, user_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
async def login(request: TokenRequest, db: Session = Depends(get_db)):
    """Login with email and password."""
    
    user = UserService.authenticate_user(db, request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create tokens
    access_token, access_expires = create_access_token(
        {"sub": user.id, "email": user.email}
    )
    refresh_token, refresh_expires = create_refresh_token(
        {"sub": user.id, "email": user.email}
    )
    
    logger.info(f"User {user.username} logged in")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    )


@router.post("/auth/refresh", response_model=TokenResponse, tags=["auth"])
async def refresh_token(request: dict):
    """Refresh access token using refresh token."""
    
    refresh_token_str = request.get("refresh_token")
    payload = verify_token(refresh_token_str)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    
    # Create new access token
    access_token, _ = create_access_token(
        {"sub": user_id}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        expires_in=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    )


# ==================== Helper Functions ====================

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Dependency to get current authenticated user."""
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    token = extract_token_from_header(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    user = UserService.get_user_by_id(db, user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


# ==================== Chat Routes ====================

@router.post("/chat", response_model=ConversationResponse, tags=["chat"])
async def chat(
    request: ConversationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to the AI assistant."""
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI workflow not initialized"
        )
    
    try:
        response = ChatService.process_conversation(
            db, current_user.id, request, workflow
        )
        return response
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/sessions", tags=["chat"])
async def get_sessions(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    params: PaginationParams = Depends()
):
    """Get user's chat sessions."""
    
    sessions = ChatService.get_user_sessions(
        db, current_user.id, params.limit
    )
    
    return {
        "total": len(sessions),
        "sessions": sessions
    }


@router.get("/chat/sessions/{session_id}", tags=["chat"])
async def get_session_history(
    session_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    params: PaginationParams = Depends()
):
    """Get conversation history for a session."""
    
    conversations = ChatService.get_session_history(
        db, current_user.id, session_id, params.limit
    )
    
    return {
        "session_id": session_id,
        "conversations": conversations
    }


# ==================== Analytics Routes ====================

@router.post("/analytics/query", response_model=AnalyticsResponse, tags=["analytics"])
async def analytics_query(
    request: AnalyticsRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute analytics query."""
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI workflow not initialized"
        )
    
    try:
        response = AnalyticsService.execute_analytics(
            db, current_user.id, request, workflow
        )
        return response
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/dashboard", tags=["analytics"])
async def dashboard_snapshot(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard snapshot."""
    
    try:
        dashboard = AnalyticsService.get_dashboard_snapshot(
            db, current_user.id, workflow=workflow
        )
        return dashboard
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/trends/{metric}", tags=["analytics"])
async def get_metric_trends(
    metric: str,
    days: int = 30,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical trends for a metric."""
    
    trends = AnalyticsService.get_trends(
        db, current_user.id, metric, days
    )
    
    return {
        "metric": metric,
        "days": days,
        "trends": trends
    }


# ==================== Report Routes ====================

@router.post("/reports", response_model=ReportResponse, tags=["reports"])
async def create_report(
    request: ReportCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    session_id: Optional[str] = None
):
    """Create a new report."""
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI workflow not initialized"
        )
    
    try:
        # Get AI results if session provided
        ai_result = None
        if session_id:
            ai_result = workflow.process(
                user_message="Generate report summary",
                session_id=session_id,
                user_id=current_user.id
            )
        
        response = ReportService.create_report(
            db, current_user.id, session_id, ai_result, request
        )
        return response
    except Exception as e:
        logger.error(f"Report creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports", tags=["reports"])
async def list_reports(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    params: PaginationParams = Depends()
):
    """List user's reports."""
    
    reports, total = ReportService.list_user_reports(
        db, current_user.id, params.skip, params.limit
    )
    
    return {
        "total": total,
        "skip": params.skip,
        "limit": params.limit,
        "reports": reports
    }


@router.get("/reports/{report_id}", response_model=ReportResponse, tags=["reports"])
async def get_report(
    report_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific report."""
    
    report = ReportService.get_report(db, current_user.id, report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.post("/reports/{report_id}/share", tags=["reports"])
async def share_report(
    report_id: str,
    share_with: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share report with other users."""
    
    user_ids = share_with.get("user_ids", [])
    is_public = share_with.get("is_public", False)
    
    report = ReportService.share_report(
        db, current_user.id, report_id, user_ids, is_public
    )
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {"message": "Report shared successfully", "report": report}


@router.post("/reports/{report_id}/export", tags=["reports"])
async def export_report(
    report_id: str,
    export_request: ReportExportRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export report in different formats."""
    
    report = ReportService.get_report(db, current_user.id, report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    exported = ReportService.export_report(report, export_request.format)
    
    if export_request.format == "json":
        return JSONResponse(content={"report": exported})
    else:
        return JSONResponse(content={"data": exported})


@router.delete("/reports/{report_id}", tags=["reports"])
async def delete_report(
    report_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a report."""
    
    success = ReportService.delete_report(db, current_user.id, report_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {"message": "Report deleted successfully"}


# ==================== Health & Status Routes ====================

@router.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    """Check API health status."""
    
    from database import health_check
    
    db_healthy = health_check()
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": db_healthy,
        "ai_agents": workflow is not None,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


@router.get("/", tags=["root"])
async def root():
    """API info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "api_prefix": settings.API_PREFIX,
        "status": "online"
    }


# ==================== Text-to-SQL Routes ====================

@router.post("/text-to-sql/query", response_model=TextToSQLResponse, tags=["text-to-sql"])
async def text_to_sql_query(
    request: TextToSQLRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Convert natural language query to SQL and execute it.
    
    Example queries:
    - "Which promotion performed best last month?"
    - "Compare North vs South region sales"
    - "Which products experienced stockouts?"
    - "Show me inventory turnover by product"
    """
    try:
        service = TextToSQLService(db)
        result = service.process_query(request.query, use_llm=request.use_llm)
        
        # Log the query for audit trail
        logger.info(f"User {current_user.id} executed text-to-sql query: {request.query[:100]}")
        
        return result
    
    except Exception as e:
        logger.error(f"Text-to-SQL error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.post("/text-to-sql/validate", tags=["text-to-sql"])
async def validate_sql_query(
    sql_query: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate a SQL query for safety without executing it."""
    try:
        service = TextToSQLService(db)
        is_valid, validation_result = service.validate_query(sql_query)
        
        return {
            "is_valid": is_valid,
            "validation_result": validation_result
        }
    
    except Exception as e:
        logger.error(f"Query validation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Query validation failed")


@router.get("/text-to-sql/schema", response_model=SchemaInfoResponse, tags=["text-to-sql"])
async def get_schema_info(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get database schema information for context."""
    try:
        service = TextToSQLService(db)
        schema = service.get_schema_info()
        
        return {
            "tables": service.schema_extractor.get_available_tables(),
            "schema_details": schema
        }
    
    except Exception as e:
        logger.error(f"Schema retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve schema")


@router.get("/text-to-sql/samples", response_model=SampleQueriesResponse, tags=["text-to-sql"])
async def get_sample_queries(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sample queries for common FMCG analytics questions."""
    try:
        service = TextToSQLService(db)
        samples = service.get_sample_queries()
        
        return {"samples": samples}
    
    except Exception as e:
        logger.error(f"Sample queries error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sample queries")


@router.post("/text-to-sql/explain", response_model=QueryExplanationResponse, tags=["text-to-sql"])
async def explain_query(
    sql_query: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get human-readable explanation of a SQL query."""
    try:
        service = TextToSQLService(db)
        explanation = service.explain_query(sql_query)
        
        return {"explanation": explanation}
    
    except Exception as e:
        logger.error(f"Query explanation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to explain query")


# ==================== Insight Generation Routes ====================

@router.post("/insights/generate", tags=["insights"])
async def generate_insights(
    request: InsightGenerationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive autonomous insights from query results.
    
    Includes:
    - Issue detection and anomalies
    - KPI monitoring and health scoring
    - Business opportunity identification
    - Automated alert generation
    """
    try:
        service = InsightService(db)
        
        # Generate comprehensive insights
        report = service.generate_comprehensive_insights(
            query_results=request.query_results,
            query_metadata=request.query_metadata,
            include_anomalies=request.include_anomalies,
            include_kpis=request.include_kpis,
            include_opportunities=request.include_opportunities,
            include_alerts=request.include_alerts
        )
        
        # Log insight generation
        logger.info(f"User {current_user.id} generated insights from {len(request.query_results)} data points")
        
        return report
    
    except Exception as e:
        logger.error(f"Insight generation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")


@router.post("/insights/action-plan", response_model=ActionPlan, tags=["insights"])
async def generate_action_plan(
    insight_report: Dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate prioritized action plan from insight report.
    
    Prioritizes actions into:
    - Immediate actions (Priority 1)
    - This week actions (Priority 2)
    - This month actions (Priority 3)
    """
    try:
        service = InsightService(db)
        action_plan = service.generate_action_plan(insight_report)
        
        logger.info(f"User {current_user.id} generated action plan")
        
        return action_plan
    
    except Exception as e:
        logger.error(f"Action plan error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate action plan")


@router.post("/insights/anomalies", tags=["insights"])
async def detect_anomalies(
    query_results: List[Dict],
    metric_field: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Detect statistical anomalies in data.
    
    Uses Z-score analysis to identify outliers and unusual patterns.
    """
    try:
        service = InsightService(db)
        anomalies = service.anomaly_detector.detect_anomalies(
            query_results,
            metric_field=metric_field,
            groupby_field="product_name" if "product_name" in (query_results[0] if query_results else {}) else None
        )
        
        return {
            "anomalies": [a.to_dict() for a in anomalies],
            "count": len(anomalies)
        }
    
    except Exception as e:
        logger.error(f"Anomaly detection error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to detect anomalies")


@router.post("/insights/kpi-dashboard", tags=["insights"])
async def get_kpi_dashboard(
    query_results: List[Dict],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate KPI dashboard with health metrics.
    
    Tracks key business KPIs and provides overall health score.
    """
    try:
        service = InsightService(db)
        dashboard = service.kpi_monitor.calculate_kpi_dashboard(query_results)
        
        return dashboard
    
    except Exception as e:
        logger.error(f"KPI dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate KPI dashboard")


@router.post("/insights/opportunities", tags=["insights"])
async def find_opportunities(
    query_results: List[Dict],
    query_metadata: Dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Find business opportunities from query results.
    
    Identifies expansion, optimization, and growth opportunities
    with estimated financial impact.
    """
    try:
        service = InsightService(db)
        opportunities = service.opportunity_finder.find_opportunities(
            query_results,
            query_metadata
        )
        
        return {
            "opportunities": [o.to_dict() for o in opportunities],
            "count": len(opportunities),
            "total_value": sum(o.estimated_impact_value for o in opportunities)
        }
    
    except Exception as e:
        logger.error(f"Opportunity finding error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to find opportunities")


@router.post("/insights/alerts", tags=["insights"])
async def generate_alerts(
    query_results: List[Dict],
    query_metadata: Dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate automated business alerts.
    
    Creates actionable alerts for issues, risks, and critical situations.
    """
    try:
        service = InsightService(db)
        alerts = service.alert_generator.generate_alerts(
            query_results,
            query_metadata
        )
        
        # Separate by level
        critical = [a for a in alerts if a.level == "CRITICAL"]
        warning = [a for a in alerts if a.level == "WARNING"]
        info = [a for a in alerts if a.level == "INFO"]
        
        return {
            "alerts": [a.to_dict() for a in alerts],
            "count": len(alerts),
            "critical": len(critical),
            "warnings": len(warning),
            "info": len(info)
        }
    
    except Exception as e:
        logger.error(f"Alert generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate alerts")


@router.post("/insights/export", tags=["insights"])
async def export_insights_report(
    insight_report: Dict,
    format: str = "json",
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export insight report in various formats (json, text, etc).
    """
    try:
        service = InsightService(db)
        
        if format == "text":
            content = service.export_insights_report(insight_report, format="text")
            return {"report": content, "format": "text"}
        else:
            content = service.export_insights_report(insight_report, format="json")
            return {"report": content, "format": "json"}
    
    except Exception as e:
        logger.error(f"Report export error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export report")


# ==================== Autonomous Report Generation Routes ====================

@router.post("/reports/generate/executive", tags=["report-generation"])
async def generate_executive_report(
    insights_data: Dict,
    period_days: int = 7,
    include_forecast: bool = True,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate autonomous executive summary report from insights.
    
    Includes:
    - Key metrics and KPI dashboard
    - Business findings and risks
    - Identified opportunities
    - Prioritized recommendations
    """
    try:
        from services.report_generation_service import ReportGenerationService
        
        service = ReportGenerationService()
        report = service.generate_executive_report(
            insights_data,
            period_days=period_days,
            include_forecast=include_forecast
        )
        
        logger.info(f"User {current_user.id} generated executive report: {report['report_id']}")
        
        return report
    
    except Exception as e:
        logger.error(f"Executive report generation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/reports/generate/detailed", tags=["report-generation"])
async def generate_detailed_report(
    insights_data: Dict,
    focus_areas: List[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate detailed analysis report with deep metrics and trends.
    """
    try:
        from services.report_generation_service import ReportGenerationService
        
        service = ReportGenerationService()
        report = service.generate_detailed_report(
            insights_data,
            focus_areas=focus_areas
        )
        
        logger.info(f"User {current_user.id} generated detailed report: {report['report_id']}")
        
        return report
    
    except Exception as e:
        logger.error(f"Detailed report error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate detailed report")


@router.post("/reports/generate/opportunities", tags=["report-generation"])
async def generate_opportunity_report(
    opportunities: List[Dict],
    insights_data: Dict = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate opportunities review report with impact analysis.
    """
    try:
        from services.report_generation_service import ReportGenerationService
        
        service = ReportGenerationService()
        report = service.generate_opportunity_report(
            opportunities,
            insights_data=insights_data
        )
        
        logger.info(f"User {current_user.id} generated opportunity report: {report['report_id']}")
        
        return report
    
    except Exception as e:
        logger.error(f"Opportunity report error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate opportunity report")


@router.post("/reports/generate/kpi", tags=["report-generation"])
async def generate_kpi_report(
    kpi_data: Dict,
    include_targets: bool = True,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate KPI scorecard report with health metrics.
    """
    try:
        from services.report_generation_service import ReportGenerationService
        
        service = ReportGenerationService()
        report = service.generate_kpi_report(
            kpi_data,
            include_targets=include_targets
        )
        
        logger.info(f"User {current_user.id} generated KPI report: {report['report_id']}")
        
        return report
    
    except Exception as e:
        logger.error(f"KPI report error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate KPI report")


@router.post("/reports/{report_id}/format", tags=["report-generation"])
async def format_report(
    report_id: str,
    output_format: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Format a generated report to different output formats.
    
    Supported formats: json, html, markdown, text, csv, pdf
    """
    try:
        from services.report_generation_service import ReportGenerationService
        
        service = ReportGenerationService()
        formatted = service.format_report(report_id, output_format)
        
        if not formatted:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "report_id": report_id,
            "format": output_format,
            "content": formatted
        }
    
    except Exception as e:
        logger.error(f"Report formatting error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to format report")


@router.post("/reports/{report_id}/visualizations", tags=["report-generation"])
async def get_visualization_specs(
    report_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get visualization specifications for dashboard integration.
    """
    try:
        from services.report_generation_service import ReportGenerationService
        
        service = ReportGenerationService()
        specs = service.get_visualization_specs(report_id)
        
        if not specs:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return specs
    
    except Exception as e:
        logger.error(f"Visualization specs error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get visualization specs")


@router.post("/reports/schedules/create", tags=["report-generation"])
async def create_report_schedule(
    report_type: str,
    frequency: str,
    recipients: List[str],
    output_formats: List[str] = None,
    enabled: bool = True,
    run_time: str = "08:00",
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a scheduled report generation.
    
    Frequencies: daily, weekly, monthly, quarterly
    Example: Generate executive report daily at 8:00 AM
    """
    try:
        from services.report_generation_service import ReportGenerationService
        
        service = ReportGenerationService()
        schedule = service.create_report_schedule(
            report_type=report_type,
            frequency=frequency,
            recipients=recipients,
            output_formats=output_formats,
            enabled=enabled,
            run_time=run_time
        )
        
        logger.info(f"User {current_user.id} created report schedule: {schedule['schedule_id']}")
        
        return schedule
    
    except Exception as e:
        logger.error(f"Schedule creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create schedule")


@router.get("/reports/schedules/all", tags=["report-generation"])
async def get_all_schedules(
    enabled_only: bool = False,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all report schedules.
    """
    try:
        from services.report_generation_service import ReportGenerationService
        
        service = ReportGenerationService()
        schedules = service.get_all_schedules(enabled_only=enabled_only)
        
        return {
            "total": len(schedules),
            "schedules": schedules
        }
    
    except Exception as e:
        logger.error(f"Schedule retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve schedules")


@router.get("/reports/schedules/due", tags=["report-generation"])
async def get_due_schedules(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get schedules due to run.
    """
    try:
        from services.report_generation_service import ReportGenerationService
        
        service = ReportGenerationService()
        due_schedules = service.get_due_schedules()
        
        return {
            "due_count": len(due_schedules),
            "schedules": due_schedules
        }
    
    except Exception as e:
        logger.error(f"Due schedules error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve due schedules")


@router.post("/reports/{report_id}/distribute", tags=["report-generation"])
async def distribute_report(
    report_id: str,
    channels: List[str],
    recipients: Dict[str, List[str]] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Distribute a report to multiple channels.
    
    Channels: email, webhook, file_storage, dashboard, slack, teams
    """
    try:
        from services.report_generation_service import ReportGenerationService
        
        service = ReportGenerationService()
        
        # Get report data first
        report_data = service.generator.get_report_by_id(report_id)
        if not report_data:
            raise HTTPException(status_code=404, detail="Report not found")
        
        distributions = service.distribute_report(
            report_id,
            report_data.to_dict(),
            channels=channels,
            recipients=recipients
        )
        
        logger.info(f"User {current_user.id} distributed report {report_id} to {len(channels)} channels")
        
        return {
            "distributions": distributions,
            "total": len(distributions),
            "success_count": len([d for d in distributions if d['status'] == 'sent'])
        }
    
    except Exception as e:
        logger.error(f"Report distribution error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to distribute report")


@router.get("/reports/statistics", tags=["report-generation"])
async def get_report_statistics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get report generation and distribution statistics.
    """
    try:
        from services.report_generation_service import ReportGenerationService
        
        service = ReportGenerationService()
        
        return {
            "scheduler": service.get_scheduler_statistics(),
            "distributor": service.get_distribution_statistics(),
            "report_history": service.get_report_history(limit=20),
            "distribution_history": service.get_distribution_history(limit=50)
        }
    
    except Exception as e:
        logger.error(f"Statistics retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")
