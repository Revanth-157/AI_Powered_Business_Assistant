"""
Database schema extraction for Text-to-SQL engine.
"""
from typing import Dict, List, Optional
from sqlalchemy import inspect, MetaData, text
from sqlalchemy.orm import Session
import logging
import json

logger = logging.getLogger(__name__)


class SchemaExtractor:
    """Extract and cache database schema information."""
    
    def __init__(self, db_session: Session):
        """Initialize schema extractor with database session."""
        self.db = db_session
        self._schema_cache = None
        self._table_descriptions = {
            "products": "Product master data with name, brand, category, price",
            "stores": "Store locations with region, channel, format",
            "sales_promotions": "Sales and promotion data by week, store, product",
            "inventory": "Inventory levels and movement data",
            "users": "User accounts and roles",
            "chat_history": "Chat conversation history",
            "generated_reports": "Generated reports and their data"
        }
        self._column_descriptions = {
            "sales_promotions": {
                "promo_active": "Boolean flag if promotion was active",
                "discount_pct": "Discount percentage applied",
                "stockout": "Boolean flag if product stockout occurred",
                "sales_value": "Total sales revenue",
                "units_sold": "Number of units sold",
                "gross_margin": "Profit margin"
            },
            "inventory": {
                "opening_qty": "Starting inventory quantity",
                "received_qty": "Quantity received in period",
                "sold_qty": "Quantity sold",
                "closing_qty": "Ending inventory quantity",
                "shrinkage_qty": "Loss/shrinkage quantity"
            }
        }
    
    def get_schema(self) -> Dict[str, any]:
        """
        Get complete database schema with tables, columns, and types.
        Includes table and column descriptions for better SQL generation.
        """
        if self._schema_cache is not None:
            return self._schema_cache
        
        try:
            inspector = inspect(self.db.get_bind())
            tables = inspector.get_table_names()
            
            schema_dict = {}
            for table_name in tables:
                columns = inspector.get_columns(table_name)
                pk = inspector.get_pk_constraint(table_name)
                fk = inspector.get_foreign_keys(table_name)
                indexes = inspector.get_indexes(table_name)
                
                schema_dict[table_name] = {
                    "description": self._table_descriptions.get(table_name, f"Table: {table_name}"),
                    "columns": [
                        {
                            "name": col["name"],
                            "type": str(col["type"]),
                            "nullable": col.get("nullable", True),
                            "description": self._get_column_description(table_name, col["name"])
                        }
                        for col in columns
                    ],
                    "primary_key": pk.get("constrained_columns", []) if pk else [],
                    "foreign_keys": [
                        {
                            "column": fk_item["constrained_columns"],
                            "references": f"{fk_item['referred_table']}.{fk_item['referred_columns']}"
                        }
                        for fk_item in fk
                    ],
                    "indexes": indexes
                }
            
            self._schema_cache = schema_dict
            logger.info(f"Extracted schema for {len(tables)} tables")
            return schema_dict
            
        except Exception as e:
            logger.error(f"Failed to extract schema: {str(e)}")
            return {}
    
    def _get_column_description(self, table_name: str, column_name: str) -> str:
        """Get description for a column."""
        if table_name in self._column_descriptions:
            return self._column_descriptions[table_name].get(column_name, "")
        return ""
    
    def get_schema_as_string(self, include_sample_queries: bool = True) -> str:
        """
        Get schema as formatted string for LLM context.
        Useful for prompt engineering.
        """
        schema = self.get_schema()
        
        if not schema:
            return "No schema available"
        
        lines = ["DATABASE SCHEMA:", "=" * 50]
        
        for table_name, table_info in schema.items():
            lines.append(f"\nTABLE: {table_name}")
            lines.append(f"Description: {table_info['description']}")
            
            lines.append("\nColumns:")
            for col in table_info["columns"]:
                nullable = "NULL" if col["nullable"] else "NOT NULL"
                desc = f" - {col['description']}" if col["description"] else ""
                lines.append(f"  - {col['name']}: {col['type']} {nullable}{desc}")
            
            if table_info["primary_key"]:
                lines.append(f"Primary Key: {', '.join(table_info['primary_key'])}")
            
            if table_info["foreign_keys"]:
                lines.append("Foreign Keys:")
                for fk in table_info["foreign_keys"]:
                    lines.append(f"  - {fk['column']} → {fk['references']}")
        
        if include_sample_queries:
            lines.extend([
                "\n" + "=" * 50,
                "SAMPLE QUERIES:",
                "=" * 50,
                "\n1. Which promotion performed best last month?",
                "   SELECT product_id, SUM(sales_value) as total_sales",
                "   FROM sales_promotions WHERE promo_active = true AND week_start >= CURRENT_DATE - INTERVAL '30 days'",
                "   GROUP BY product_id ORDER BY total_sales DESC;",
                "\n2. Compare North vs South region sales:",
                "   SELECT region, SUM(sales_value) as total_sales",
                "   FROM sales_promotions sp JOIN stores s ON sp.store_id = s.store_id",
                "   WHERE region IN ('North', 'South')",
                "   GROUP BY region;",
                "\n3. Which products experienced stockouts?",
                "   SELECT DISTINCT product_id FROM sales_promotions WHERE stockout = true;",
                "\n4. Inventory turnover by product:",
                "   SELECT product_id, AVG(sold_qty) as avg_sold",
                "   FROM inventory GROUP BY product_id ORDER BY avg_sold DESC;"
            ])
        
        return "\n".join(lines)
    
    def get_available_tables(self) -> List[str]:
        """Get list of available tables."""
        schema = self.get_schema()
        return list(schema.keys())
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, str]]:
        """Get columns for a specific table."""
        schema = self.get_schema()
        if table_name in schema:
            return schema[table_name]["columns"]
        return []
    
    def validate_table_exists(self, table_name: str) -> bool:
        """Check if table exists in schema."""
        schema = self.get_schema()
        return table_name in schema
