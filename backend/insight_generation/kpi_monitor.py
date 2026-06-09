"""
KPI monitoring and tracking for automated KPI dashboards.
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class KPIStatus(Enum):
    """KPI status indicators."""
    ON_TARGET = "ON_TARGET"
    AT_RISK = "AT_RISK"
    BELOW_TARGET = "BELOW_TARGET"
    ABOVE_TARGET = "ABOVE_TARGET"


@dataclass
class KPI:
    """KPI definition and tracking."""
    name: str
    display_name: str
    metric_field: str
    current_value: float
    target_value: float
    previous_value: Optional[float] = None
    unit: str = ""
    status: str = "ON_TARGET"
    variance_pct: float = 0.0  # Actual vs target
    trend: str = "STABLE"  # UP, DOWN, STABLE
    threshold_warn: float = 0.9  # Warn at 90% of target
    threshold_critical: float = 0.7  # Critical at 70% of target
    last_updated: datetime = None
    period: str = "MONTHLY"  # DAILY, WEEKLY, MONTHLY, QUARTERLY

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()

    def to_dict(self):
        data = asdict(self)
        data['last_updated'] = self.last_updated.isoformat()
        return data


class KPIMonitor:
    """Monitor and track FMCG KPIs."""

    def __init__(self):
        """Initialize KPI monitor."""
        self.kpis = {}
        self.history = {}  # Track historical values

        # Define standard FMCG KPIs
        self.define_standard_kpis()

    def define_standard_kpis(self):
        """Define standard FMCG KPIs."""
        standard_kpis = {
            "revenue": KPI(
                name="revenue",
                display_name="Total Revenue",
                metric_field="total_sales",
                current_value=0,
                target_value=1000000,
                unit="$",
                threshold_warn=900000,
                threshold_critical=700000
            ),
            "units_sold": KPI(
                name="units_sold",
                display_name="Units Sold",
                metric_field="total_units",
                current_value=0,
                target_value=100000,
                unit="units",
                threshold_warn=90000,
                threshold_critical=70000
            ),
            "avg_discount": KPI(
                name="avg_discount",
                display_name="Average Discount",
                metric_field="avg_discount",
                current_value=0,
                target_value=15,  # Target: 15% max
                unit="%",
                threshold_warn=20,
                threshold_critical=30
            ),
            "margin": KPI(
                name="margin",
                display_name="Gross Margin",
                metric_field="total_margin",
                current_value=0,
                target_value=300000,
                unit="$",
                threshold_warn=270000,
                threshold_critical=210000
            ),
            "stockout_rate": KPI(
                name="stockout_rate",
                display_name="Stockout Rate",
                metric_field="stockout_count",
                current_value=0,
                target_value=0,  # Target: zero stockouts
                unit="count",
                threshold_warn=1,
                threshold_critical=5
            ),
            "inventory_days": KPI(
                name="inventory_days",
                display_name="Days Inventory Outstanding",
                metric_field="days_inventory",
                current_value=0,
                target_value=30,
                unit="days",
                threshold_warn=45,
                threshold_critical=60
            ),
            "turnover_rate": KPI(
                name="turnover_rate",
                display_name="Inventory Turnover",
                metric_field="turnover_rate",
                current_value=0,
                target_value=10,  # Target: 10x per year
                unit="x/year",
                threshold_warn=8,
                threshold_critical=5
            ),
            "promo_lift": KPI(
                name="promo_lift",
                display_name="Promotion Lift",
                metric_field="sales_lift_pct",
                current_value=0,
                target_value=30,  # Target: 30% lift
                unit="%",
                threshold_warn=20,
                threshold_critical=10
            )
        }

        self.kpis = standard_kpis

    def update_kpi(
        self,
        kpi_name: str,
        current_value: float,
        previous_value: Optional[float] = None
    ) -> KPI:
        """
        Update a KPI with new value.

        Args:
            kpi_name: Name of KPI to update
            current_value: New current value
            previous_value: Previous value for trend analysis

        Returns:
            Updated KPI object
        """
        if kpi_name not in self.kpis:
            logger.warning(f"KPI {kpi_name} not found")
            return None

        kpi = self.kpis[kpi_name]
        kpi.previous_value = previous_value or kpi.current_value
        kpi.current_value = current_value
        kpi.last_updated = datetime.utcnow()

        # Calculate variance
        if kpi.target_value != 0:
            kpi.variance_pct = ((current_value - kpi.target_value) / kpi.target_value) * 100
        else:
            kpi.variance_pct = 0

        # Determine trend
        if kpi.previous_value is not None:
            if current_value > kpi.previous_value * 1.05:
                kpi.trend = "UP"
            elif current_value < kpi.previous_value * 0.95:
                kpi.trend = "DOWN"
            else:
                kpi.trend = "STABLE"

        # Determine status
        kpi.status = self._determine_status(kpi)

        # Log to history
        if kpi_name not in self.history:
            self.history[kpi_name] = []
        self.history[kpi_name].append({
            "value": current_value,
            "status": kpi.status,
            "timestamp": kpi.last_updated.isoformat()
        })

        return kpi

    def _determine_status(self, kpi: KPI) -> str:
        """Determine KPI status based on current value vs targets."""
        # Special case: metrics where lower is better (discounts, stockouts, days inventory)
        if kpi.name in ["avg_discount", "stockout_rate", "inventory_days"]:
            if kpi.current_value <= kpi.threshold_warn:
                return KPIStatus.ON_TARGET.value
            elif kpi.current_value <= kpi.threshold_critical:
                return KPIStatus.AT_RISK.value
            else:
                return KPIStatus.BELOW_TARGET.value

        # Default: higher is better
        if kpi.current_value >= kpi.target_value:
            return KPIStatus.ABOVE_TARGET.value
        elif kpi.current_value >= kpi.threshold_warn:
            return KPIStatus.ON_TARGET.value
        elif kpi.current_value >= kpi.threshold_critical:
            return KPIStatus.AT_RISK.value
        else:
            return KPIStatus.BELOW_TARGET.value

    def get_kpi_status(self, kpi_name: str) -> Optional[Dict]:
        """Get current status of a KPI."""
        if kpi_name not in self.kpis:
            return None

        kpi = self.kpis[kpi_name]
        return kpi.to_dict()

    def get_all_kpis(self) -> Dict[str, Dict]:
        """Get all KPIs and their status."""
        return {name: kpi.to_dict() for name, kpi in self.kpis.items()}

    def get_at_risk_kpis(self) -> List[Dict]:
        """Get KPIs that are at risk or below target."""
        at_risk = [
            kpi.to_dict() for kpi in self.kpis.values()
            if kpi.status in [KPIStatus.AT_RISK.value, KPIStatus.BELOW_TARGET.value]
        ]
        return sorted(at_risk, key=lambda x: x["variance_pct"])

    def calculate_kpi_dashboard(self, query_results: List[Dict]) -> Dict:
        """
        Calculate KPI dashboard from query results.

        Args:
            query_results: Query result data

        Returns:
            Dashboard with KPI status
        """
        if not query_results:
            return {"error": "No data provided"}

        dashboard = {
            "timestamp": datetime.utcnow().isoformat(),
            "kpis": {},
            "summary": {
                "total_kpis": 0,
                "on_target": 0,
                "at_risk": 0,
                "below_target": 0
            },
            "health_score": 100
        }

        # Try to extract KPI values from results
        try:
            # Common field mappings
            if "total_sales" in query_results[0]:
                total_sales = sum(r.get("total_sales", 0) for r in query_results)
                self.update_kpi("revenue", total_sales)

            if "total_units" in query_results[0]:
                total_units = sum(r.get("total_units", 0) for r in query_results)
                self.update_kpi("units_sold", total_units)

            if "avg_discount" in query_results[0]:
                avg_discount = sum(r.get("avg_discount", 0) for r in query_results) / len(query_results)
                self.update_kpi("avg_discount", avg_discount)

            if "total_margin" in query_results[0]:
                total_margin = sum(r.get("total_margin", 0) for r in query_results)
                self.update_kpi("margin", total_margin)

            if "stockout_count" in query_results[0]:
                stockout_count = sum(r.get("stockout_count", 0) for r in query_results)
                self.update_kpi("stockout_rate", stockout_count)

        except Exception as e:
            logger.warning(f"Error extracting KPIs: {str(e)}")

        # Build dashboard
        for name, kpi in self.kpis.items():
            dashboard["kpis"][name] = kpi.to_dict()

            # Update summary counts
            dashboard["summary"]["total_kpis"] += 1
            if kpi.status == KPIStatus.ON_TARGET.value:
                dashboard["summary"]["on_target"] += 1
            elif kpi.status == KPIStatus.AT_RISK.value:
                dashboard["summary"]["at_risk"] += 1
            else:
                dashboard["summary"]["below_target"] += 1

        # Calculate health score (0-100)
        total_kpis = dashboard["summary"]["total_kpis"]
        on_target = dashboard["summary"]["on_target"]
        at_risk = dashboard["summary"]["at_risk"]

        if total_kpis > 0:
            dashboard["health_score"] = int((on_target / total_kpis) * 100) - (at_risk * 5)
            dashboard["health_score"] = max(0, min(100, dashboard["health_score"]))

        # Add recommendations
        dashboard["recommendations"] = []
        for kpi in self.get_at_risk_kpis():
            if kpi["status"] == KPIStatus.BELOW_TARGET.value:
                dashboard["recommendations"].append(
                    f"URGENT: {kpi['display_name']} is below target ({kpi['current_value']:.1f} vs {kpi['target_value']:.1f})"
                )
            elif kpi["status"] == KPIStatus.AT_RISK.value:
                dashboard["recommendations"].append(
                    f"WATCH: {kpi['display_name']} trending toward target breach"
                )

        return dashboard

    def get_kpi_history(self, kpi_name: str, days: int = 30) -> List[Dict]:
        """Get historical KPI values."""
        if kpi_name not in self.history:
            return []

        return self.history[kpi_name][-days:]

    def get_kpi_forecast(self, kpi_name: str, days_ahead: int = 7) -> Dict:
        """
        Simple forecast of KPI values.

        Args:
            kpi_name: KPI to forecast
            days_ahead: Number of days to forecast

        Returns:
            Forecast data
        """
        if kpi_name not in self.history or len(self.history[kpi_name]) < 3:
            return {"error": "Insufficient history for forecast"}

        history = self.history[kpi_name][-14:]  # Last 14 days
        values = [h["value"] for h in history]

        # Simple linear forecast
        trend = (values[-1] - values[0]) / len(values)
        last_value = values[-1]

        forecast = []
        for day in range(1, days_ahead + 1):
            predicted = last_value + (trend * day)
            forecast.append({
                "day": day,
                "predicted_value": predicted,
                "confidence": 0.7  # Simple confidence
            })

        return {
            "kpi_name": kpi_name,
            "current_value": last_value,
            "trend": "UP" if trend > 0 else "DOWN" if trend < 0 else "STABLE",
            "forecast": forecast
        }
