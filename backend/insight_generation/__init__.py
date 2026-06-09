"""
Insight Generation Engine for autonomous discovery of business insights, opportunities, and alerts.
"""

from .insight_detector import InsightDetector, InsightFinding
from .anomaly_detector import AnomalyDetector, AnomalyAlert
from .kpi_monitor import KPIMonitor, KPI, KPIStatus
from .opportunity_finder import OpportunityFinder, Opportunity
from .alert_generator import AlertGenerator, Alert, AlertLevel

__all__ = [
    "InsightDetector",
    "InsightFinding",
    "AnomalyDetector",
    "AnomalyAlert",
    "KPIMonitor",
    "KPI",
    "KPIStatus",
    "OpportunityFinder",
    "Opportunity",
    "AlertGenerator",
    "Alert",
    "AlertLevel"
]
