"""
Report Agent - generates executive summaries and persists reports.
"""
import json
import uuid
from datetime import datetime
from .schema import AgentState


class ReportAgent:
    """
    Assembles insights, visuals, and KPIs into executive reports.
    """
    
    def __init__(self, reports_storage: dict = None):
        """
        Args:
            reports_storage: Optional in-memory dict to store reports
        """
        self.reports_storage = reports_storage or {}
    
    def process(self, state: AgentState) -> AgentState:
        """Generate and persist a report."""
        try:
            if not state.insights and not state.analytics_output:
                state.error_messages.append("Insufficient data to generate report.")
                return state
            
            # Build report
            report = self._build_report(state)
            
            # Assign report ID and store
            report_id = str(uuid.uuid4())
            report["report_id"] = report_id
            report["created_at"] = datetime.utcnow().isoformat()
            
            self.reports_storage[report_id] = report
            
            state.report_id = report_id
            state.response_data["report_id"] = report_id
            state.response_data["report_summary"] = report.get("summary", "")
            state.updated_at = datetime.utcnow()
            
            return state
        
        except Exception as e:
            state.error_messages.append(f"Report Generation Error: {str(e)}")
            return state
    
    def _build_report(self, state: AgentState) -> dict:
        """Assemble report from state components."""
        report = {
            "title": self._generate_title(state),
            "summary": self._generate_summary(state),
            "executive_summary": self._generate_executive_summary(state),
            "kpis": [
                {
                    "name": kpi.metric_name,
                    "value": kpi.value,
                    "unit": kpi.unit,
                    "dimensions": kpi.dimensions
                }
                for kpi in (state.analytics_output.kpis if state.analytics_output else [])
            ],
            "insights": {
                "summary": state.insights.summary if state.insights else "",
                "narrative": state.insights.narrative if state.insights else "",
                "anomalies": state.insights.anomalies if state.insights else [],
                "recommendations": state.insights.recommendations if state.insights else []
            },
            "visualizations": [
                {
                    "chart_type": viz.chart_type,
                    "title": viz.title,
                    "data_points": len(viz.data)
                }
                for viz in state.visualizations
            ],
            "metadata": {
                "user_id": state.user_id,
                "user_role": state.user_role,
                "intent": state.structured_intent.intent.value if state.structured_intent else "unknown",
                "session_id": state.session_id,
                "turn_id": state.turn_id
            }
        }
        
        return report
    
    def _generate_title(self, state: AgentState) -> str:
        """Generate report title."""
        if state.structured_intent:
            intent_title = state.structured_intent.intent.value.replace("_", " ").title()
            return f"{intent_title} Report"
        return "FMCG Analytics Report"
    
    def _generate_summary(self, state: AgentState) -> str:
        """Generate concise summary."""
        summary_lines = []
        
        if state.structured_intent and state.structured_intent.time_range:
            tr = state.structured_intent.time_range
            summary_lines.append(f"Period: {tr.get('start')} to {tr.get('end')}")
        
        if state.analytics_output and state.analytics_output.kpis:
            kpi_count = len(state.analytics_output.kpis)
            summary_lines.append(f"Metrics analyzed: {kpi_count}")
        
        if state.insights:
            summary_lines.append(f"Confidence: {state.insights.confidence:.0%}")
        
        return "\n".join(summary_lines) if summary_lines else "Report generated."
    
    def _generate_executive_summary(self, state: AgentState) -> str:
        """Generate executive-level summary."""
        sections = []
        
        # Headline
        if state.insights:
            sections.append("## Executive Summary\n")
            sections.append(state.insights.narrative)
        
        # Recommendations
        if state.insights and state.insights.recommendations:
            sections.append("\n## Recommended Actions\n")
            for rec in state.insights.recommendations[:3]:
                sections.append(f"- {rec}")
        
        # Key metrics
        if state.analytics_output and state.analytics_output.kpis:
            sections.append("\n## Key Metrics\n")
            for kpi in state.analytics_output.kpis[:5]:
                sections.append(f"**{kpi.metric_name}:** {kpi.value:,.0f} {kpi.unit}")
        
        return "\n".join(sections) if sections else "No executive summary available."
    
    def get_report(self, report_id: str) -> dict:
        """Retrieve stored report."""
        return self.reports_storage.get(report_id)
    
    def list_reports(self) -> list:
        """List all stored reports."""
        return list(self.reports_storage.values())
