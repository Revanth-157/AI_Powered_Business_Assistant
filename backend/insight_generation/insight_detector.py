"""
Insight detection for autonomous discovery of business issues and opportunities.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class InsightFinding:
    """Represents a discovered insight."""
    type: str  # "ISSUE", "OPPORTUNITY", "TREND", "ANOMALY"
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    title: str
    description: str
    metric: str  # What metric this relates to
    current_value: float
    baseline_value: Optional[float] = None
    change_percent: Optional[float] = None
    recommendation: str = ""
    confidence: float = 0.8  # 0-1 confidence score
    affected_entities: List[str] = None  # Which products/regions/stores affected
    generated_at: datetime = None

    def __post_init__(self):
        if self.affected_entities is None:
            self.affected_entities = []
        if self.generated_at is None:
            self.generated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "type": self.type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "metric": self.metric,
            "current_value": self.current_value,
            "baseline_value": self.baseline_value,
            "change_percent": self.change_percent,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "affected_entities": self.affected_entities,
            "generated_at": self.generated_at.isoformat()
        }


class InsightDetector:
    """Detects business insights from FMCG data."""

    def __init__(self):
        """Initialize insight detector."""
        self.thresholds = {
            "sales_drop": -20,  # Alert if sales drop > 20%
            "sales_spike": 30,  # Alert if sales spike > 30%
            "stockout_threshold": 0.1,  # Alert if stockouts > 10% of SKUs
            "margin_drop": -15,  # Alert if margin drops > 15%
            "inventory_high": 90,  # Alert if inventory > 90 days
            "inventory_low": 5,  # Alert if inventory < 5 days
            "promo_efficiency": 1.2,  # Expected min lift from promotion
        }

    def detect_insights(self, query_results: List[Dict], metadata: Dict) -> List[InsightFinding]:
        """
        Detect insights from query results.

        Args:
            query_results: Query result data
            metadata: Query metadata with intent and context

        Returns:
            List of discovered insights
        """
        if not query_results:
            return []

        intent = metadata.get("intent", "")
        findings = []

        # Route to appropriate detector based on query intent
        if intent == "PROMO_PERFORMANCE":
            findings.extend(self._detect_promo_insights(query_results))
        elif intent == "REGIONAL_SALES":
            findings.extend(self._detect_regional_insights(query_results))
        elif intent == "STOCKOUT_ANALYSIS":
            findings.extend(self._detect_stockout_insights(query_results))
        elif intent == "PRODUCT_PERFORMANCE":
            findings.extend(self._detect_product_insights(query_results))
        elif intent == "INVENTORY_ANALYSIS":
            findings.extend(self._detect_inventory_insights(query_results))
        elif intent == "CAMPAIGN_IMPACT":
            findings.extend(self._detect_campaign_insights(query_results))
        else:
            findings.extend(self._detect_generic_insights(query_results))

        return findings

    def _detect_promo_insights(self, data: List[Dict]) -> List[InsightFinding]:
        """Detect promotion performance insights."""
        findings = []

        if not data:
            return findings

        # Calculate metrics
        avg_sales = sum(row.get("total_sales", 0) for row in data) / len(data)
        avg_units = sum(row.get("total_units", 0) for row in data) / len(data)
        avg_discount = sum(row.get("avg_discount", 0) for row in data) / len(data)

        # Detect top performers
        top_performers = sorted(data, key=lambda x: x.get("total_sales", 0), reverse=True)[:3]
        if top_performers:
            top = top_performers[0]
            sales_diff = ((top.get("total_sales", 0) - avg_sales) / avg_sales * 100) if avg_sales else 0
            if sales_diff > 50:
                findings.append(
                    InsightFinding(
                        type="OPPORTUNITY",
                        severity="HIGH",
                        title=f"Star Performer: {top.get('product_name', 'Product')}",
                        description=f"{top.get('product_name')} significantly outperforms other promotions",
                        metric="sales_performance",
                        current_value=top.get("total_sales", 0),
                        baseline_value=avg_sales,
                        change_percent=sales_diff,
                        recommendation=f"Scale promotion for {top.get('product_name')} to similar channels",
                        affected_entities=[top.get("product_name", "")],
                        confidence=0.95
                    )
                )

        # Detect underperformers
        bottom_performers = sorted(data, key=lambda x: x.get("total_sales", 0))[:3]
        if bottom_performers:
            bottom = bottom_performers[0]
            sales_diff = ((bottom.get("total_sales", 0) - avg_sales) / avg_sales * 100) if avg_sales else 0
            if sales_diff < -40:
                findings.append(
                    InsightFinding(
                        type="ISSUE",
                        severity="MEDIUM",
                        title=f"Underperforming: {bottom.get('product_name', 'Product')}",
                        description=f"{bottom.get('product_name')} underperforms promotion expectations",
                        metric="sales_performance",
                        current_value=bottom.get("total_sales", 0),
                        baseline_value=avg_sales,
                        change_percent=sales_diff,
                        recommendation=f"Review promotion strategy or pricing for {bottom.get('product_name')}",
                        affected_entities=[bottom.get("product_name", "")],
                        confidence=0.85
                    )
                )

        # Detect inefficient discounts
        high_discount_rows = [r for r in data if r.get("avg_discount", 0) > 30]
        for row in high_discount_rows:
            if row.get("total_sales", 0) < avg_sales:
                findings.append(
                    InsightFinding(
                        type="ISSUE",
                        severity="MEDIUM",
                        title="Discount Not Driving Sales",
                        description=f"Heavy discount ({row.get('avg_discount', 0):.1f}%) not translating to sales lift",
                        metric="discount_efficiency",
                        current_value=row.get("avg_discount", 0),
                        baseline_value=20,
                        change_percent=(row.get("avg_discount", 0) - 20),
                        recommendation="Consider lower discount with targeted marketing instead",
                        affected_entities=[row.get("product_name", "")],
                        confidence=0.8
                    )
                )

        return findings

    def _detect_regional_insights(self, data: List[Dict]) -> List[InsightFinding]:
        """Detect regional sales insights."""
        findings = []

        if not data:
            return findings

        # Find best and worst regions
        sorted_regions = sorted(data, key=lambda x: x.get("total_sales", 0), reverse=True)

        if len(sorted_regions) > 1:
            best = sorted_regions[0]
            worst = sorted_regions[-1]

            best_sales = best.get("total_sales", 0)
            worst_sales = worst.get("total_sales", 0)

            if best_sales > 0:
                disparity = ((best_sales - worst_sales) / best_sales * 100)
                if disparity > 50:
                    findings.append(
                        InsightFinding(
                            type="ISSUE",
                            severity="HIGH",
                            title="High Regional Disparity",
                            description=f"{best.get('region')} outperforms {worst.get('region')} by {disparity:.1f}%",
                            metric="regional_performance",
                            current_value=best_sales,
                            baseline_value=worst_sales,
                            change_percent=disparity,
                            recommendation=f"Investigate market conditions in {worst.get('region')} for improvement",
                            affected_entities=[best.get("region", ""), worst.get("region", "")],
                            confidence=0.9
                        )
                    )

        # Detect growth regions
        for region in data:
            growth = region.get("store_count", 0)
            sales = region.get("total_sales", 0)
            if growth > 5 and sales > 0:
                per_store = sales / growth if growth > 0 else 0
                findings.append(
                    InsightFinding(
                        type="OPPORTUNITY",
                        severity="MEDIUM",
                        title=f"Growth Market: {region.get('region')}",
                        description=f"{region.get('region')} has strong store density with good sales",
                        metric="market_opportunity",
                        current_value=per_store,
                        baseline_value=0,
                        recommendation=f"Expand distribution in {region.get('region')}",
                        affected_entities=[region.get("region", "")],
                        confidence=0.85
                    )
                )

        return findings

    def _detect_stockout_insights(self, data: List[Dict]) -> List[InsightFinding]:
        """Detect stockout and supply chain issues."""
        findings = []

        if not data:
            return findings

        total_issues = len(data)
        if total_issues > 0:
            findings.append(
                InsightFinding(
                    type="ISSUE",
                    severity="CRITICAL",
                    title=f"Stockout Alert: {total_issues} SKUs",
                    description=f"{total_issues} product-region combinations experiencing stockouts",
                    metric="stockout_count",
                    current_value=total_issues,
                    baseline_value=0,
                    recommendation="Expedite inventory replenishment to affected stores",
                    affected_entities=[row.get("product_name", "") for row in data[:5]],
                    confidence=0.99
                )
            )

        # Calculate lost revenue
        total_lost = sum(row.get("lost_sales", 0) for row in data)
        if total_lost > 0:
            findings.append(
                InsightFinding(
                    type="ISSUE",
                    severity="HIGH",
                    title="Lost Revenue from Stockouts",
                    description=f"Estimated ${total_lost:,.0f} revenue lost due to stockouts",
                    metric="lost_revenue",
                    current_value=total_lost,
                    baseline_value=0,
                    recommendation="Implement safety stock for high-velocity SKUs",
                    affected_entities=list(set(row.get("region", "") for row in data)),
                    confidence=0.95
                )
            )

        return findings

    def _detect_product_insights(self, data: List[Dict]) -> List[InsightFinding]:
        """Detect product performance insights."""
        findings = []

        if not data:
            return findings

        avg_margin = sum(row.get("total_margin", 0) for row in data) / len(data) if data else 0
        avg_sales = sum(row.get("total_sales", 0) for row in data) / len(data) if data else 0

        # High-margin products
        high_margin = [r for r in data if r.get("total_margin", 0) > avg_margin * 1.5]
        for product in high_margin[:3]:
            margin_pct = (product.get("total_margin", 0) / product.get("total_sales", 1)) * 100 if product.get("total_sales", 0) > 0 else 0
            findings.append(
                InsightFinding(
                    type="OPPORTUNITY",
                    severity="MEDIUM",
                    title=f"High-Margin Product: {product.get('product_name')}",
                    description=f"{product.get('product_name')} delivers {margin_pct:.1f}% margin",
                    metric="product_margin",
                    current_value=product.get("total_margin", 0),
                    baseline_value=avg_margin,
                    change_percent=(margin_pct),
                    recommendation="Prioritize shelf space and marketing for this product",
                    affected_entities=[product.get("product_name", "")],
                    confidence=0.9
                )
            )

        # Fast movers
        high_velocity = sorted(data, key=lambda x: x.get("total_units", 0), reverse=True)[:2]
        for product in high_velocity:
            findings.append(
                InsightFinding(
                    type="OPPORTUNITY",
                    severity="MEDIUM",
                    title=f"Fast-Moving SKU: {product.get('product_name')}",
                    description=f"{product.get('product_name')} shows strong consumer demand",
                    metric="sales_velocity",
                    current_value=product.get("total_units", 0),
                    baseline_value=0,
                    recommendation="Ensure adequate stock to meet demand",
                    affected_entities=[product.get("product_name", "")],
                    confidence=0.9
                )
            )

        return findings

    def _detect_inventory_insights(self, data: List[Dict]) -> List[InsightFinding]:
        """Detect inventory and turnover insights."""
        findings = []

        if not data:
            return findings

        for item in data:
            days_inventory = item.get("days_inventory", 0)
            turn_rate = item.get("turnover_rate", 0)

            if days_inventory > self.thresholds["inventory_high"]:
                findings.append(
                    InsightFinding(
                        type="ISSUE",
                        severity="MEDIUM",
                        title="Excess Inventory",
                        description=f"{item.get('product_name')} has {days_inventory:.0f} days of inventory",
                        metric="inventory_level",
                        current_value=days_inventory,
                        baseline_value=30,
                        change_percent=(days_inventory - 30),
                        recommendation="Run clearance promotion or adjust orders",
                        affected_entities=[item.get("product_name", "")],
                        confidence=0.85
                    )
                )

            if days_inventory < self.thresholds["inventory_low"]:
                findings.append(
                    InsightFinding(
                        type="ISSUE",
                        severity="HIGH",
                        title="Low Inventory Risk",
                        description=f"{item.get('product_name')} at only {days_inventory:.0f} days supply",
                        metric="inventory_level",
                        current_value=days_inventory,
                        baseline_value=30,
                        change_percent=(days_inventory - 30),
                        recommendation="Accelerate replenishment orders",
                        affected_entities=[item.get("product_name", "")],
                        confidence=0.9
                    )
                )

        return findings

    def _detect_campaign_insights(self, data: List[Dict]) -> List[InsightFinding]:
        """Detect campaign effectiveness insights."""
        findings = []

        if not data:
            return findings

        for campaign in data:
            lift = campaign.get("sales_lift_pct", 0)
            roi = campaign.get("roi_pct", 0)

            if lift > self.thresholds["promo_efficiency"] * 100:
                findings.append(
                    InsightFinding(
                        type="OPPORTUNITY",
                        severity="HIGH",
                        title="Highly Effective Campaign",
                        description=f"Campaign driving {lift:.1f}% sales lift",
                        metric="campaign_effectiveness",
                        current_value=lift,
                        baseline_value=20,
                        change_percent=lift,
                        recommendation="Scale this campaign to additional SKUs/regions",
                        affected_entities=[campaign.get("product_name", "")],
                        confidence=0.9
                    )
                )

            if roi > 200:
                findings.append(
                    InsightFinding(
                        type="OPPORTUNITY",
                        severity="HIGH",
                        title="Excellent Campaign ROI",
                        description=f"Campaign delivering {roi:.1f}% ROI",
                        metric="campaign_roi",
                        current_value=roi,
                        baseline_value=100,
                        change_percent=(roi - 100),
                        recommendation="Document and replicate this campaign",
                        affected_entities=[campaign.get("product_name", "")],
                        confidence=0.95
                    )
                )

        return findings

    def _detect_generic_insights(self, data: List[Dict]) -> List[InsightFinding]:
        """Detect generic insights for unknown query types."""
        findings = []

        if not data:
            return findings

        # Basic statistics
        if len(data) > 0:
            # Find max and min values
            if "total_sales" in data[0]:
                sales_values = [r.get("total_sales", 0) for r in data]
                max_sales = max(sales_values)
                min_sales = min(sales_values)
                avg_sales = sum(sales_values) / len(sales_values)

                if max_sales > avg_sales * 2:
                    findings.append(
                        InsightFinding(
                            type="OPPORTUNITY",
                            severity="MEDIUM",
                            title="High Performer Identified",
                            description=f"Top entry is {(max_sales/avg_sales):.1f}x average performance",
                            metric="performance_ratio",
                            current_value=max_sales,
                            baseline_value=avg_sales,
                            change_percent=((max_sales - avg_sales) / avg_sales * 100),
                            recommendation="Analyze and replicate success factors",
                            confidence=0.8
                        )
                    )

        return findings
