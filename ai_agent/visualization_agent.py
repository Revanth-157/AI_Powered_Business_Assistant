"""
Visualization Agent - generates chart specifications from analytics data.
"""
from datetime import datetime
from typing import List, Dict, Any
from .schema import AgentState, VisualizationSpec


class VisualizationAgent:
    """
    Chooses appropriate chart types and generates visualization metadata.
    """
    
    def __init__(self):
        pass
    
    def process(self, state: AgentState) -> AgentState:
        """Generate visualization specifications."""
        try:
            if not state.analytics_output:
                state.error_messages.append("No analytics data for visualization.")
                return state
            
            visualizations = []
            
            # Generate time series chart if available
            if state.analytics_output.time_series:
                viz = self._create_time_series_chart(state.analytics_output.time_series)
                if viz:
                    visualizations.append(viz)
            
            # Generate aggregation charts (by region, category)
            if state.analytics_output.aggregations:
                viz = self._create_aggregation_chart(state.analytics_output.aggregations)
                if viz:
                    visualizations.append(viz)
            
            # Generate KPI card data
            if state.analytics_output.kpis:
                viz = self._create_kpi_cards(state.analytics_output.kpis)
                if viz:
                    visualizations.append(viz)
            
            state.visualizations = visualizations
            state.response_data["visualizations"] = [
                {
                    "chart_type": v.chart_type,
                    "title": v.title,
                    "data_points": len(v.data),
                    "annotations": v.annotations
                }
                for v in visualizations
            ]
            state.updated_at = datetime.utcnow()
            return state
        
        except Exception as e:
            state.error_messages.append(f"Visualization Generation Error: {str(e)}")
            return state
    
    def _create_time_series_chart(self, time_series: List[Dict[str, Any]]) -> VisualizationSpec:
        """Create a line chart for time series data."""
        if not time_series:
            return None
        
        # Determine best metric to plot
        sample = time_series[0]
        y_metric = "total_sales" if "total_sales" in sample else "total_units"
        
        spec = VisualizationSpec(
            chart_type="line",
            title="Sales Trend Over Time",
            data=time_series,
            axes={
                "x": "week_start",
                "y": y_metric
            },
            annotations=[
                "Data aggregated by week",
                f"Y-axis: {y_metric.replace('_', ' ').title()}"
            ]
        )
        
        # Add Vega-Lite spec
        spec.vega_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": "Sales trend over time",
            "data": {"values": time_series},
            "mark": "line",
            "encoding": {
                "x": {"field": "week_start", "type": "temporal", "title": "Week"},
                "y": {"field": y_metric, "type": "quantitative", "title": y_metric.replace('_', ' ').title()}
            }
        }
        
        return spec
    
    def _create_aggregation_chart(self, aggregations: List[Dict[str, Any]]) -> VisualizationSpec:
        """Create a bar chart for aggregations by dimension."""
        if not aggregations:
            return None
        
        # Separate by dimension
        dimensions = {}
        for agg in aggregations:
            dim = agg.get("dimension", "unknown")
            if dim not in dimensions:
                dimensions[dim] = []
            dimensions[dim].append(agg)
        
        # Use first dimension found
        first_dim = list(dimensions.keys())[0]
        data = dimensions[first_dim]
        
        spec = VisualizationSpec(
            chart_type="bar",
            title=f"Sales by {first_dim.title()}",
            data=data,
            axes={
                "x": "value",
                "y": "total_sales"
            },
            annotations=[
                f"Aggregated by {first_dim}",
                "Values sorted by sales"
            ]
        )
        
        # Add Vega-Lite spec
        spec.vega_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": f"Sales by {first_dim}",
            "data": {"values": data},
            "mark": "bar",
            "encoding": {
                "x": {"field": "value", "type": "nominal", "title": first_dim.title()},
                "y": {"field": "total_sales", "type": "quantitative", "title": "Total Sales"},
                "color": {"field": "value", "type": "nominal"}
            }
        }
        
        return spec
    
    def _create_kpi_cards(self, kpis: List[Any]) -> VisualizationSpec:
        """Create KPI card data structure."""
        data = [
            {
                "metric": kpi.metric_name,
                "value": kpi.value,
                "unit": kpi.unit,
                "provenance": kpi.provenance
            }
            for kpi in kpis
        ]
        
        spec = VisualizationSpec(
            chart_type="kpi_cards",
            title="Key Performance Indicators",
            data=data,
            axes={},
            annotations=[
                "Executive summary KPIs",
                "Click for drill-down"
            ]
        )
        
        return spec
