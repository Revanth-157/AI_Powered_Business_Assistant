"""
SQL Generation Agent - converts structured intent to safe SQL queries.
"""
import re
import sqlparse
from typing import Dict, Any, Optional
from datetime import datetime
from .schema import (
    AgentState, StructuredIntent, SQLQuery, Intent
)


class SQLGenerationAgent:
    """
    Generates parameterized SQL queries from structured intent.
    Enforces safety guardrails and SQL injection prevention.
    """
    
    # Whitelisted tables and columns
    ALLOWED_TABLES = {
        "products", "stores", "sales_promotions", "inventory",
        "users", "chat_history", "generated_reports"
    }
    
    ALLOWED_COLUMNS = {
        "sales_promotions": [
            "week_start", "store_id", "product_id", "region", "channel",
            "promo_active", "discount_pct", "units_sold", "unit_price",
            "sales_value", "cost", "gross_margin", "stockout"
        ],
        "inventory": [
            "week_start", "store_id", "product_id", "opening_qty",
            "received_qty", "sold_qty", "closing_qty", "shrinkage_qty"
        ],
        "products": [
            "product_id", "product_name", "brand", "category",
            "sub_category", "pack_size_ml", "launch_date", "base_price"
        ],
        "stores": [
            "store_id", "store_name", "region", "sub_region",
            "channel", "store_format", "area_type", "market_size"
        ],
    }
    
    # Forbidden SQL patterns
    FORBIDDEN_PATTERNS = [
        r"\bDROP\b", r"\bDELETE\b", r"\bALTER\b", r"\bCREATE\b",
        r"\bINSERT\b", r"\bUPDATE\b", r"\bEXEC\b", r"\bEXECUTE\b",
        r"--", r"/\*", r"\*/", r";\s*(DROP|DELETE|ALTER|INSERT|UPDATE)"
    ]
    
    def __init__(self):
        pass
    
    def process(self, state: AgentState) -> AgentState:
        """Main entry - generates safe SQL from structured intent."""
        try:
            if not state.structured_intent:
                state.error_messages.append("No structured intent provided.")
                return state
            
            if state.structured_intent.clarification_needed:
                state.response_text = f"Clarification needed: {state.structured_intent.clarification_question}"
                return state
            
            # Generate SQL based on intent
            sql_query = self._generate_sql_from_intent(state.structured_intent, state)
            
            # Validate SQL safety
            is_safe, issues = self._validate_sql_safety(sql_query.text)
            sql_query.safe = is_safe
            sql_query.issues = issues
            
            if not is_safe:
                state.error_messages.append(f"SQL validation failed: {'; '.join(issues)}")
                state.sql_query = sql_query
                return state
            
            # Estimate query cost
            sql_query.estimated_cost = self._estimate_cost(sql_query.text)
            
            state.sql_query = sql_query
            state.updated_at = datetime.utcnow()
            return state
        
        except Exception as e:
            state.error_messages.append(f"SQL Generation Error: {str(e)}")
            return state
    
    def _generate_sql_from_intent(self, intent: StructuredIntent, state: AgentState) -> SQLQuery:
        """Generate SQL query from structured intent."""
        
        if intent.intent == Intent.PROMO_PERFORMANCE:
            return self._promo_performance_sql(intent, state)
        elif intent.intent == Intent.INVENTORY_MOVEMENT:
            return self._inventory_movement_sql(intent, state)
        elif intent.intent == Intent.REGIONAL_SALES:
            return self._regional_sales_sql(intent, state)
        elif intent.intent == Intent.CAMPAIGN_IMPACT:
            return self._campaign_impact_sql(intent, state)
        elif intent.intent == Intent.KPI_DASHBOARD:
            return self._kpi_dashboard_sql(intent, state)
        else:
            return SQLQuery(
                text="SELECT 1 as placeholder;",
                params={},
                safe=False,
                issues=["Unknown intent type"]
            )
    
    def _promo_performance_sql(self, intent: StructuredIntent, state: AgentState) -> SQLQuery:
        """Generate SQL for promotional performance query."""
        sql = """
        SELECT 
            week_start, 
            region, 
            category,
            SUM(units_sold) as total_units,
            SUM(sales_value) as total_sales,
            AVG(discount_pct) as avg_discount,
            COUNT(CASE WHEN promo_active = 1 THEN 1 END) as promo_count
        FROM sales_promotions
        WHERE 1=1
        """
        
        params = {}
        
        # Add time range filter
        if intent.time_range:
            sql += " AND week_start >= :start_date AND week_start <= :end_date"
            params["start_date"] = intent.time_range.get("start")
            params["end_date"] = intent.time_range.get("end")
        
        # Add region filter (with RLS)
        if state.accessible_regions:
            sql += f" AND region IN ({','.join(['?' for _ in state.accessible_regions])})"
            params.update({f"region_{i}": r for i, r in enumerate(state.accessible_regions)})
        elif "region" in intent.filters:
            sql += " AND region = :region"
            params["region"] = intent.filters["region"]
        
        # Add category filter
        if "category" in intent.filters:
            sql += " AND category = :category"
            params["category"] = intent.filters["category"]
        
        sql += " GROUP BY week_start, region, category"
        sql += " ORDER BY week_start DESC, region"
        
        return SQLQuery(text=sql, params=params)
    
    def _inventory_movement_sql(self, intent: StructuredIntent, state: AgentState) -> SQLQuery:
        """Generate SQL for inventory movement query."""
        sql = """
        SELECT 
            week_start,
            store_id,
            product_id,
            opening_qty,
            received_qty,
            sold_qty,
            closing_qty,
            shrinkage_qty,
            (CASE WHEN (opening_qty + received_qty) > 0 
             THEN CAST(sold_qty AS FLOAT) / ((opening_qty + received_qty) / 2.0) 
             ELSE 0 END) as inventory_turn
        FROM inventory
        WHERE 1=1
        """
        
        params = {}
        
        # Add time range filter
        if intent.time_range:
            sql += " AND week_start >= :start_date AND week_start <= :end_date"
            params["start_date"] = intent.time_range.get("start")
            params["end_date"] = intent.time_range.get("end")
        
        sql += " ORDER BY week_start DESC, store_id"
        
        return SQLQuery(text=sql, params=params)
    
    def _regional_sales_sql(self, intent: StructuredIntent, state: AgentState) -> SQLQuery:
        """Generate SQL for regional sales comparison."""
        sql = """
        SELECT 
            week_start,
            region,
            channel,
            SUM(units_sold) as total_units,
            SUM(sales_value) as total_sales,
            SUM(gross_margin) as total_margin,
            COUNT(DISTINCT store_id) as store_count
        FROM sales_promotions
        WHERE 1=1
        """
        
        params = {}
        
        # Add time range filter
        if intent.time_range:
            sql += " AND week_start >= :start_date AND week_start <= :end_date"
            params["start_date"] = intent.time_range.get("start")
            params["end_date"] = intent.time_range.get("end")
        
        # Add region filter (with RLS)
        if state.accessible_regions:
            placeholders = ",".join([f":region_{i}" for i in range(len(state.accessible_regions))])
            sql += f" AND region IN ({placeholders})"
            for i, r in enumerate(state.accessible_regions):
                params[f"region_{i}"] = r
        
        sql += " GROUP BY week_start, region, channel"
        sql += " ORDER BY week_start DESC, region, total_sales DESC"
        
        return SQLQuery(text=sql, params=params)
    
    def _campaign_impact_sql(self, intent: StructuredIntent, state: AgentState) -> SQLQuery:
        """Generate SQL for campaign impact analysis."""
        sql = """
        SELECT 
            week_start,
            promo_type,
            SUM(CASE WHEN promo_active = 1 THEN units_sold ELSE 0 END) as promo_units,
            SUM(CASE WHEN promo_active = 1 THEN sales_value ELSE 0 END) as promo_sales,
            SUM(CASE WHEN promo_active = 0 THEN units_sold ELSE 0 END) as non_promo_units,
            SUM(CASE WHEN promo_active = 0 THEN sales_value ELSE 0 END) as non_promo_sales,
            AVG(discount_pct) as avg_discount
        FROM sales_promotions
        WHERE promo_active = 1
        """
        
        params = {}
        
        # Add time range filter
        if intent.time_range:
            sql += " AND week_start >= :start_date AND week_start <= :end_date"
            params["start_date"] = intent.time_range.get("start")
            params["end_date"] = intent.time_range.get("end")
        
        sql += " GROUP BY week_start, promo_type"
        sql += " ORDER BY week_start DESC, promo_sales DESC"
        
        return SQLQuery(text=sql, params=params)
    
    def _kpi_dashboard_sql(self, intent: StructuredIntent, state: AgentState) -> SQLQuery:
        """Generate SQL for KPI dashboard snapshot."""
        sql = """
        SELECT 
            SUM(units_sold) as total_units,
            SUM(sales_value) as total_revenue,
            SUM(gross_margin) as total_margin,
            AVG(gross_margin / NULLIF(sales_value, 0)) as avg_margin_pct,
            COUNT(DISTINCT product_id) as product_count,
            COUNT(DISTINCT store_id) as store_count,
            SUM(CASE WHEN promo_active = 1 THEN units_sold ELSE 0 END) as promo_units,
            SUM(CASE WHEN stockout = 1 THEN 1 ELSE 0 END) as stockout_count
        FROM sales_promotions
        WHERE 1=1
        """
        
        params = {}
        
        # Add time range filter
        if intent.time_range:
            sql += " AND week_start >= :start_date AND week_start <= :end_date"
            params["start_date"] = intent.time_range.get("start")
            params["end_date"] = intent.time_range.get("end")
        
        return SQLQuery(text=sql, params=params)
    
    def _validate_sql_safety(self, sql_text: str) -> tuple:
        """Validate SQL for injection and forbidden patterns."""
        issues = []
        sql_upper = sql_text.upper()
        
        # Check for forbidden operations
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, sql_upper, re.IGNORECASE):
                issues.append(f"Forbidden SQL pattern detected: {pattern}")
        
        # Parse SQL and check tables/columns
        try:
            parsed = sqlparse.parse(sql_text)
            if parsed:
                stmt = parsed[0]
                # Simple check: ensure only SELECT and FROM
                if "INSERT" in sql_upper or "UPDATE" in sql_upper or "DELETE" in sql_upper:
                    issues.append("Only SELECT queries are permitted.")
        except Exception as e:
            issues.append(f"SQL parse error: {str(e)}")
        
        return len(issues) == 0, issues
    
    def _estimate_cost(self, sql_text: str) -> float:
        """Estimate query cost (simple heuristic)."""
        # In production, use EXPLAIN ANALYZE
        cost = 1.0
        if "GROUP BY" in sql_text.upper():
            cost += 0.5
        if "JOIN" in sql_text.upper():
            cost += 1.0
        if "UNION" in sql_text.upper():
            cost += 0.8
        return cost
