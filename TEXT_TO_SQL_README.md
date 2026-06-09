# Prompt 6: Text-to-SQL Engine

## Overview

The Text-to-SQL Engine converts natural language questions about FMCG analytics into SQL queries, executes them against the database, and provides intelligent interpretation of results.

## Features

### 1. **Schema-Aware Query Generation**
- Automatically extracts database schema (tables, columns, types)
- Understands relationships and foreign keys
- Maintains schema cache for performance
- Provides intelligent column descriptions

### 2. **Natural Language Understanding**
- Pattern-based intent detection
- Rule-based query generation for common FMCG questions
- Timeframe extraction (last month, this quarter, etc.)
- Product/entity name recognition

### 3. **Query Safety & Validation**
- **SQL Injection Prevention**: Detects and blocks injection attempts
- **Dangerous Keywords**: Blocks DROP, DELETE, INSERT, UPDATE, etc.
- **Table Whitelist**: Only allows queries on approved tables
- **Query Complexity Analysis**: Warns about slow queries
- **Comment Injection Prevention**: Detects malicious SQL comments

### 4. **Intelligent Result Interpretation**
- Detects query intent (promotions, sales, inventory, stockouts, etc.)
- Generates actionable insights
- Identifies anomalies and trends
- Provides business recommendations
- Suggests visualizations

### 5. **LangChain Ready**
- Modular architecture supports LLM integration
- Prompt templates for advanced SQL generation
- Fallback to rule-based generation

## Architecture

```
TextToSQLService (Orchestrator)
├── SchemaExtractor
│   ├── get_schema() - Extract all tables/columns
│   ├── get_schema_as_string() - Format for LLM
│   └── validate_table_exists()
│
├── SQLGenerator
│   ├── generate_sql() - Convert NL to SQL
│   ├── _try_rule_based() - Pattern matching
│   └── _try_llm_based() - LLM fallback
│
├── QueryValidator
│   ├── validate() - Full security check
│   ├── _check_dangerous_keywords()
│   ├── _check_sql_injection()
│   ├── _check_table_whitelist()
│   └── sanitize_query()
│
└── ResultInterpreter
    ├── interpret() - Generate insights
    ├── _interpret_promo_performance()
    ├── _interpret_regional_sales()
    ├── _interpret_stockout_analysis()
    └── [6 other intent handlers]
```

## Supported Query Patterns

### 1. **Promotion Performance**
**Questions:**
- "Which promotion performed best last month?"
- "What's the top performing promo?"
- "Show me promotion effectiveness"

**Output:**
- Top products by promotion sales
- Average discounts and units sold
- Recommendations for scaling

### 2. **Regional Sales Comparison**
**Questions:**
- "Compare North vs South region sales"
- "Which region is performing best?"
- "Regional performance breakdown"

**Output:**
- Sales by region
- Market penetration metrics
- Regional rankings and disparity analysis

### 3. **Stockout Detection**
**Questions:**
- "Which products experienced stockouts?"
- "Where do we have out-of-stock items?"
- "Show me stockout issues"

**Output:**
- Products with stockouts
- Impact on lost sales
- Affected regions
- ⚠️ Urgent recommendations

### 4. **Product Performance**
**Questions:**
- "Top performing products this quarter"
- "Show me best-selling products"
- "Product sales analysis"

**Output:**
- Top products by sales/margin
- Price analysis
- Category breakdown
- Portfolio recommendations

### 5. **Inventory Turnover**
**Questions:**
- "Show me inventory turnover by product"
- "Which products are slow-moving?"
- "Inventory analysis"

**Output:**
- Inventory turn rates
- High-turn vs slow-moving
- Optimization recommendations

### 6. **Campaign Impact Analysis**
**Questions:**
- "What was the campaign impact on Spark Lemon Water?"
- "Show me promo lift for [product]"
- "Campaign effectiveness"

**Output:**
- Sales lift percentage
- Campaign vs non-campaign comparison
- ROI analysis
- Optimization suggestions

## API Endpoints

### 1. **Process Query**
```bash
POST /api/v1/text-to-sql/query
Content-Type: application/json

{
  "query": "Which promotion performed best last month?",
  "use_llm": false,
  "context": {}
}

Response:
{
  "original_query": "Which promotion performed best...",
  "generated_sql": "SELECT ...",
  "is_valid": true,
  "results": [
    {"product_id": 1, "product_name": "Spark", ...},
    ...
  ],
  "interpretation": {
    "summary": "Analysis of 15 promoted products...",
    "key_findings": [...],
    "insights": [...],
    "metrics": {...},
    "recommendations": [...]
  },
  "execution_time_ms": 245
}
```

### 2. **Validate SQL**
```bash
POST /api/v1/text-to-sql/validate
?sql_query=SELECT * FROM sales_promotions WHERE...

Response:
{
  "is_valid": true,
  "validation_result": {
    "errors": [],
    "warnings": [],
    "estimated_risk": "low",
    "estimated_time_ms": 500
  }
}
```

