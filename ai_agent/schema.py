"""
Shared types and state definitions for the multi-agent FMCG BI system.
"""
from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class Intent(str, Enum):
    PROMO_PERFORMANCE = "promo_performance"
    INVENTORY_MOVEMENT = "inventory_movement"
    REGIONAL_SALES = "regional_sales"
    CAMPAIGN_IMPACT = "campaign_impact"
    KPI_DASHBOARD = "kpi_dashboard"
    UNKNOWN = "unknown"


@dataclass
class Entity:
    type: str  # e.g., "time_range", "region", "product_category"
    value: str
    confidence: float


@dataclass
class StructuredIntent:
    intent: Intent
    entities: List[Entity]
    time_range: Optional[Dict[str, str]] = None  # {"start": "2025-01-01", "end": "2025-12-31"}
    granularity: str = "week"  # "day", "week", "month"
    filters: Dict[str, Any] = field(default_factory=dict)
    clarification_needed: bool = False
    clarification_question: Optional[str] = None
    confidence: float = 0.8


@dataclass
class SQLQuery:
    text: str
    params: Dict[str, Any] = field(default_factory=dict)
    estimated_cost: float = 0.0
    safe: bool = True
    issues: List[str] = field(default_factory=list)


@dataclass
class KPIResult:
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    dimensions: Dict[str, str] = field(default_factory=dict)
    provenance: str = ""  # query or calculation method


@dataclass
class AnalyticsOutput:
    kpis: List[KPIResult]
    time_series: Optional[List[Dict[str, Any]]] = None
    aggregations: Optional[List[Dict[str, Any]]] = None
    raw_data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


@dataclass
class Insight:
    summary: str  # bullet points
    narrative: str  # longer explanation
    confidence: float
    anomalies: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class VisualizationSpec:
    chart_type: str  # "line", "bar", "pie", "heatmap"
    title: str
    data: List[Dict[str, Any]]
    axes: Dict[str, str]  # {"x": "week_start", "y": "sales_value"}
    annotations: List[str] = field(default_factory=list)
    vega_spec: Optional[Dict[str, Any]] = None


@dataclass
class AgentState:
    """Main state object passed through the LangGraph workflow."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    turn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    user_role: str = "analyst"  # "analyst", "manager", "executive"
    accessible_regions: List[str] = field(default_factory=list)
    
    # Input
    user_message: str = ""
    
    # Processing chain
    structured_intent: Optional[StructuredIntent] = None
    sql_query: Optional[SQLQuery] = None
    analytics_output: Optional[AnalyticsOutput] = None
    insights: Optional[Insight] = None
    visualizations: List[VisualizationSpec] = field(default_factory=list)
    report_id: Optional[str] = None
    
    # Response assembly
    response_text: str = ""
    response_data: Dict[str, Any] = field(default_factory=dict)
    
    # Error handling
    error_messages: List[str] = field(default_factory=list)
    requires_clarification: bool = False
    clarification_question: Optional[str] = None
    
    # Conversation memory
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    context_from_history: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    model_used: str = "gpt-4"
    

@dataclass
class SessionMemory:
    """Ephemeral per-session memory."""
    session_id: str
    user_id: Optional[str]
    turns: List[Dict[str, Any]] = field(default_factory=list)
    resolved_entities: Dict[str, Any] = field(default_factory=dict)
    current_filters: Dict[str, Any] = field(default_factory=dict)
    cache: Dict[str, Any] = field(default_factory=dict)
    ttl_seconds: int = 3600


@dataclass
class ConversationTurn:
    """Single turn in conversation."""
    turn_id: str
    session_id: str
    user_message: str
    intent: Optional[Intent] = None
    sql_query: Optional[str] = None
    result_summary: str = ""
    kpis: Dict[str, float] = field(default_factory=dict)
    generated_report_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
