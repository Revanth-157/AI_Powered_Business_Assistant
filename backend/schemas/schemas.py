"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== User Schemas ====================

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    id: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== Authentication Schemas ====================

class TokenRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ==================== Session Schemas ====================

class SessionCreate(BaseModel):
    title: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None


class SessionUpdate(BaseModel):
    title: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SessionResponse(BaseModel):
    id: str
    user_id: str
    title: Optional[str]
    is_active: bool
    context_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Conversation Schemas ====================

class EntityExtraction(BaseModel):
    type: str  # time_period, region, category, store_format
    value: str
    confidence: float


class ConversationRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    intent: Optional[str] = None


class KPIResult(BaseModel):
    metric_name: str
    value: Any
    unit: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = None


class InsightResult(BaseModel):
    summary: str
    narrative: str
    anomalies: List[str] = []
    recommendations: List[str] = []
    confidence: float


class VisualizationResult(BaseModel):
    chart_type: str  # line, bar, kpi_cards
    title: str
    data: List[Dict[str, Any]]
    vega_spec: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    id: str
    session_id: str
    user_message: str
    assistant_response: str
    
    # Processing results
    intent: Optional[str] = None
    entities: Optional[List[EntityExtraction]] = None
    kpis: Optional[List[KPIResult]] = None
    insights: Optional[InsightResult] = None
    visualizations: Optional[List[VisualizationResult]] = None
    
    # Metadata
    confidence_score: Optional[float] = None
    processing_time_ms: int
    error_message: Optional[str] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Analytics Schemas ====================

class AnalyticsRequest(BaseModel):
    query: str
    time_range: Optional[Dict[str, str]] = None  # {"start": "2026-01-01", "end": "2026-06-09"}
    filters: Optional[Dict[str, Any]] = None  # {region: "North", category: "Carbonated"}
    granularity: Optional[str] = "week"  # day, week, month


class AnalyticsResponse(BaseModel):
    query: str
    kpis: List[KPIResult]
    time_series: Optional[List[Dict[str, Any]]] = None
    aggregations: Optional[List[Dict[str, Any]]] = None
    raw_data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


# ==================== Report Schemas ====================

class ReportCreate(BaseModel):
    title: str = Field(..., max_length=255)
    intent: Optional[str] = None
    report_type: str = "standard"  # standard, custom, scheduled


class ReportUpdate(BaseModel):
    title: Optional[str] = None
    is_shared: Optional[bool] = None
    shared_with: Optional[List[str]] = None


class ReportResponse(BaseModel):
    id: str
    user_id: str
    title: str
    summary: Optional[str]
    executive_summary: Optional[str]
    
    kpis: Optional[List[KPIResult]] = None
    insights: Optional[InsightResult] = None
    visualizations: Optional[List[VisualizationResult]] = None
    
    report_type: str
    is_shared: bool
    is_public: bool
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    id: str
    title: str
    report_type: str
    created_at: datetime
    updated_at: datetime
    is_shared: bool


class ReportExportRequest(BaseModel):
    format: str = "pdf"  # pdf, excel, json, csv


# ==================== API Key Schemas ====================

class ApiKeyCreate(BaseModel):
    name: str = Field(..., max_length=255)
    permissions: List[str] = []  # ["chat", "analytics", "reports"]
    expires_in_days: Optional[int] = None


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key: str  # Only shown on creation
    permissions: List[str]
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== Health & Status Schemas ====================

class HealthResponse(BaseModel):
    status: str  # healthy, degraded, unhealthy
    timestamp: datetime
    database: bool
    ai_agents: bool
    llm: Optional[bool] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime


class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: str = "desc"  # asc, desc


class PaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[Any]


# ==================== Text-to-SQL Schemas ====================

class TextToSQLRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query")
    use_llm: bool = False
    context: Optional[Dict[str, Any]] = None


class QueryValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    estimated_risk: str = "low"  # low, medium, high
    estimated_time_ms: int = 0
    estimated_rows: int = 0


class TextToSQLResponse(BaseModel):
    original_query: str
    generated_sql: str
    is_valid: bool
    validation_result: Optional[QueryValidationResult] = None
    results: List[Dict[str, Any]] = []
    interpretation: Optional[Dict[str, Any]] = None
    sql_metadata: Optional[Dict[str, Any]] = None
    execution_time_ms: int = 0
    errors: List[str] = []


class SchemaInfoResponse(BaseModel):
    tables: List[str]
    schema_details: Optional[Dict[str, Any]] = None


class SampleQuery(BaseModel):
    question: str
    intent: str
    description: str


class SampleQueriesResponse(BaseModel):
    samples: List[SampleQuery]


class QueryExplanationResponse(BaseModel):
    explanation: str
    components: Optional[Dict[str, str]] = None


# ==================== Insight Generation Schemas ====================

class InsightFinding(BaseModel):
    type: str  # "ISSUE", "OPPORTUNITY", "TREND", "ANOMALY"
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    title: str
    description: str
    metric: str
    current_value: float
    baseline_value: Optional[float] = None
    change_percent: Optional[float] = None
    recommendation: str = ""
    confidence: float = 0.8
    affected_entities: List[str] = []
    generated_at: datetime = None


class AnomalyAlert(BaseModel):
    metric_name: str
    entity: str
    expected_value: float
    actual_value: float
    z_score: float
    anomaly_type: str  # "spike", "drop", "outlier"
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    message: str
    timestamp: datetime = None


class KPIMetric(BaseModel):
    name: str
    display_name: str
    current_value: float
    target_value: float
    previous_value: Optional[float] = None
    unit: str = ""
    status: str  # "ON_TARGET", "AT_RISK", "BELOW_TARGET", "ABOVE_TARGET"
    variance_pct: float = 0.0
    trend: str  # "UP", "DOWN", "STABLE"


class KPIDashboard(BaseModel):
    timestamp: datetime
    kpis: Dict[str, Any]
    summary: Dict[str, int]  # on_target, at_risk, below_target counts
    health_score: int  # 0-100
    recommendations: List[str] = []


class Opportunity(BaseModel):
    title: str
    description: str
    type: str  # "EXPANSION", "OPTIMIZATION", "NEW_MARKET", "COST_SAVING", "REVENUE_GROWTH"
    impact: str  # "LOW", "MEDIUM", "HIGH"
    effort: str  # "LOW", "MEDIUM", "HIGH"
    estimated_value: float
    entities: List[str]
    actions: List[str]
    priority: int  # 1-10


class Alert(BaseModel):
    title: str
    message: str
    type: str  # "PERFORMANCE", "OPERATIONAL", "RISK", "OPPORTUNITY"
    level: str  # "INFO", "WARNING", "ALERT", "CRITICAL"
    entity: str
    metric_value: float
    threshold: float
    action_required: bool
    actions: List[str]
    created: datetime = None


class InsightReport(BaseModel):
    timestamp: datetime
    query_intent: str
    data_points: int
    insights: Dict[str, Any]
    summary: Dict[str, Any]
    executive_summary: Dict[str, Any]


class InsightGenerationRequest(BaseModel):
    query_results: List[Dict[str, Any]]
    query_metadata: Dict[str, Any]
    include_anomalies: bool = True
    include_kpis: bool = True
    include_opportunities: bool = True
    include_alerts: bool = True


class ActionPlan(BaseModel):
    priority_1_immediate: List[Dict[str, Any]] = []
    priority_2_this_week: List[Dict[str, Any]] = []
    priority_3_this_month: List[Dict[str, Any]] = []
    generated_at: datetime = None