### 3. **Get Schema Info**
```bash
GET /api/v1/text-to-sql/schema

Response:
{
  "tables": ["products", "stores", "sales_promotions", "inventory"],
  "schema_details": {
    "products": {
      "description": "Product master...",
      "columns": [...]
    }
  }
}
```

### 4. **Get Sample Queries**
```bash
GET /api/v1/text-to-sql/samples

Response:
{
  "samples": [
    {
      "question": "Which promotion performed best last month?",
      "intent": "PROMO_PERFORMANCE",
      "description": "Analyze promotion effectiveness by product"
    },
    ...
  ]
}
```

### 5. **Explain Query**
```bash
POST /api/v1/text-to-sql/explain
?sql_query=SELECT ...

Response:
{
  "explanation": "QUERY EXPLANATION:\nRetrieving: product sales...\nFrom: sales_promotions..."
}
```

## Usage Examples

### Example 1: Promotion Performance
```python
from services.text_to_sql_service import TextToSQLService

service = TextToSQLService(db_session)

result = service.process_query(
    "Which promotion performed best last month?"
)

print(f"SQL: {result['generated_sql']}")
print(f"Results: {result['results']}")
print(f"Insights: {result['interpretation']['insights']}")
```

### Example 2: Validation Only
```python
is_valid, validation = service.validate_query(sql_query)

if not is_valid:
    print(f"Errors: {validation['errors']}")
else:
    print(f"Query is safe. Risk level: {validation['estimated_risk']}")
```

### Example 3: Get Schema for Context
```python
schema_text = service.get_schema_as_text()
print(schema_text)  # Formatted schema for LLM prompts
```

## Security Features

### 1. **SQL Injection Prevention**
- Blocks queries with multiple statements
- Detects unbalanced quotes
- Prevents union-based injection
- Sanitizes input

### 2. **Access Control**
- Table whitelist (7 FMCG tables only)
- No DDL/DML operations allowed
- Only SELECT queries permitted
- User audit trail

### 3. **Query Complexity Limits**
- Warns on deep nesting (3+ subqueries)
- Detects expensive joins (5+ joins)
- Suggests optimization

## Performance

- **Schema Caching**: ~5ms subsequent queries
- **Rule-Based Generation**: <50ms for common patterns
- **Query Execution**: Depends on data size (typical 200-500ms)
- **Result Interpretation**: <100ms
- **Total E2E**: 300-1000ms for typical queries

## Integration with Other Prompts

### Prompt 7: Insight Generation
- Uses ResultInterpreter for initial insights
- Can be extended with deeper analysis

### Prompt 8: Report Generation
- Text-to-SQL queries form basis of reports
- Interpretations used in executive summaries

### Prompt 10: Autonomous Agent
- Text-to-SQL powers agent's data access
- Enables proactive monitoring

## Future Enhancements

1. **LLM Integration**
   - OpenAI GPT-4 for complex queries
   - Custom prompt templates
   - Fine-tuning on FMCG domain

2. **Advanced Caching**
   - Query result caching
   - Schema change detection
   - Incremental refresh

3. **Visualization**
   - Auto-generate charts
   - Dashboard recommendations
   - Export to Tableau/Power BI

4. **Optimization**
   - Query plan analysis
   - Index recommendations
   - Query rewriting

5. **Collaboration**
   - Saved queries
   - Query sharing
   - Annotation/notes

## Testing

```bash
# Test basic query
curl -X POST http://localhost:8001/api/v1/text-to-sql/query \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which promotion performed best last month?",
    "use_llm": false
  }'

# Test validation
curl -X POST http://localhost:8001/api/v1/text-to-sql/validate \
  -H "Authorization: Bearer <token>" \
  -d "sql_query=SELECT * FROM sales_promotions LIMIT 10"

# Get samples
curl -X GET http://localhost:8001/api/v1/text-to-sql/samples \
  -H "Authorization: Bearer <token>"
```

## Configuration

Update in `.env` or `config.py`:
```bash
# Text-to-SQL Engine
TEXT_TO_SQL_ENABLED=True
TEXT_TO_SQL_TIMEOUT_SECONDS=30
TEXT_TO_SQL_USE_LLM=False
TEXT_TO_SQL_CACHE_SCHEMA=True
```

## Troubleshooting

**Issue**: "Query validation failed: Dangerous keyword not allowed"
**Solution**: SQL generation blocked a keyword. Text-to-SQL only allows SELECT queries.

**Issue**: "Table not whitelisted"
**Solution**: Only FMCG tables allowed. Check schema endpoint for available tables.

**Issue**: "Unbalanced quotes detected"
**Solution**: Query has syntax error. Use validation endpoint to diagnose.

**Issue**: No results returned
**Solution**: Query may have wrong date filters or no data. Check schema and sample queries.

## References

- Database Schema: [architecture/postgres_schema_fmcg_analytics.sql](../architecture/postgres_schema_fmcg_analytics.sql)
- Implementation: [backend/text_to_sql/](../backend/text_to_sql/)
- Integration: [backend/services/text_to_sql_service.py](../backend/services/text_to_sql_service.py)
- API Routes: [backend/api/routes.py](../backend/api/routes.py) - Text-to-SQL section
