"""
SQL generation from natural language using LangChain.
"""
from typing import Dict, Tuple, Optional
from sqlalchemy.orm import Session
import logging
import re

logger = logging.getLogger(__name__)


class SQLGenerator:
    """Generate SQL from natural language using prompts and LLM."""
    
    def __init__(self, db_session: Session, schema_extractor):
        """Initialize SQL generator."""
        self.db = db_session
        self.schema = schema_extractor
        self.llm = None  # Will be initialized if LangChain/LLM is available
    
    def generate_sql(self, user_query: str, use_llm: bool = False) -> Tuple[str, Dict]:
        """
        Generate SQL from natural language query.
        
        Args:
            user_query: Natural language question
            use_llm: Whether to use LLM (if available)
        
        Returns:
            Tuple of (SQL query, metadata with confidence/method)
        """
        metadata = {
            "method": "rule-based",
            "confidence": 0.0,
            "intent": None,
            "tables": []
        }
        
        # First try rule-based generation for common patterns
        sql, meta = self._try_rule_based(user_query)
        if sql:
            metadata.update(meta)
            return sql, metadata
        
        # Fall back to LLM-based if available
        if use_llm:
            sql, meta = self._try_llm_based(user_query)
            if sql:
                metadata.update(meta)
                return sql, metadata
        
        logger.warning(f"Failed to generate SQL for: {user_query}")
        metadata["error"] = "Could not generate SQL from query"
        return "", metadata
    
    def _try_rule_based(self, query: str) -> Tuple[str, Dict]:
        """
        Try to generate SQL using rule-based patterns.
        Covers common FMCG analytics queries.
        """
        query_lower = query.lower()
        metadata = {"method": "rule-based", "confidence": 0.8}
        
        # Pattern 1: Promotion performance
        if any(phrase in query_lower for phrase in ["promotion", "promo", "performed", "perform", "best promo", "top promo", "effective"]):
            if any(word in query_lower for word in ["promotion", "promo", "campaign"]):
                timeframe = self._extract_timeframe(query)
                sql = f"""
                SELECT 
                    p.product_id, p.product_name, p.brand,
                    SUM(sp.sales_value) as total_sales,
                    SUM(sp.units_sold) as total_units,
                    AVG(sp.discount_pct) as avg_discount,
                    COUNT(*) as promo_weeks
                FROM sales_promotions sp
                JOIN products p ON sp.product_id = p.product_id
                WHERE sp.promo_active = true {timeframe}
                GROUP BY p.product_id, p.product_name, p.brand
                ORDER BY total_sales DESC
                LIMIT 10
                """
                metadata["intent"] = "PROMO_PERFORMANCE"
                metadata["tables"] = ["sales_promotions", "products"]
                return sql, metadata
        
        # Pattern 2: Regional sales comparison
        if any(phrase in query_lower for phrase in ["region", "north", "south", "east", "west", "compare region"]):
            timeframe = self._extract_timeframe(query)
            sql = f"""
            SELECT 
                s.region,
                SUM(sp.sales_value) as total_sales,
                SUM(sp.units_sold) as total_units,
                AVG(sp.discount_pct) as avg_discount,
                COUNT(DISTINCT sp.store_id) as store_count
            FROM sales_promotions sp
            JOIN stores s ON sp.store_id = s.store_id
            WHERE 1=1 {timeframe}
            GROUP BY s.region
            ORDER BY total_sales DESC
            """
            metadata["intent"] = "REGIONAL_SALES"
            metadata["tables"] = ["sales_promotions", "stores"]
            return sql, metadata
        
        # Pattern 3: Stockout detection
        if any(phrase in query_lower for phrase in ["stockout", "stock out", "out of stock", "unavailable"]):
            timeframe = self._extract_timeframe(query)
            sql = f"""
            SELECT 
                p.product_id, p.product_name, p.brand,
                s.region,
                COUNT(*) as stockout_count,
                SUM(sp.units_sold) as lost_sales
            FROM sales_promotions sp
            JOIN products p ON sp.product_id = p.product_id
            JOIN stores s ON sp.store_id = s.store_id
            WHERE sp.stockout = true {timeframe}
            GROUP BY p.product_id, p.product_name, p.brand, s.region
            ORDER BY stockout_count DESC
            """
            metadata["intent"] = "STOCKOUT_ANALYSIS"
            metadata["tables"] = ["sales_promotions", "products", "stores"]
            return sql, metadata
        
        # Pattern 4: Product performance
        if any(phrase in query_lower for phrase in ["product performance", "top product", "best product", "product sales"]):
            timeframe = self._extract_timeframe(query)
            sql = f"""
            SELECT 
                p.product_id, p.product_name, p.brand, p.category,
                SUM(sp.sales_value) as total_sales,
                SUM(sp.units_sold) as total_units,
                AVG(sp.unit_price) as avg_price,
                SUM(sp.gross_margin) as total_margin
            FROM sales_promotions sp
            JOIN products p ON sp.product_id = p.product_id
            WHERE 1=1 {timeframe}
            GROUP BY p.product_id, p.product_name, p.brand, p.category
            ORDER BY total_sales DESC
            LIMIT 10
            """
            metadata["intent"] = "PRODUCT_PERFORMANCE"
            metadata["tables"] = ["sales_promotions", "products"]
            return sql, metadata
        
        # Pattern 5: Inventory turnover
        if any(phrase in query_lower for phrase in ["inventory", "turn", "stock level", "inventory movement"]):
            sql = """
            SELECT 
                p.product_id, p.product_name,
                i.week_start,
                i.opening_qty, i.received_qty, i.sold_qty, i.closing_qty,
                CASE WHEN (i.opening_qty + i.received_qty) > 0 
                     THEN ROUND((i.sold_qty::numeric / ((i.opening_qty + i.received_qty) / 2.0))::numeric, 2)
                     ELSE NULL 
                END as inventory_turn
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            ORDER BY i.week_start DESC, p.product_name
            LIMIT 50
            """
            metadata["intent"] = "INVENTORY_ANALYSIS"
            metadata["tables"] = ["inventory", "products"]
            return sql, metadata
        
        # Pattern 6: Campaign impact
        if any(phrase in query_lower for phrase in ["campaign", "impact", "effect", "lift"]):
            product_name = self._extract_product_name(query)
            if product_name:
                sql = f"""
                SELECT 
                    sp.week_start,
                    sp.promo_active,
                    SUM(sp.sales_value) as sales_value,
                    SUM(sp.units_sold) as units_sold,
                    AVG(sp.discount_pct) as avg_discount,
                    AVG(sp.unit_price) as avg_price
                FROM sales_promotions sp
                JOIN products p ON sp.product_id = p.product_id
                WHERE LOWER(p.product_name) LIKE '%{product_name}%'
                GROUP BY sp.week_start, sp.promo_active
                ORDER BY sp.week_start DESC
                """
                metadata["intent"] = "CAMPAIGN_IMPACT"
                metadata["tables"] = ["sales_promotions", "products"]
                return sql, metadata
        
        return "", metadata
    
    def _try_llm_based(self, query: str) -> Tuple[str, Dict]:
        """
        Try to generate SQL using LLM (LangChain).
        Currently returns empty - would require LangChain setup.
        """
        try:
            # This would require langchain and an LLM API key
            # For now, this is a placeholder
            logger.debug("LLM-based generation not yet implemented")
            return "", {"method": "llm-based", "confidence": 0.0, "error": "LLM not configured"}
        except Exception as e:
            logger.error(f"LLM-based generation failed: {str(e)}")
            return "", {"method": "llm-based", "confidence": 0.0, "error": str(e)}
    
    def _extract_timeframe(self, query: str) -> str:
        """Extract timeframe constraint from query."""
        query_lower = query.lower()
        
        # Map timeframe patterns to SQL
        timeframe_patterns = {
            r'\blast\s+month': "AND sp.week_start >= CURRENT_DATE - INTERVAL '30 days'",
            r'\blast\s+week': "AND sp.week_start >= CURRENT_DATE - INTERVAL '7 days'",
            r'\blast\s+quarter': "AND sp.week_start >= CURRENT_DATE - INTERVAL '90 days'",
            r'\blast\s+year': "AND sp.week_start >= CURRENT_DATE - INTERVAL '365 days'",
            r'\bthis\s+month': "AND EXTRACT(MONTH FROM sp.week_start) = EXTRACT(MONTH FROM CURRENT_DATE)",
            r'\bthis\s+year': "AND EXTRACT(YEAR FROM sp.week_start) = EXTRACT(YEAR FROM CURRENT_DATE)",
        }
        
        for pattern, sql_constraint in timeframe_patterns.items():
            if re.search(pattern, query_lower):
                return sql_constraint
        
        return ""  # Default: no time constraint
    
    def _extract_product_name(self, query: str) -> Optional[str]:
        """Extract product name from query."""
        # Common FMCG product patterns
        products = ["spark", "lemon water", "juice", "beverage", "water", "drink", "soda"]
        query_lower = query.lower()
        
        for product in products:
            if product in query_lower:
                return product
        
        # Try to extract quoted product names
        import re
        match = re.search(r"['\"]([^'\"]+)['\"]", query)
        if match:
            return match.group(1)
        
        return None
