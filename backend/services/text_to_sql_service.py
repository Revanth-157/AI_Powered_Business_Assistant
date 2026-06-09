"""
Text-to-SQL service for the FMCG BI Assistant.
"""
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import time

from text_to_sql.schema_extractor import SchemaExtractor
from text_to_sql.sql_generator import SQLGenerator
from text_to_sql.query_validator import QueryValidator
from text_to_sql.result_interpreter import ResultInterpreter

logger = logging.getLogger(__name__)


class TextToSQLService:
    """Service for converting natural language to SQL queries and executing them."""
    
    def __init__(self, db_session: Session):
        """Initialize the Text-to-SQL service."""
        self.db = db_session
        self.schema_extractor = SchemaExtractor(db_session)
        self.sql_generator = SQLGenerator(db_session, self.schema_extractor)
        self.query_validator = QueryValidator()
        self.result_interpreter = ResultInterpreter()
        self.query_timeout_seconds = 30
    
    def process_query(self, natural_language_query: str, use_llm: bool = False) -> Dict:
        """
        Process a natural language query end-to-end.
        
        Returns:
            Dictionary with:
            - generated_sql: The SQL query generated
            - is_valid: Whether query passed validation
            - results: Query results
            - interpretation: Insights from results
            - execution_time_ms: Time to execute
            - errors: Any errors encountered
        """
        start_time = time.time()
        result = {
            "original_query": natural_language_query,
            "generated_sql": "",
            "is_valid": False,
            "validation_result": {},
            "results": [],
            "interpretation": {},
            "execution_time_ms": 0,
            "errors": []
        }
        
        try:
            # Step 1: Generate SQL from natural language
            logger.info(f"Processing query: {natural_language_query[:100]}")
            sql_query, sql_metadata = self.sql_generator.generate_sql(natural_language_query, use_llm=use_llm)
            
            if not sql_query:
                result["errors"].append("Failed to generate SQL from query")
                return result
            
            result["generated_sql"] = sql_query
            result["sql_metadata"] = sql_metadata
            
            # Step 2: Validate SQL query
            is_valid, validation_result = self.query_validator.validate(sql_query)
            result["is_valid"] = is_valid
            result["validation_result"] = validation_result
            
            if not is_valid:
                result["errors"].extend(validation_result.get("errors", []))
                logger.warning(f"Query validation failed: {validation_result['errors']}")
                return result
            
            # Step 3: Execute SQL query
            try:
                query_results = self._execute_query(sql_query)
                result["results"] = query_results
                logger.info(f"Query executed successfully, returned {len(query_results)} rows")
            except Exception as e:
                result["errors"].append(f"Query execution failed: {str(e)}")
                logger.error(f"Query execution error: {str(e)}", exc_info=True)
                return result
            
            # Step 4: Interpret results
            interpretation = self.result_interpreter.interpret(query_results, sql_metadata)
            result["interpretation"] = interpretation
            
            result["execution_time_ms"] = int((time.time() - start_time) * 1000)
            logger.info(f"Query processed successfully in {result['execution_time_ms']}ms")
            
        except Exception as e:
            result["errors"].append(f"Unexpected error: {str(e)}")
            logger.error(f"Unexpected error processing query: {str(e)}", exc_info=True)
        
        return result
    
    def _execute_query(self, sql_query: str) -> List[Dict]:
        """
        Execute SQL query and return results as list of dicts.
        """
        try:
            # Use text() to wrap raw SQL
            query_obj = text(sql_query)
            
            # Set query timeout
            self.db.connection().connection.timeout = self.query_timeout_seconds
            
            # Execute query
            result = self.db.execute(query_obj)
            
            # Fetch all results
            rows = result.fetchall()
            
            # Convert to list of dicts
            if rows:
                # Get column names
                columns = result.keys()
                results = [dict(zip(columns, row)) for row in rows]
            else:
                results = []
            
            return results
            
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def validate_query(self, sql_query: str) -> Tuple[bool, Dict]:
        """Validate a SQL query without executing it."""
        return self.query_validator.validate(sql_query)
    
    def get_schema_info(self) -> Dict:
        """Get database schema information."""
        return self.schema_extractor.get_schema()
    
    def get_schema_as_text(self) -> str:
        """Get schema as formatted text for LLM prompting."""
        return self.schema_extractor.get_schema_as_string()
    
    def get_sample_queries(self) -> List[Dict]:
        """Get sample queries for common FMCG analytics questions."""
        return [
            {
                "question": "Which promotion performed best last month?",
                "intent": "PROMO_PERFORMANCE",
                "description": "Analyze promotion effectiveness by product"
            },
            {
                "question": "Compare North vs South region sales",
                "intent": "REGIONAL_SALES",
                "description": "Compare sales metrics across regions"
            },
            {
                "question": "Which products experienced stockouts?",
                "intent": "STOCKOUT_ANALYSIS",
                "description": "Identify products with inventory issues"
            },
            {
                "question": "What was the campaign impact on Spark Lemon Water?",
                "intent": "CAMPAIGN_IMPACT",
                "description": "Analyze campaign effectiveness for specific product"
            },
            {
                "question": "Show me inventory turnover by product",
                "intent": "INVENTORY_ANALYSIS",
                "description": "Analyze inventory movement and efficiency"
            },
            {
                "question": "Top performing products this quarter",
                "intent": "PRODUCT_PERFORMANCE",
                "description": "Identify best-selling and highest-margin products"
            }
        ]
    
    def explain_query(self, sql_query: str) -> str:
        """Provide human-readable explanation of SQL query."""
        explanation_lines = [
            "QUERY EXPLANATION:",
            "=" * 50
        ]
        
        query_upper = sql_query.upper()
        
        # Extract main components
        if "SELECT" in query_upper:
            select_match = sql_query[sql_query.upper().find("SELECT"):sql_query.upper().find("FROM")]
            explanation_lines.append(f"Retrieving: {select_match.strip()}")
        
        if "FROM" in query_upper:
            from_idx = query_upper.find("FROM")
            where_idx = query_upper.find("WHERE")
            join_idx = query_upper.find("JOIN")
            group_idx = query_upper.find("GROUP BY")
            
            end_idx = min([x for x in [where_idx, join_idx, group_idx] if x > from_idx and x != -1], default=len(sql_query))
            
            from_clause = sql_query[from_idx:end_idx].strip()
            explanation_lines.append(f"From: {from_clause}")
        
        if "WHERE" in query_upper:
            where_idx = query_upper.find("WHERE")
            group_idx = query_upper.find("GROUP BY")
            order_idx = query_upper.find("ORDER BY")
            
            end_idx = min([x for x in [group_idx, order_idx] if x > where_idx and x != -1], default=len(sql_query))
            where_clause = sql_query[where_idx:end_idx].strip()
            explanation_lines.append(f"Filtering: {where_clause}")
        
        if "GROUP BY" in query_upper:
            group_idx = query_upper.find("GROUP BY")
            order_idx = query_upper.find("ORDER BY")
            end_idx = order_idx if order_idx > group_idx else len(sql_query)
            group_clause = sql_query[group_idx:end_idx].strip()
            explanation_lines.append(f"Grouping: {group_clause}")
        
        if "ORDER BY" in query_upper:
            order_idx = query_upper.find("ORDER BY")
            limit_idx = query_upper.find("LIMIT")
            end_idx = limit_idx if limit_idx > order_idx else len(sql_query)
            order_clause = sql_query[order_idx:end_idx].strip()
            explanation_lines.append(f"Sorting: {order_clause}")
        
        if "LIMIT" in query_upper:
            limit_idx = query_upper.find("LIMIT")
            limit_clause = sql_query[limit_idx:].strip()
            explanation_lines.append(f"Limiting: {limit_clause}")
        
        return "\n".join(explanation_lines)
