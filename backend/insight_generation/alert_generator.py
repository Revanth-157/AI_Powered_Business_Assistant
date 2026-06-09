"""
Alert generation for automated business alerts and notifications.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ALERT = "ALERT"
    CRITICAL = "CRITICAL"


@dataclass
class Alert:
    """Actionable business alert."""
    title: str
    message: str
    alert_type: str  # "PERFORMANCE", "OPERATIONAL", "RISK", "OPPORTUNITY"
    level: str  # INFO, WARNING, ALERT, CRITICAL
    entity: str  # Product, region, store, metric
    metric_value: float
    threshold: float
    action_required: bool
    recommended_actions: List[str]
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "title": self.title,
            "message": self.message,
            "type": self.alert_type,
            "level": self.level,
            "entity": self.entity,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "action_required": self.action_required,
            "actions": self.recommended_actions,
            "created": self.created_at.isoformat()
        }


class AlertGenerator:
    """Generate automated business alerts."""

    def __init__(self):
        """Initialize alert generator."""
        self.alert_thresholds = {
            "revenue_miss_pct": -20,  # Alert if revenue down 20%
            "margin_miss_pct": -15,   # Alert if margin down 15%
            "stockout_count": 3,      # Alert if 3+ SKUs in stockout
            "inventory_days": 60,     # Alert if inventory > 60 days
            "discount_level": 35,     # Alert if discount > 35%
            "sales_drop_daily": -30   # Alert if daily sales down 30%
        }
        self.active_alerts = {}

    def generate_alerts(
        self,
        query_results: List[Dict],
        metadata: Dict,
        thresholds: Optional[Dict] = None
    ) -> List[Alert]:
        """
        Generate alerts from query results.

        Args:
            query_results: Query result data
            metadata: Query metadata
            thresholds: Optional custom thresholds

        Returns:
            List of generated alerts
        """
        if thresholds:
            self.alert_thresholds.update(thresholds)

        alerts = []

        if not query_results:
            return alerts

        intent = metadata.get("intent", "")

        # Route to appropriate alert generator
        if intent == "PROMO_PERFORMANCE":
            alerts.extend(self._generate_promo_alerts(query_results))
        elif intent == "REGIONAL_SALES":
            alerts.extend(self._generate_regional_alerts(query_results))
        elif intent == "STOCKOUT_ANALYSIS":
            alerts.extend(self._generate_stockout_alerts(query_results))
        elif intent == "PRODUCT_PERFORMANCE":
            alerts.extend(self._generate_product_alerts(query_results))
        elif intent == "INVENTORY_ANALYSIS":
            alerts.extend(self._generate_inventory_alerts(query_results))
        else:
            alerts.extend(self._generate_operational_alerts(query_results))

        # Track active alerts
        for alert in alerts:
            key = f"{alert.entity}_{alert.alert_type}"
            self.active_alerts[key] = alert

        return sorted(alerts, key=lambda x: self._severity_score(x.level), reverse=True)

    def _severity_score(self, level: str) -> int:
        """Convert alert level to numeric score for sorting."""
        scores = {
            AlertLevel.CRITICAL.value: 4,
            AlertLevel.ALERT.value: 3,
            AlertLevel.WARNING.value: 2,
            AlertLevel.INFO.value: 1
        }
        return scores.get(level, 0)

    def _generate_promo_alerts(self, data: List[Dict]) -> List[Alert]:
        """Generate promotion-related alerts."""
        alerts = []

        for item in data:
            product = item.get("product_name", "Unknown")
            sales = item.get("total_sales", 0)
            discount = item.get("avg_discount", 0)
            units = item.get("total_units", 0)

            # Alert: Excessive discount without sales lift
            if discount > self.alert_thresholds["discount_level"]:
                alerts.append(
                    Alert(
                        title="Excessive Promotion Discount",
                        message=f"{product} promotion using {discount:.1f}% discount - above acceptable threshold",
                        alert_type="OPERATIONAL",
                        level=AlertLevel.ALERT.value,
                        entity=product,
                        metric_value=discount,
                        threshold=self.alert_thresholds["discount_level"],
                        action_required=True,
                        recommended_actions=[
                            f"Review {product} promotion strategy",
                            "Consider price increase or alternative incentives",
                            "Evaluate competitor positioning",
                            "Decide: scale, adjust, or pause promotion"
                        ]
                    )
                )

            # Alert: Low performing promotion
            if units < 1000 and discount > 20:
                alerts.append(
                    Alert(
                        title="Underperforming Promotion",
                        message=f"{product} promotion not driving sufficient volume with {discount:.1f}% discount",
                        alert_type="PERFORMANCE",
                        level=AlertLevel.WARNING.value,
                        entity=product,
                        metric_value=units,
                        threshold=1000,
                        action_required=True,
                        recommended_actions=[
                            "Analyze target consumer response",
                            "Check in-store execution and visibility",
                            "Consider timing or shelf placement",
                            "Evaluate media support effectiveness"
                        ]
                    )
                )

        return alerts

    def _generate_regional_alerts(self, data: List[Dict]) -> List[Alert]:
        """Generate regional performance alerts."""
        alerts = []

        if len(data) > 1:
            sorted_regions = sorted(data, key=lambda x: x.get("total_sales", 0), reverse=True)
            best_sales = sorted_regions[0].get("total_sales", 0)

            for region in sorted_regions[1:]:
                region_name = region.get("region", "Unknown")
                sales = region.get("total_sales", 0)

                if best_sales > 0:
                    perf_pct = (sales / best_sales) * 100

                    if perf_pct < 50:
                        alerts.append(
                            Alert(
                                title="Severe Regional Underperformance",
                                message=f"{region_name} at {perf_pct:.0f}% of best performer - significant gap",
                                alert_type="PERFORMANCE",
                                level=AlertLevel.CRITICAL.value,
                                entity=region_name,
                                metric_value=perf_pct,
                                threshold=75,
                                action_required=True,
                                recommended_actions=[
                                    f"Audit {region_name} operations immediately",
                                    f"Compare with {sorted_regions[0].get('region')} best practices",
                                    "Assess team capability and resources",
                                    f"Develop urgent action plan for {region_name}",
                                    "Consider leadership changes if needed"
                                ]
                            )
                        )

        return alerts

    def _generate_stockout_alerts(self, data: List[Dict]) -> List[Alert]:
        """Generate stockout alerts."""
        alerts = []

        if len(data) >= self.alert_thresholds["stockout_count"]:
            alerts.append(
                Alert(
                    title="Critical Stockout Situation",
                    message=f"{len(data)} SKUs experiencing stockouts - revenue at risk",
                    alert_type="OPERATIONAL",
                    level=AlertLevel.CRITICAL.value,
                    entity="Supply Chain",
                    metric_value=len(data),
                    threshold=self.alert_thresholds["stockout_count"],
                    action_required=True,
                    recommended_actions=[
                        "Activate emergency replenishment protocols",
                        "Expedite shipments from alternate warehouses",
                        "Contact supplier for rush orders",
                        "Communicate to customers about delays",
                        "Track daily stockout recovery"
                    ]
                )
            )

            # Calculate lost revenue
            total_lost = sum(item.get("lost_sales", 0) for item in data)
            if total_lost > 50000:
                alerts.append(
                    Alert(
                        title="Significant Revenue at Risk",
                        message=f"Estimated ${total_lost:,.0f} revenue loss from stockouts",
                        alert_type="RISK",
                        level=AlertLevel.ALERT.value,
                        entity="Revenue",
                        metric_value=total_lost,
                        threshold=50000,
                        action_required=True,
                        recommended_actions=[
                            "Prioritize restocking high-revenue SKUs",
                            "Implement temporary substitutions where possible",
                            "Create make-good offers for lost sales",
                            "Review demand forecasting accuracy"
                        ]
                    )
                )

        return alerts

    def _generate_product_alerts(self, data: List[Dict]) -> List[Alert]:
        """Generate product performance alerts."""
        alerts = []

        for item in data:
            product = item.get("product_name", "Unknown")
            sales = item.get("total_sales", 0)
            margin = item.get("total_margin", 0)

            # Alert: Declining margin despite sales
            margin_pct = (margin / sales * 100) if sales > 0 else 0
            if margin_pct < 15:  # Below 15% threshold
                alerts.append(
                    Alert(
                        title="Low Margin Product",
                        message=f"{product} margin at {margin_pct:.1f}% - below healthy level",
                        alert_type="PERFORMANCE",
                        level=AlertLevel.WARNING.value,
                        entity=product,
                        metric_value=margin_pct,
                        threshold=15,
                        action_required=True,
                        recommended_actions=[
                            f"Review pricing of {product}",
                            f"Analyze {product} cost structure",
                            "Consider reducing promotional activity",
                            "Evaluate supply chain efficiency"
                        ]
                    )
                )

        return alerts

    def _generate_inventory_alerts(self, data: List[Dict]) -> List[Alert]:
        """Generate inventory alerts."""
        alerts = []

        for item in data:
            product = item.get("product_name", "Unknown")
            days_inv = item.get("days_inventory", 0)

            # Alert: Excess inventory
            if days_inv > self.alert_thresholds["inventory_days"]:
                alerts.append(
                    Alert(
                        title="Excess Inventory Alert",
                        message=f"{product} at {days_inv:.0f} days - {days_inv-30:.0f} days above target",
                        alert_type="OPERATIONAL",
                        level=AlertLevel.ALERT.value,
                        entity=product,
                        metric_value=days_inv,
                        threshold=self.alert_thresholds["inventory_days"],
                        action_required=True,
                        recommended_actions=[
                            f"Execute clearance promotion for {product}",
                            f"Extend payment terms to reduce cash impact",
                            "Reduce incoming orders until stock levels normalize",
                            "Consider discounting to distributors/retailers"
                        ]
                    )
                )

            # Alert: Low inventory
            if days_inv < 5:
                alerts.append(
                    Alert(
                        title="Low Inventory Alert",
                        message=f"{product} at critical {days_inv:.0f} days - stockout risk",
                        alert_type="RISK",
                        level=AlertLevel.CRITICAL.value,
                        entity=product,
                        metric_value=days_inv,
                        threshold=5,
                        action_required=True,
                        recommended_actions=[
                            f"Emergency reorder of {product} immediately",
                            "Prioritize shipment from all sources",
                            "Prepare for potential stockout",
                            "Alert sales team to manage customer expectations"
                        ]
                    )
                )

        return alerts

    def _generate_operational_alerts(self, data: List[Dict]) -> List[Alert]:
        """Generate operational alerts for any data."""
        alerts = []

        if len(data) > 0:
            # Generic low-data alert
            if len(data) < 5:
                alerts.append(
                    Alert(
                        title="Insufficient Data Alert",
                        message="Limited data points - insights may be incomplete",
                        alert_type="OPERATIONAL",
                        level=AlertLevel.INFO.value,
                        entity="Data Quality",
                        metric_value=len(data),
                        threshold=5,
                        action_required=False,
                        recommended_actions=[
                            "Expand time period for analysis",
                            "Include additional metrics or dimensions",
                            "Verify data collection is complete"
                        ]
                    )
                )

        return alerts

    def get_active_alerts(self, level: Optional[str] = None) -> List[Alert]:
        """Get all active alerts, optionally filtered by level."""
        alerts = list(self.active_alerts.values())

        if level:
            alerts = [a for a in alerts if a.level == level]

        return sorted(alerts, key=lambda x: self._severity_score(x.level), reverse=True)

    def clear_alert(self, entity: str, alert_type: str) -> bool:
        """Clear a specific alert."""
        key = f"{entity}_{alert_type}"
        if key in self.active_alerts:
            del self.active_alerts[key]
            return True
        return False

    def acknowledge_alert(self, entity: str, alert_type: str, notes: str = "") -> Dict:
        """Acknowledge an alert (mark as reviewed)."""
        key = f"{entity}_{alert_type}"
        if key in self.active_alerts:
            alert = self.active_alerts[key]
            return {
                "acknowledged": True,
                "alert": alert.to_dict(),
                "notes": notes
            }
        return {"acknowledged": False, "error": "Alert not found"}
