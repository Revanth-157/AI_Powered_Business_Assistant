"""
Insight Generation Service - Orchestrates autonomous insight discovery.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from insight_generation import (
    InsightDetector,
    AnomalyDetector,
    KPIMonitor,
    OpportunityFinder,
    AlertGenerator
)

logger = logging.getLogger(__name__)


class InsightService:
    """Main service for generating autonomous insights."""

    def __init__(self, db_session: Session):
        """
        Initialize insight service.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

        # Initialize all insight components
        self.insight_detector = InsightDetector()
        self.anomaly_detector = AnomalyDetector(z_score_threshold=2.5)
        self.kpi_monitor = KPIMonitor()
        self.opportunity_finder = OpportunityFinder()
        self.alert_generator = AlertGenerator()

    def generate_comprehensive_insights(
        self,
        query_results: List[Dict],
        query_metadata: Dict,
        include_anomalies: bool = True,
        include_kpis: bool = True,
        include_opportunities: bool = True,
        include_alerts: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights from query results.

        Args:
            query_results: Query result data
            query_metadata: Query metadata (intent, tables, etc.)
            include_anomalies: Include anomaly detection
            include_kpis: Include KPI monitoring
            include_opportunities: Include opportunity finding
            include_alerts: Include alert generation

        Returns:
            Comprehensive insight report
        """
        if not query_results:
            return {
                "error": "No data provided",
                "timestamp": datetime.utcnow().isoformat()
            }

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "query_intent": query_metadata.get("intent", "UNKNOWN"),
            "data_points": len(query_results),
            "insights": {},
            "summary": {}
        }

        try:
            # 1. Detect insights
            logger.info("Generating insights...")
            insights = self.insight_detector.detect_insights(query_results, query_metadata)
            report["insights"]["findings"] = [i.to_dict() for i in insights]
            report["summary"]["insight_count"] = len(insights)
            report["summary"]["critical_insights"] = len([i for i in insights if i.severity == "CRITICAL"])

            # 2. Detect anomalies
            if include_anomalies:
                logger.info("Detecting anomalies...")
                # Try to detect anomalies on numeric fields
                anomalies = []
                for field in ["total_sales", "total_units", "avg_discount", "total_margin"]:
                    if query_results and field in query_results[0]:
                        detected = self.anomaly_detector.detect_anomalies(
                            query_results,
                            metric_field=field,
                            groupby_field="product_name"
                        )
                        anomalies.extend(detected)

                report["insights"]["anomalies"] = [a.to_dict() for a in anomalies]
                report["summary"]["anomaly_count"] = len(anomalies)

            # 3. Monitor KPIs
            if include_kpis:
                logger.info("Monitoring KPIs...")
                kpi_dashboard = self.kpi_monitor.calculate_kpi_dashboard(query_results)
                report["insights"]["kpi_dashboard"] = kpi_dashboard
                report["summary"]["health_score"] = kpi_dashboard.get("health_score", 0)
                report["summary"]["at_risk_kpis"] = kpi_dashboard.get("summary", {}).get("at_risk", 0)

            # 4. Find opportunities
            if include_opportunities:
                logger.info("Finding opportunities...")
                opportunities = self.opportunity_finder.find_opportunities(
                    query_results,
                    query_metadata
                )
                report["insights"]["opportunities"] = [o.to_dict() for o in opportunities]
                report["summary"]["opportunity_count"] = len(opportunities)
                total_opportunity_value = sum(o.estimated_impact_value for o in opportunities)
                report["summary"]["total_opportunity_value"] = total_opportunity_value

            # 5. Generate alerts
            if include_alerts:
                logger.info("Generating alerts...")
                alerts = self.alert_generator.generate_alerts(query_results, query_metadata)
                report["insights"]["alerts"] = [a.to_dict() for a in alerts]
                report["summary"]["alert_count"] = len(alerts)
                report["summary"]["critical_alerts"] = len([a for a in alerts if a.level == "CRITICAL"])

        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}", exc_info=True)
            report["error"] = str(e)

        # Add executive summary
        report["executive_summary"] = self._generate_executive_summary(report)

        return report

    def _generate_executive_summary(self, report: Dict) -> Dict:
        """Generate executive summary of insights."""
        summary = report.get("summary", {})

        sections = []

        # Critical findings
        critical_insights = len([i for i in report.get("insights", {}).get("findings", [])
                                if i.get("severity") == "CRITICAL"])
        if critical_insights > 0:
            sections.append(f"🔴 CRITICAL: {critical_insights} critical issues identified")

        # Health score
        health = summary.get("health_score", 0)
        if health < 50:
            sections.append(f"⚠️ HEALTH: Business health score {health}/100 - immediate action needed")
        elif health < 75:
            sections.append(f"⚠️ HEALTH: Business health score {health}/100 - monitor closely")
        else:
            sections.append(f"✅ HEALTH: Business health score {health}/100 - performing well")

        # Opportunities
        opp_value = summary.get("total_opportunity_value", 0)
        opp_count = summary.get("opportunity_count", 0)
        if opp_count > 0:
            sections.append(f"💡 OPPORTUNITIES: {opp_count} opportunities identified, ${opp_value:,.0f} potential value")

        # Alerts
        critical_alerts = summary.get("critical_alerts", 0)
        if critical_alerts > 0:
            sections.append(f"🚨 ALERTS: {critical_alerts} critical alerts require attention")

        return {
            "status": "healthy" if health > 75 else "at_risk" if health > 50 else "critical",
            "key_points": sections,
            "generated_at": datetime.utcnow().isoformat()
        }

    def get_insight_by_type(self, report: Dict, insight_type: str) -> List[Dict]:
        """Extract specific insight type from report."""
        insights = report.get("insights", {})
        if insight_type == "findings":
            return insights.get("findings", [])
        elif insight_type == "anomalies":
            return insights.get("anomalies", [])
        elif insight_type == "alerts":
            return insights.get("alerts", [])
        elif insight_type == "opportunities":
            return insights.get("opportunities", [])
        elif insight_type == "kpis":
            kpi_dash = insights.get("kpi_dashboard", {})
            return kpi_dash.get("kpis", {})
        return []

    def filter_insights_by_severity(self, insights: List[Dict], severity: str) -> List[Dict]:
        """Filter insights by severity level."""
        return [i for i in insights if i.get("severity") == severity or i.get("level") == severity]

    def generate_action_plan(self, report: Dict) -> Dict:
        """Generate prioritized action plan from insights."""
        action_plan = {
            "priority_1_immediate": [],
            "priority_2_this_week": [],
            "priority_3_this_month": [],
            "generated_at": datetime.utcnow().isoformat()
        }

        # Add critical alerts
        critical_alerts = [a for a in report.get("insights", {}).get("alerts", [])
                          if a.get("level") == "CRITICAL"]
        for alert in critical_alerts:
            action_plan["priority_1_immediate"].append({
                "action": alert.get("title"),
                "type": "URGENT",
                "items": alert.get("actions", [])
            })

        # Add critical insights
        critical_findings = [f for f in report.get("insights", {}).get("findings", [])
                            if f.get("severity") == "CRITICAL"]
        for finding in critical_findings:
            action_plan["priority_1_immediate"].append({
                "action": finding.get("title"),
                "type": "INVESTIGATION",
                "items": [finding.get("recommendation", "")]
            })

        # Add high-priority opportunities
        high_opp = [o for o in report.get("insights", {}).get("opportunities", [])
                   if o.get("priority", 0) >= 8]
        for opp in high_opp[:3]:
            action_plan["priority_2_this_week"].append({
                "action": opp.get("title"),
                "type": "OPPORTUNITY",
                "items": opp.get("actions", []),
                "value": f"${opp.get('estimated_value', 0):,.0f}"
            })

        return action_plan

    def export_insights_report(self, report: Dict, format: str = "json") -> str:
        """Export insight report in various formats."""
        if format == "json":
            import json
            return json.dumps(report, indent=2, default=str)

        elif format == "text":
            text = "=" * 80 + "\n"
            text += "AUTONOMOUS INSIGHT REPORT\n"
            text += f"Generated: {report.get('timestamp')}\n"
            text += f"Query Intent: {report.get('query_intent')}\n"
            text += f"Data Points: {report.get('data_points')}\n"
            text += "=" * 80 + "\n\n"

            summary = report.get("executive_summary", {})
            text += "EXECUTIVE SUMMARY\n"
            text += f"Status: {summary.get('status').upper()}\n"
            for point in summary.get("key_points", []):
                text += f"  • {point}\n"
            text += "\n"

            # Add findings
            findings = report.get("insights", {}).get("findings", [])
            if findings:
                text += f"KEY FINDINGS ({len(findings)})\n"
                for finding in findings[:5]:
                    text += f"  • {finding.get('title')}\n"
                    text += f"    {finding.get('description')}\n"

            return text

        return json.dumps(report, indent=2, default=str)
