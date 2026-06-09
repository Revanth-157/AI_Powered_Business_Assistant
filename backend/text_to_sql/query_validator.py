"""
SQL query validation and safety checks.
"""
from typing import Tuple, Dict, List
import re
import logging

logger = logging.getLogger(__name__)


class QueryValidator:
    """Validate SQL queries for safety and correctness."""
    
    # SQL keywords that should not appear in user queries
    DANGEROUS_KEYWORDS = [
        "DROP", "DELETE", "INSERT", "UPDATE", "CREATE", "ALTER", "TRUNCATE",
        "EXEC", "EXECUTE", "GRANT", "REVOKE", "PRAGMA", "ATTACH", "DETACH"
    ]
    
    # Functions that are safe to use
    SAFE_FUNCTIONS = [
        "SUM", "AVG", "COUNT", "MIN", "MAX", "ROUND", "CAST", "EXTRACT",
        "DATE_PART", "SUBSTRING", "LOWER", "UPPER", "TRIM", "COALESCE",
        "CASE", "WHEN", "THEN", "ELSE", "END", "GROUP_CONCAT", "CONCAT"
    ]
    
    # Allowed tables
    ALLOWED_TABLES = [
        "products", "stores", "sales_promotions", "inventory",
        "users", "chat_history", "generated_reports"
    ]
    
    def __init__(self):
        """Initialize query validator."""
        self.errors = []
        self.warnings = []
    
    def validate(self, query: str, allow_joins: bool = True) -> Tuple[bool, Dict]:
        """
        Validate SQL query for safety and correctness.
        
        Args:
            query: SQL query string
            allow_joins: Whether to allow JOIN clauses
        
        Returns:
            Tuple of (is_valid, validation_result_dict)
        """
        self.errors = []
        self.warnings = []
        
        # Reset validation state
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "estimated_risk": "low"
        }
        
        # Check 1: Query not empty
        if not query or not query.strip():
            result["is_valid"] = False
            result["errors"].append("Query is empty")
            return False, result
        
        # Check 2: No dangerous keywords
        if not self._check_dangerous_keywords(query):
            result["is_valid"] = False
            result["errors"].extend(self.errors)
        
        # Check 3: Only SELECT queries allowed
        if not self._is_select_query(query):
            result["is_valid"] = False
            result["errors"].append("Only SELECT queries are allowed for security")
            return False, result
        
        # Check 4: SQL injection patterns
        if not self._check_sql_injection(query):
            result["is_valid"] = False
            result["errors"].extend(self.errors)
            result["estimated_risk"] = "high"
        
        # Check 5: Table whitelist
        if not self._check_table_whitelist(query):
            result["is_valid"] = False
            result["errors"].extend(self.errors)
        
        # Check 6: Query complexity
        complexity_warning = self._check_query_complexity(query)
        if complexity_warning:
            result["warnings"].append(complexity_warning)
        
        # Check 7: Comment injection
        if not self._check_comments(query):
            self.errors.extend(self.errors)
            result["estimated_risk"] = "high"
        
        result["errors"] = self.errors
        result["warnings"] = self.warnings
        
        if result["errors"]:
            result["is_valid"] = False
        
        return result["is_valid"], result
    
    def _is_select_query(self, query: str) -> bool:
        """Check if query is a SELECT query."""
        query_upper = query.strip().upper()
        
        # Must start with SELECT, WITH (CTE), or (SELECT for subqueries)
        if query_upper.startswith("SELECT") or query_upper.startswith("WITH"):
            # Ensure it's not SELECT INTO
            if "SELECT INTO" in query_upper or "SELECT...INTO" in query_upper:
                self.errors.append("SELECT INTO is not allowed")
                return False
            return True
        
        self.errors.append("Only SELECT queries are allowed")
        return False
    
    def _check_dangerous_keywords(self, query: str) -> bool:
        """Check for dangerous SQL keywords."""
        query_upper = query.upper()
        
        for keyword in self.DANGEROUS_KEYWORDS:
            # Use word boundaries to avoid false positives
            if re.search(r'\b' + keyword + r'\b', query_upper):
                self.errors.append(f"Dangerous keyword '{keyword}' not allowed")
                return False
        
        return True
    
    def _check_sql_injection(self, query: str) -> bool:
        """Check for common SQL injection patterns."""
        # Pattern 1: Multiple statements (semicolon followed by non-comment)
        if re.search(r';\s*(?!--)\s*\w', query):
            self.errors.append("Multiple SQL statements detected")
            return False
        
        # Pattern 2: Suspicious quotes and escapes
        if re.search(r"(['\"])\s*(\||;|--)", query):
            self.errors.append("Suspicious quote/escape pattern detected")
            return False
        
        # Pattern 3: UNION keyword (can be used for injection)
        if re.search(r'\bUNION\b', query.upper()):
            self.warnings.append("UNION queries are suspicious, please verify")
        
        # Pattern 4: Unbalanced quotes
        single_quotes = query.count("'") - len(re.findall(r"''", query)) * 2
        double_quotes = query.count('"')
        if single_quotes % 2 != 0 or double_quotes % 2 != 0:
            self.errors.append("Unbalanced quotes detected")
            return False
        
        return True
    
    def _check_table_whitelist(self, query: str) -> bool:
        """Check that only whitelisted tables are accessed."""
        query_upper = query.upper()
        
        for table in self.ALLOWED_TABLES:
            # Create pattern for table usage
            pattern = r'\b' + table.upper() + r'\b'
            query_upper_temp = query_upper.replace(table.upper(), "")
            
            if re.search(pattern, query):
                continue  # Table is allowed
        
        # Find all table references (patterns like FROM table, JOIN table)
        patterns = [
            r'\bFROM\s+(\w+)',
            r'\bJOIN\s+(\w+)',
            r'\bLEFT\s+JOIN\s+(\w+)',
            r'\bRIGHT\s+JOIN\s+(\w+)',
            r'\bINNER\s+JOIN\s+(\w+)',
        ]
        
        found_tables = set()
        for pattern in patterns:
            matches = re.findall(pattern, query_upper)
            found_tables.update([m.strip() for m in matches])
        
        # Check if all found tables are in whitelist
        allowed_upper = [t.upper() for t in self.ALLOWED_TABLES]
        for table in found_tables:
            if table not in allowed_upper and not table.startswith("("):  # Skip subqueries
                self.errors.append(f"Table '{table}' is not whitelisted")
                return False
        
        return True
    
    def _check_query_complexity(self, query: str) -> str:
        """Check query complexity and provide warnings."""
        # Count subqueries
        subquery_count = query.count("SELECT") - 1
        if subquery_count > 3:
            return f"Query has {subquery_count} nested subqueries - may be slow"
        
        # Count joins
        join_count = len(re.findall(r'\bJOIN\b', query.upper()))
        if join_count > 5:
            return f"Query has {join_count} JOINs - may be slow"
        
        # Check for DISTINCT with GROUP BY (often redundant)
        if "DISTINCT" in query.upper() and "GROUP BY" in query.upper():
            return "Query uses both DISTINCT and GROUP BY - may be redundant"
        
        # Check for cross joins
        if re.search(r'FROM\s+\w+\s*,\s*\w+', query):
            return "Query appears to use cross join - verify this is intentional"
        
        return ""
    
    def _check_comments(self, query: str) -> bool:
        """Check for SQL comment injection patterns."""
        # Pattern: -- followed by suspicious content
        if re.search(r'--\s*[;(]', query):
            self.errors.append("Suspicious SQL comment pattern detected")
            return False
        
        # Pattern: /* */ style comments with suspicious content
        if re.search(r'/\*\s*[A-Z]+\s*\*/', query):
            self.warnings.append("SQL block comment detected - verify legitimacy")
        
        return True
    
    def sanitize_query(self, query: str) -> str:
        """
        Sanitize query by removing/escaping potentially dangerous patterns.
        This is NOT a replacement for proper parameterization!
        """
        sanitized = query
        
        # Remove leading/trailing whitespace
        sanitized = sanitized.strip()
        
        # Remove trailing semicolon if present
        if sanitized.endswith(";"):
            sanitized = sanitized[:-1].strip()
        
        # Remove SQL comments
        sanitized = re.sub(r'--.*?$', '', sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r'/\*.*?\*/', '', sanitized, flags=re.DOTALL)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        return sanitized
    
    def estimate_query_cost(self, query: str) -> Dict[str, any]:
        """
        Estimate query execution characteristics.
        """
        cost_estimate = {
            "estimated_rows": 0,
            "estimated_time_ms": 0,
            "complexity_score": 0,  # 0-10
            "recommendation": ""
        }
        
        # Base complexity: 1 point for SELECT
        complexity = 1
        
        # Add complexity for joins
        join_count = len(re.findall(r'\bJOIN\b', query.upper()))
        complexity += join_count * 2
        
        # Add complexity for subqueries
        subquery_count = query.count("SELECT") - 1
        complexity += subquery_count * 1.5
        
        # Add complexity for GROUP BY
        if "GROUP BY" in query.upper():
            complexity += 1
        
        # Estimate rows (simplified)
        # This is just an estimate without actual stats
        if "LIMIT" in query.upper():
            limit_match = re.search(r'LIMIT\s+(\d+)', query.upper())
            if limit_match:
                cost_estimate["estimated_rows"] = int(limit_match.group(1))
        else:
            cost_estimate["estimated_rows"] = 100000  # Default estimate
        
        # Rough time estimate (milliseconds)
        cost_estimate["estimated_time_ms"] = min(int(complexity * 100), 5000)
        cost_estimate["complexity_score"] = min(int(complexity), 10)
        
        # Recommendations
        if complexity > 7:
            cost_estimate["recommendation"] = "Query is complex. Consider adding indexes or using materialized views."
        elif complexity > 5:
            cost_estimate["recommendation"] = "Query is moderately complex. Performance may be acceptable."
        else:
            cost_estimate["recommendation"] = "Query is simple and should perform well."
        
        return cost_estimate
