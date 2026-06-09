"""
Opportunity finder for autonomous identification of business growth opportunities.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Opportunity:
    """Represents a discovered business opportunity."""
    title: str
    description: str
    opportunity_type: str  # "EXPANSION", "OPTIMIZATION", "NEW_MARKET", "COST_SAVING", "REVENUE_GROWTH"
    impact: str  # "LOW", "MEDIUM", "HIGH"
    implementation_effort: str  # "LOW", "MEDIUM", "HIGH"
    estimated_impact_value: float  # Estimated financial impact
    affected_entities: List[str]  # Products, regions, etc.
    action_items: List[str]
    priority: int  # 1-10 score
    discovered_at: datetime = None

    def __post_init__(self):
        if self.discovered_at is None:
            self.discovered_at = datetime.utcnow()

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "type": self.opportunity_type,
            "impact": self.impact,
            "effort": self.implementation_effort,
            "estimated_value": self.estimated_impact_value,
            "entities": self.affected_entities,
            "actions": self.action_items,
            "priority": self.priority,
            "discovered": self.discovered_at.isoformat()
        }


class OpportunityFinder:
    """Find business opportunities in FMCG data."""

    def __init__(self):
        """Initialize opportunity finder."""
        self.minimum_opportunity_value = 10000  # Minimum $10k impact to report

    def find_opportunities(
        self,
        query_results: List[Dict],
        metadata: Dict,
        historical_data: Optional[List[Dict]] = None
    ) -> List[Opportunity]:
        """
        Find business opportunities in data.

        Args:
            query_results: Current query results
            metadata: Query metadata
            historical_data: Optional historical data for comparison

        Returns:
            List of discovered opportunities
        """
        opportunities = []

        intent = metadata.get("intent", "")

        # Route to appropriate finder based on intent
        if intent == "PROMO_PERFORMANCE":
            opportunities.extend(self._find_promo_opportunities(query_results))
        elif intent == "REGIONAL_SALES":
            opportunities.extend(self._find_regional_opportunities(query_results))
        elif intent == "PRODUCT_PERFORMANCE":
            opportunities.extend(self._find_product_opportunities(query_results))
        elif intent == "INVENTORY_ANALYSIS":
            opportunities.extend(self._find_inventory_opportunities(query_results))
        else:
            opportunities.extend(self._find_generic_opportunities(query_results))

        # Sort by priority
        return sorted(opportunities, key=lambda x: x.priority, reverse=True)

    def _find_promo_opportunities(self, data: List[Dict]) -> List[Opportunity]:
        """Find promotion-related opportunities."""
        opportunities = []

        if not data:
            return opportunities

        # Identify promotions that could be expanded
        for item in data:
            product = item.get("product_name", "Unknown")
            sales = item.get("total_sales", 0)
            discount = item.get("avg_discount", 0)
            units = item.get("total_units", 0)

            # Opportunity: Scale successful promos
            if sales > 50000 and discount < 20:
                estimated_impact = sales * 0.25  # 25% expansion revenue
                if estimated_impact > self.minimum_opportunity_value:
                    desc = f"{product} shows strong performance with {discount:.1f}% discount. "
                    desc += f"Could expand to additional channels/regions."
                    opportunities.append(
                        Opportunity(
                            title=f"Scale Successful Promotion: {product}",
                            description=desc,
                            opportunity_type="EXPANSION",
                            impact="HIGH",
                            implementation_effort="MEDIUM",
                            estimated_impact_value=estimated_impact,
                            affected_entities=[product],
                            action_items=[
                                f"1. Analyze channel mix for {product} promotion",
                                f"2. Identify similar high-performing regions for expansion",
                                f"3. Develop rollout plan for additional markets",
                                f"4. Budget for expanded promotion spend"
                            ],
                            priority=9
                        )
                    )

            # Opportunity: Optimize discount level
            if discount > 25 and sales < 30000:
                estimated_saving = sales * (discount * 0.05)  # 5% margin improvement potential
                if estimated_saving > self.minimum_opportunity_value:
                    desc = f"{product} uses high discount ({discount:.1f}%) but shows weak sales."
                    desc += f" Could reduce discount and use alternative tactics."
                    opportunities.append(
                        Opportunity(
                            title=f"Optimize Discount Level: {product}",
                            description=desc,
                            opportunity_type="OPTIMIZATION",
                            impact="MEDIUM",
                            implementation_effort="LOW",
                            estimated_impact_value=estimated_saving,
                            affected_entities=[product],
                            action_items=[
                                f"1. Run A/B test with lower discount ({discount-5:.1f}%)",
                                f"2. Combine with targeted marketing campaign",
                                f"3. Test in 2-3 regions first before scaling",
                                f"4. Measure volume/margin trade-off"
                            ],
                            priority=7
                        )
                    )

        return opportunities

    def _find_regional_opportunities(self, data: List[Dict]) -> List[Opportunity]:
        """Find regional expansion opportunities."""
        opportunities = []

        if not data:
            return opportunities

        # Find high-potential underperforming regions
        sorted_regions = sorted(data, key=lambda x: x.get("total_sales", 0), reverse=True)

        if len(sorted_regions) > 1:
            best_region = sorted_regions[0]
            best_sales = best_region.get("total_sales", 0)
            best_stores = best_region.get("store_count", 1)
            best_per_store = best_sales / best_stores if best_stores > 0 else 0

            for region in sorted_regions[1:]:
                region_name = region.get("region", "Unknown")
                region_sales = region.get("total_sales", 0)
                region_stores = region.get("store_count", 1)
                region_per_store = region_sales / region_stores if region_stores > 0 else 0

                # Opportunity: Expand to underperforming but accessible region
                if region_stores > 5 and region_per_store < best_per_store * 0.7:
                    # Estimate potential with best practices
                    potential_sales = region_per_store * 1.3 * region_stores
                    uplift = potential_sales - region_sales

                    if uplift > self.minimum_opportunity_value:
                        desc = f"{region_name} has {region_stores} stores but lags peer regions."
                        desc += f" Per-store performance could be improved by 30%."
                        opportunities.append(
                            Opportunity(
                                title=f"Regional Performance Uplift: {region_name}",
                                description=desc,
                                opportunity_type="REVENUE_GROWTH",
                                impact="HIGH",
                                implementation_effort="MEDIUM",
                                estimated_impact_value=uplift,
                                affected_entities=[region_name],
                                action_items=[
                                    f"1. Benchmark {region_name} operations vs {best_region.get('region')}",
                                    f"2. Identify operational gaps and best practices",
                                    f"3. Implement training programs for {region_name} stores",
                                    f"4. Increase promotional support in {region_name}"
                                ],
                                priority=8
                            )
                        )

        return opportunities

    def _find_product_opportunities(self, data: List[Dict]) -> List[Opportunity]:
        """Find product-specific opportunities."""
        opportunities = []

        if not data:
            return opportunities

        # Identify products with different characteristics
        high_volume = sorted(data, key=lambda x: x.get("total_units", 0), reverse=True)
        high_margin = sorted(data, key=lambda x: x.get("total_margin", 0), reverse=True)

        # Opportunity: Cross-sell high-margin products
        if high_margin:
            top_margin_product = high_margin[0]
            if top_margin_product.get("total_units", 0) < 10000:  # Room to grow
                estimated_uplift = top_margin_product.get("total_margin", 0) * 0.4
                if estimated_uplift > self.minimum_opportunity_value:
                    prod_name = top_margin_product.get('product_name')
                    desc = f"{prod_name} has excellent margins but low volume."
                    desc += f" Increase distribution and marketing support."
                    opportunities.append(
                        Opportunity(
                            title=f"Grow High-Margin Product: {prod_name}",
                            description=desc,
                            opportunity_type="REVENUE_GROWTH",
                            impact="MEDIUM",
                            implementation_effort="LOW",
                            estimated_impact_value=estimated_uplift,
                            affected_entities=[top_margin_product.get("product_name", "")],
                            action_items=[
                                f"1. Increase shelf space allocation",
                                f"2. Run targeted promotional campaigns",
                                f"3. Incentivize store staff for upselling",
                                f"4. Bundle with popular products"
                            ],
                            priority=8
                        )
                    )

        # Opportunity: SKU rationalization
        if len(data) > 10:
            low_performers = sorted(data, key=lambda x: x.get("total_sales", 0))[:5]
            total_low_sales = sum(p.get("total_sales", 0) for p in low_performers)
            if total_low_sales < 20000:  # Bottom 5 products low sales
                desc = "Multiple products show consistently low performance."
                desc += " Consider consolidating or discontinuing underperformers."
                opportunities.append(
                    Opportunity(
                        title="SKU Rationalization Opportunity",
                        description=desc,
                        opportunity_type="COST_SAVING",
                        impact="MEDIUM",
                        implementation_effort="HIGH",
                        estimated_impact_value=100000,  # Inventory reduction benefit
                        affected_entities=[p.get("product_name", "") for p in low_performers],
                        action_items=[
                            "1. Analyze historical performance trends",
                            "2. Calculate carrying cost of low-volume SKUs",
                            "3. Evaluate customer demand and substitutes",
                            "4. Plan gradual phase-out to minimize disruption"
                        ],
                        priority=6
                    )
                )

        return opportunities

    def _find_inventory_opportunities(self, data: List[Dict]) -> List[Opportunity]:
        """Find inventory optimization opportunities."""
        opportunities = []

        if not data:
            return opportunities

        # Find products with excess inventory
        high_inventory = [d for d in data if d.get("days_inventory", 0) > 60]
        for item in high_inventory:
            product = item.get("product_name", "Unknown")
            days = item.get("days_inventory", 0)
            current_value = item.get("inventory_value", 0)

            # Opportunity: Reduce excess inventory
            excess_fraction = (days - 30) / days if days > 0 else 0
            inventory_reduction = current_value * excess_fraction

            if inventory_reduction > self.minimum_opportunity_value:
                desc = f"{product} has {days:.0f} days of inventory (target: 30)."
                desc += f" Can reduce by {excess_fraction*100:.0f}% through optimization."
                opportunities.append(
                    Opportunity(
                        title=f"Reduce Excess Inventory: {product}",
                        description=desc,
                        opportunity_type="COST_SAVING",
                        impact="MEDIUM",
                        implementation_effort="MEDIUM",
                        estimated_impact_value=inventory_reduction,
                        affected_entities=[product],
                        action_items=[
                            f"1. Run clearance promotion for {product}",
                            f"2. Adjust replenishment orders to {days-30} days",
                            f"3. Negotiate shelf space reduction if needed",
                            f"4. Monitor stock-outs post-reduction"
                        ],
                        priority=7
                    )
                )

        return opportunities

    def _find_generic_opportunities(self, data: List[Dict]) -> List[Opportunity]:
        """Find generic opportunities from any data."""
        opportunities = []

        if len(data) < 5:
            return opportunities

        # Basic analysis: find items with best metrics
        if "total_sales" in data[0]:
            sorted_by_sales = sorted(data, key=lambda x: x.get("total_sales", 0), reverse=True)
            top_item = sorted_by_sales[0]

            opportunities.append(
                Opportunity(
                    title="Identify and Scale Top Performers",
                    description="Data shows clear performance leaders that could be scaled.",
                    opportunity_type="EXPANSION",
                    impact="HIGH",
                    implementation_effort="LOW",
                    estimated_impact_value=50000,
                    affected_entities=[top_item.get("product_name", "") or top_item.get("region", "")],
                    action_items=[
                        "1. Analyze success factors of top performers",
                        "2. Document best practices and processes",
                        "3. Replicate to similar contexts",
                        "4. Measure results and iterate"
                    ],
                    priority=8
                )
            )

        return opportunities
