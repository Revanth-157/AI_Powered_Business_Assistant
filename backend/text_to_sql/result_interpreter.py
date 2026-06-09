"""
Result interpretation for Text-to-SQL queries.
"""
from typing import Dict, List, Any, Tuple
import statistics
import logging

logger = logging.getLogger(__name__)


class ResultInterpreter:
    """Interpret query results and generate insights."""
    
    def __init__(self):
        """Initialize result interpreter."""
        pass
    
    def interpret(self, results: List[Dict], metadata: Dict) -> Dict[str, Any]:
        """
        Interpret query results and generate insights.
        
        Args:
            results: List of result rows (dicts)
            metadata: Metadata from SQL generation (intent, tables, etc.)
        
        Returns:
            Dictionary with insights, summary, and visualizations
        """
        interpretation = {
            "summary": "",
            "key_findings": [],
            "insights": [],
            "metrics": {},
            "anomalies": [],
            "recommendations": [],
            "visualization": None
        }
        
        if not results:
            interpretation["summary"] = "No data found matching the query criteria."
            return interpretation
        
        intent = metadata.get("intent", "")
        
        # Route to appropriate interpreter based on intent
        if intent == "PROMO_PERFORMANCE":
            self._interpret_promo_performance(results, interpretation)
        elif intent == "REGIONAL_SALES":
            self._interpret_regional_sales(results, interpretation)
        elif intent == "STOCKOUT_ANALYSIS":
            self._interpret_stockout_analysis(results, interpretation)
        elif intent == "PRODUCT_PERFORMANCE":
            self._interpret_product_performance(results, interpretation)
        elif intent == "INVENTORY_ANALYSIS":
            self._interpret_inventory_analysis(results, interpretation)
        elif intent == "CAMPAIGN_IMPACT":
            self._interpret_campaign_impact(results, interpretation)
        else:
            self._interpret_generic(results, interpretation)
        
        return interpretation
    
    def _interpret_promo_performance(self, results: List[Dict], interpretation: Dict):
        """Interpret promotion performance results."""
        if not results:
            return
        
        # Get top performer
        top_promo = results[0]
        top_sales = top_promo.get("total_sales", 0)
        top_units = top_promo.get("total_units", 0)
        
        interpretation["summary"] = (
            f"Analysis of {len(results)} promoted products shows that "
            f"{top_promo.get('product_name', 'Top product')} is the best performer "
            f"with ${top_sales:,.2f} in sales and {top_units:,.0f} units sold."
        )
        
        # Calculate metrics
        sales_list = [r.get("total_sales", 0) for r in results if r.get("total_sales")]
        if sales_list:
            interpretation["metrics"] = {
                "total_promo_sales": sum(sales_list),
                "average_promo_sales": statistics.mean(sales_list),
                "median_promo_sales": statistics.median(sales_list),
                "std_dev_sales": statistics.stdev(sales_list) if len(sales_list) > 1 else 0,
                "num_products_promoted": len(results),
            }
        
        # Key findings
        avg_discount = statistics.mean([r.get("avg_discount", 0) for r in results if r.get("avg_discount") is not None])
        interpretation["key_findings"] = [
            f"Top 3 products by promotion sales: {', '.join([r.get('product_name', 'Unknown') for r in results[:3]])}",
            f"Average promotional discount: {avg_discount:.1f}%",
            f"Promotional lift potential: High across {len(results)} products"
        ]
        
        # Insights
        if len(results) > 1:
            top_sales_val = results[0].get("total_sales", 0)
            second_sales_val = results[1].get("total_sales", 0) if len(results) > 1 else 0
            if second_sales_val > 0:
                gap = ((top_sales_val - second_sales_val) / second_sales_val) * 100
                interpretation["insights"].append(
                    f"Top performer {top_promo.get('product_name')} outperforms second place by {gap:.1f}%"
                )
        
        # Recommendations
        interpretation["recommendations"] = [
            f"Increase promotion frequency for {top_promo.get('product_name')} - consistent top performer",
            f"Review underperforming products for potential issues or demand shifts",
            f"Optimize discount levels: current avg {avg_discount:.1f}% shows good ROI"
        ]
        
        # Visualization
        interpretation["visualization"] = {
            "type": "bar",
            "x_axis": "product_name",
            "y_axis": "total_sales",
            "title": "Promotion Performance by Product",
            "data": results[:10]  # Top 10
        }
    
    def _interpret_regional_sales(self, results: List[Dict], interpretation: Dict):
        """Interpret regional sales comparison."""
        if not results:
            return
        
        top_region = results[0]
        top_sales = top_region.get("total_sales", 0)
        
        interpretation["summary"] = (
            f"Regional sales analysis across {len(results)} regions shows {top_region.get('region', 'Top region')} "
            f"leads with ${top_sales:,.2f}. Market penetration and regional strategies vary significantly."
        )
        
        # Metrics
        sales_list = [r.get("total_sales", 0) for r in results]
        interpretation["metrics"] = {
            "total_sales_all_regions": sum(sales_list),
            "average_regional_sales": statistics.mean(sales_list),
            "highest_region_sales": max(sales_list),
            "lowest_region_sales": min(sales_list),
            "num_regions": len(results)
        }
        
        # Key findings
        interpretation["key_findings"] = [
            f"Leading region: {top_region.get('region')} with ${top_sales:,.2f}",
            f"Region count: {len(results)}",
            f"Store presence varies: {min([r.get('store_count', 0) for r in results])} to {max([r.get('store_count', 0) for r in results])} stores"
        ]
        
        # Insights
        if len(results) > 1:
            disparity = (max(sales_list) - min(sales_list)) / statistics.mean(sales_list)
            interpretation["insights"].append(
                f"High regional disparity: {disparity:.1f}x difference between best and worst regions suggests market maturity differences"
            )
        
        # Recommendations
        interpretation["recommendations"] = [
            f"Invest in expansion in underperforming regions - growth opportunity",
            f"Analyze {top_region.get('region')} strategy for best practices replication",
            f"Localize promotions by region considering cultural/demographic factors"
        ]
        
        interpretation["visualization"] = {
            "type": "pie",
            "title": "Sales Distribution by Region",
            "data": results
        }
    
    def _interpret_stockout_analysis(self, results: List[Dict], interpretation: Dict):
        """Interpret stockout analysis."""
        if not results:
            interpretation["summary"] = "No stockouts detected in the analyzed period - excellent inventory management."
            return
        
        interpretation["summary"] = (
            f"Critical: {len(results)} products experienced stockouts across various regions. "
            f"This represents potential lost sales opportunities and customer dissatisfaction."
        )
        
        # Metrics
        total_lost_sales = sum([r.get("lost_sales", 0) for r in results])
        interpretation["metrics"] = {
            "products_with_stockout": len(results),
            "estimated_lost_sales": total_lost_sales,
            "total_stockout_incidents": sum([r.get("stockout_count", 0) for r in results])
        }
        
        # Key findings
        interpretation["key_findings"] = [
            f"Critical stockout products: {', '.join([r.get('product_name', 'Unknown')[:20] for r in results[:3]])}...",
            f"Estimated lost sales: ${total_lost_sales:,.2f}",
            f"Affected regions: {len(set([r.get('region') for r in results]))} regions"
        ]
        
        # Insights
        interpretation["insights"] = [
            "Stockouts indicate supply chain issues - immediate action needed",
            f"High-demand products {' and '.join([r.get('product_name', 'Unknown') for r in results[:2]])} need increased inventory",
            "Regional differences in stockouts suggest logistics optimization opportunities"
        ]
        
        # Recommendations (URGENT)
        interpretation["recommendations"] = [
            "⚠️  URGENT: Increase safety stock for identified products",
            f"Accelerate replenishment for {results[0].get('product_name', 'top product')}",
            "Review supplier performance and lead times",
            "Implement demand forecasting to prevent future stockouts"
        ]
        
        interpretation["visualization"] = {
            "type": "bar",
            "x_axis": "product_name",
            "y_axis": "stockout_count",
            "title": "Stockout Incidents by Product",
            "alert": True,
            "data": results[:10]
        }
    
    def _interpret_product_performance(self, results: List[Dict], interpretation: Dict):
        """Interpret product performance."""
        if not results:
            return
        
        top_product = results[0]
        interpretation["summary"] = (
            f"Product performance analysis reveals {top_product.get('product_name', 'Top product')} "
            f"as the leader with ${top_product.get('total_sales', 0):,.2f} in sales. "
            f"Performance varies significantly across {len(results)} products."
        )
        
        # Metrics
        interpretation["metrics"] = {
            "total_products": len(results),
            "total_sales": sum([r.get("total_sales", 0) for r in results]),
            "total_units_sold": sum([r.get("total_units", 0) for r in results]),
            "average_price": statistics.mean([r.get("avg_price", 0) for r in results if r.get("avg_price")]),
        }
        
        # Key findings by category if available
        categories = set([r.get("category") for r in results if r.get("category")])
        interpretation["key_findings"] = [
            f"Top product: {top_product.get('product_name')} ({top_product.get('brand')})",
            f"Categories represented: {', '.join(categories)}" if categories else "Multiple categories",
            f"Price range: ${min([r.get('avg_price', 0) for r in results]):.2f} - ${max([r.get('avg_price', 0) for r in results]):.2f}"
        ]
        
        # Insights
        interpretation["insights"] = [
            f"{top_product.get('product_name')} drives significant revenue - protect market position",
            "Portfolio diversification present but some products underperform",
            "Premium products show strong margins despite lower volumes"
        ]
        
        interpretation["recommendations"] = [
            f"Expand distribution for top performer {top_product.get('product_name')}",
            "Evaluate bottom performers - consider discontinuation or repositioning",
            "Cross-sell high-margin with high-volume products"
        ]
        
        interpretation["visualization"] = {
            "type": "scatter",
            "x_axis": "total_units",
            "y_axis": "total_margin",
            "size_axis": "total_sales",
            "title": "Product Portfolio Analysis",
            "data": results[:20]
        }
    
    def _interpret_inventory_analysis(self, results: List[Dict], interpretation: Dict):
        """Interpret inventory analysis."""
        if not results:
            return
        
        # Calculate average inventory turn
        turns = [r.get("inventory_turn") for r in results if r.get("inventory_turn")]
        avg_turn = statistics.mean(turns) if turns else 0
        
        interpretation["summary"] = (
            f"Inventory analysis across {len(results)} product-week combinations shows "
            f"average inventory turn of {avg_turn:.2f}. Inventory management effectiveness varies by product."
        )
        
        # Metrics
        interpretation["metrics"] = {
            "avg_inventory_turn": avg_turn,
            "total_products_analyzed": len(set([r.get("product_id") for r in results])),
            "weeks_analyzed": len(set([r.get("week_start") for r in results]))
        }
        
        # Key findings
        high_turn = [r for r in results if r.get("inventory_turn", 0) > avg_turn * 1.5]
        low_turn = [r for r in results if r.get("inventory_turn", 0) < avg_turn * 0.5]
        
        interpretation["key_findings"] = [
            f"High-turn products ({len(high_turn)}): Fast-moving inventory, sales-driven",
            f"Low-turn products ({len(low_turn)}): Slow-moving, requires management",
            f"Average turn ratio: {avg_turn:.2f}x"
        ]
        
        interpretation["recommendations"] = [
            "High-turn products: Ensure continuous supply to avoid stockouts",
            f"Low-turn products: Review demand forecasts and reduce safety stock",
            "Optimize warehouse layout based on turn rates"
        ]
        
        interpretation["visualization"] = {
            "type": "box_plot",
            "y_axis": "inventory_turn",
            "title": "Inventory Turnover Distribution",
            "data": results
        }
    
    def _interpret_campaign_impact(self, results: List[Dict], interpretation: Dict):
        """Interpret campaign impact analysis."""
        if not results:
            return
        
        # Find campaign vs non-campaign
        campaign_results = [r for r in results if r.get("promo_active")]
        non_campaign = [r for r in results if not r.get("promo_active")]
        
        campaign_sales = sum([r.get("sales_value", 0) for r in campaign_results])
        non_campaign_sales = sum([r.get("sales_value", 0) for r in non_campaign])
        
        lift = ((campaign_sales - non_campaign_sales) / non_campaign_sales * 100) if non_campaign_sales > 0 else 0
        
        interpretation["summary"] = (
            f"Campaign impact analysis shows {lift:+.1f}% sales lift during promotion periods. "
            f"Campaign sales: ${campaign_sales:,.2f} vs non-campaign: ${non_campaign_sales:,.2f}"
        )
        
        interpretation["metrics"] = {
            "campaign_sales": campaign_sales,
            "non_campaign_sales": non_campaign_sales,
            "sales_lift_pct": lift,
            "campaign_weeks": len(campaign_results),
            "non_campaign_weeks": len(non_campaign)
        }
        
        interpretation["insights"] = [
            f"Campaign driving {lift:+.1f}% lift indicates strong promotional effectiveness",
            f"Average campaign discount: {statistics.mean([r.get('avg_discount', 0) for r in campaign_results if r.get('avg_discount')]):.1f}%",
            "Campaign timing and execution are critical factors in product success"
        ]
        
        interpretation["recommendations"] = [
            f"Continue campaigns - {lift:.0f}% lift justifies promotional investment",
            "Optimize discount levels - test lower discounts to maximize margin",
            "Extend campaign duration where ROI remains positive"
        ]
        
        interpretation["visualization"] = {
            "type": "line",
            "x_axis": "week_start",
            "y_axis": "sales_value",
            "group_by": "promo_active",
            "title": "Campaign Impact Over Time",
            "data": results
        }
    
    def _interpret_generic(self, results: List[Dict], interpretation: Dict):
        """Generic interpretation for unknown intents."""
        interpretation["summary"] = f"Query returned {len(results)} results with {len(results[0]) if results else 0} columns."
        
        # Basic statistics
        if results and isinstance(results[0], dict):
            numeric_cols = {}
            for key in results[0].keys():
                values = [r.get(key) for r in results if isinstance(r.get(key), (int, float))]
                if values:
                    numeric_cols[key] = {
                        "avg": statistics.mean(values),
                        "min": min(values),
                        "max": max(values),
                        "count": len(values)
                    }
            
            interpretation["metrics"] = numeric_cols
            interpretation["key_findings"] = [
                f"Analyzed {len(results)} records",
                f"Found {len(numeric_cols)} numeric columns",
                "Results available for further analysis"
            ]
