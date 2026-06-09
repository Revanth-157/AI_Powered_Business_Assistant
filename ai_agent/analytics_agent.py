"""
Analytics Agent - executes safe SQL queries and computes KPIs.
"""
import sqlite3
from typing import List, Dict, Any
from datetime import datetime
from .schema import (
    AgentState, AnalyticsOutput, KPIResult
)


class AnalyticsAgent:
    """
    Executes SQL queries against the database and computes derived KPIs.
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "architecture/fmcg_analytics.db"
    
    def process(self, state: AgentState) -> AgentState:
        """Execute SQL query and compute KPIs."""
        try:
            if not state.sql_query:
                state.error_messages.append("No SQL query provided.")
                return state
            
            if not state.sql_query.safe:
                state.error_messages.append("SQL query failed validation.")
                return state
            
            # Execute query
            results = self._execute_query(state.sql_query.text, state.sql_query.params)
            
            if not results:
                state.error_messages.append("Query returned no results.")
                state.analytics_output = AnalyticsOutput(
                    kpis=[],
                    error="No data available for the query."
                )
                return state
            
            # Extract KPIs from results
            kpis = self._extract_kpis(results, state)
            
            # Create analytics output
            analytics_output = AnalyticsOutput(
                kpis=kpis,
                raw_data=results if len(results) <= 100 else results[:100],
                time_series=self._aggregate_time_series(results),
                aggregations=self._compute_aggregations(results),
            )
            
            state.analytics_output = analytics_output
            state.response_data["kpis"] = [
                {
                    "name": kpi.metric_name,
                    "value": kpi.value,
                    "unit": kpi.unit,
                    "dimensions": kpi.dimensions
                }
                for kpi in kpis
            ]
            state.updated_at = datetime.utcnow()
            return state
        
        except Exception as e:
            state.error_messages.append(f"Analytics Execution Error: {str(e)}")
            state.analytics_output = AnalyticsOutput(
                kpis=[],
                error=str(e)
            )
            return state
    
    def _execute_query(self, sql_text: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute SQL query against SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Convert named parameters to SQLite format
            cursor.execute(sql_text, params)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            return results
        finally:
            conn.close()
    
    def _extract_kpis(self, results: List[Dict[str, Any]], state: AgentState) -> List[KPIResult]:
        """Extract KPIs from query results."""
        kpis = []
        
        if not results:
            return kpis
        
        # Aggregate first row for scalar KPIs
        first_row = results[0]
        
        # Revenue KPI
        if "total_sales" in first_row:
            kpis.append(KPIResult(
                metric_name="Total Revenue",
                value=float(first_row.get("total_sales", 0)),
                unit="$",
                timestamp=datetime.utcnow(),
                provenance="sum of sales_value"
            ))
        
        # Units sold KPI
        if "total_units" in first_row:
            kpis.append(KPIResult(
                metric_name="Total Units Sold",
                value=float(first_row.get("total_units", 0)),
                unit="units",
                timestamp=datetime.utcnow(),
                provenance="sum of units_sold"
            ))
        
        # Margin KPI
        if "total_margin" in first_row:
            kpis.append(KPIResult(
                metric_name="Total Gross Margin",
                value=float(first_row.get("total_margin", 0)),
                unit="$",
                timestamp=datetime.utcnow(),
                provenance="sum of gross_margin"
            ))
        
        # Average discount
        if "avg_discount" in first_row:
            kpis.append(KPIResult(
                metric_name="Average Discount %",
                value=float(first_row.get("avg_discount", 0)),
                unit="%",
                timestamp=datetime.utcnow(),
                provenance="average of discount_pct"
            ))
        
        # Promotional units
        if "promo_units" in first_row:
            kpis.append(KPIResult(
                metric_name="Promotional Units",
                value=float(first_row.get("promo_units", 0)),
                unit="units",
                timestamp=datetime.utcnow(),
                provenance="sum of units_sold where promo_active=1"
            ))
        
        # Inventory turn
        if "inventory_turn" in first_row:
            kpis.append(KPIResult(
                metric_name="Inventory Turnover",
                value=float(first_row.get("inventory_turn", 0)),
                unit="turns",
                timestamp=datetime.utcnow(),
                provenance="sold_qty / avg_inventory"
            ))
        
        # Store count
        if "store_count" in first_row:
            kpis.append(KPIResult(
                metric_name="Active Stores",
                value=float(first_row.get("store_count", 0)),
                unit="count",
                timestamp=datetime.utcnow(),
                provenance="count of distinct store_id"
            ))
        
        return kpis
    
    def _aggregate_time_series(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate results into time series."""
        if not results:
            return []
        
        # Group by week_start if available
        time_groups = {}
        for row in results:
            if "week_start" in row:
                week = row["week_start"]
                if week not in time_groups:
                    time_groups[week] = {
                        "week_start": week,
                        "total_units": 0,
                        "total_sales": 0,
                        "count": 0
                    }
                
                time_groups[week]["total_units"] += float(row.get("total_units", 0))
                time_groups[week]["total_sales"] += float(row.get("total_sales", 0))
                time_groups[week]["count"] += 1
        
        return list(time_groups.values())
    
    def _compute_aggregations(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compute aggregations by dimension (region, category, etc.)."""
        if not results:
            return []
        
        aggregations = []
        
        # Aggregate by region
        region_groups = {}
        for row in results:
            if "region" in row:
                region = row["region"]
                if region not in region_groups:
                    region_groups[region] = {
                        "dimension": "region",
                        "value": region,
                        "total_units": 0,
                        "total_sales": 0
                    }
                region_groups[region]["total_units"] += float(row.get("total_units", 0))
                region_groups[region]["total_sales"] += float(row.get("total_sales", 0))
        
        aggregations.extend(region_groups.values())
        
        # Aggregate by category
        category_groups = {}
        for row in results:
            if "category" in row:
                category = row["category"]
                if category not in category_groups:
                    category_groups[category] = {
                        "dimension": "category",
                        "value": category,
                        "total_units": 0,
                        "total_sales": 0
                    }
                category_groups[category]["total_units"] += float(row.get("total_units", 0))
                category_groups[category]["total_sales"] += float(row.get("total_sales", 0))
        
        aggregations.extend(category_groups.values())
        
        return aggregations
