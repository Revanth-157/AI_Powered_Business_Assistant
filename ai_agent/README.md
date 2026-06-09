# FMCG BI Multi-Agent System - LangGraph Implementation

Production-style multi-agent architecture for conversational FMCG business intelligence using LangGraph.

## Architecture Overview

### Agents

1. **Query Understanding Agent**
   - Parses user intent and extracts entities (time, region, category, store format)
   - Classifies business use-case: promotional performance, inventory movement, regional sales, campaign impact, KPI dashboard
   - Detects ambiguity and generates clarifying questions
   - Confidence scoring for decision-making

2. **SQL Generation Agent**
   - Converts structured intent to parameterized SQL queries
   - Enforces safety guardrails: whitelisted tables/columns, forbidden DDL patterns
   - Prevents SQL injection via parameter binding
   - Estimates query cost (simple heuristic; EXPLAIN ANALYZE in production)

3. **Analytics Agent**
   - Executes safe SQL queries against SQLite/PostgreSQL
   - Computes derived KPIs: revenue, promo lift, inventory turn, sell-through, growth rates
   - Aggregates results by dimension (time, region, category)
   - Returns time-series and aggregation views

4. **Insight Agent**
   - Generates narrative explanations of analytics results
   - Detects anomalies: zero values, sudden drops, high stockouts
   - Produces actionable recommendations
   - Calculates confidence score

5. **Visualization Agent**
   - Chooses appropriate chart types (line, bar, pie, heatmap)
   - Generates Vega-Lite specifications for rendering
   - Creates KPI card data structures
   - Supports multi-dimensional drill-downs

6. **Report Agent**
   - Assembles insights, visuals, and KPIs into executive summaries
   - Persists reports with metadata and provenance
   - Generates title, summary, and executive narrative
   - Stores in memory (extensible to database)

### Graph Flow

```
User Message
    ↓
Query Understanding
    ↓
  [Clarification Needed?] → Clarification Node → Response Assembly
    ↓ No
SQL Generation
    ↓
SQL Validation
    ↓
  [Safe?] → Fallback → Response Assembly
    ↓ Yes
Analytics Execution
    ↓
    ├─→ Insight Generation ─→┐
    │                        ├─→ Report Generation → Response Assembly
    └─→ Visualization Generation ─┘
```

## Installation

```bash
# From project root
pip install langgraph langchain langchain-openai pydantic sqlparse psycopg2-binary

# Or use the existing install (already done)
```

## Usage

### Example 1: Batch Processing

```python
from ai_agent.workflow import FMCGAgentWorkflow

# Initialize
workflow = FMCGAgentWorkflow(db_path="architecture/fmcg_analytics.db")

# Process query
result = workflow.process(
    user_message="What was the promotional performance last week?",
    user_id="analyst_001"
)

print(result.response_text)
# Output includes KPIs, insights, recommendations, and report ID
```

### Example 2: Interactive Session

```bash
cd ai_agent
python main.py interactive
```

Then ask questions like:
- "Show me regional sales for last quarter"
- "How is inventory turnover across stores?"
- "What's the impact of our promotions?"

### Example 3: Direct Agent Usage

```python
from ai_agent.query_agent import QueryUnderstandingAgent
from ai_agent.sql_agent import SQLGenerationAgent
from ai_agent.analytics_agent import AnalyticsAgent

# Query Understanding
query_agent = QueryUnderstandingAgent()
state = query_agent.process(state)

# SQL Generation
sql_agent = SQLGenerationAgent()
state = sql_agent.process(state)

# Analytics
analytics_agent = AnalyticsAgent(db_path="architecture/fmcg_analytics.db")
state = analytics_agent.process(state)
```

## State and Memory

### AgentState
Central state object passed through the workflow:
- `user_message`: Input query
- `structured_intent`: Parsed intent with entities and filters
- `sql_query`: Generated SQL with safety validation
- `analytics_output`: KPIs, time-series, aggregations
- `insights`: Narrative explanations and recommendations
- `visualizations`: Chart specifications (Vega-Lite)
- `report_id`: Persisted report identifier
- `response_text`: Final user-facing response

### Session Memory
Ephemeral per-session storage (TTL = 1 hour):
- Conversation history
- Resolved entities for follow-ups
- Query result cache
- User preferences

Example: User can ask "And what about last quarter?" and the system resolves "last quarter" from previous context.

## Error Handling

1. **Input Validation**: Low-confidence intents trigger clarification
2. **SQL Safety**: Forbidden patterns blocked; whitelisted columns only
3. **Query Cost**: High-cost queries flagged or aggregated
4. **Database Errors**: Retry with backoff; fallback responses
5. **Logging**: All errors captured for audit trails

## Security & Governance

- **SQL Injection Prevention**: Parameterized queries only
- **Row-Level Security**: User role + region filters enforced
- **Access Control**: Whitelisted tables/columns per role
- **Audit Trail**: Query text (sanitized), user ID, timestamp logged
- **Rate Limiting**: Per-session query throttling (extensible)

## Configuration

Edit workflow parameters in `workflow.py`:

```python
workflow = FMCGAgentWorkflow(
    db_path="architecture/fmcg_analytics.db"
)

# Adjust memory TTL
workflow.memory.ttl_seconds = 7200  # 2 hours

# Add role-based access
state.user_role = "executive"  # analyst, manager, executive
state.accessible_regions = ["North", "South"]  # RLS filter
```

## Extensibility

### Add a New Intent Type

In `query_agent.py`:
```python
Intent.CUSTOM = "custom_intent"

self.intent_keywords[Intent.CUSTOM] = ["custom", "keywords"]
```

In `sql_agent.py`:
```python
def _custom_intent_sql(self, intent, state):
    sql = "SELECT ... FROM ..."
    return SQLQuery(text=sql, params={})
```

### Add a New KPI

In `analytics_agent.py`:
```python
if "custom_metric" in first_row:
    kpis.append(KPIResult(
        metric_name="Custom Metric",
        value=float(first_row["custom_metric"]),
        unit="unit",
        timestamp=datetime.utcnow()
    ))
```

## Performance Tuning

1. **Caching**: Results cached in session memory (600s default)
2. **Materialized Views**: Pre-compute common aggregations in database
3. **Indexing**: Ensure database indexes on `week_start`, `region`, `product_id`
4. **Batch Processing**: Run multiple queries in parallel via LangGraph
5. **Query Cost Limiting**: Set thresholds; reject or break into sub-queries

## Testing

Run example queries:
```bash
cd ai_agent
python main.py
```

Expected output:
- Query → Structured Intent
- SQL generated and validated
- Results + KPIs computed
- Insights + Visualizations generated
- Report persisted

## Database Support

Currently supports:
- **SQLite**: `architecture/fmcg_analytics.db` (default)
- **PostgreSQL**: Swap connection string; agents are DB-agnostic

Modify in `analytics_agent.py`:
```python
def __init__(self, db_url: str = None):
    self.db_url = db_url or "sqlite:///architecture/fmcg_analytics.db"
```

## Next Steps

- Deploy Streamlit UI on top of workflow (see `../streamlit_app`)
- Integrate OpenAI/Gemini LLMs for better NLU and summarization
- Add real-time data ingestion and streaming
- Implement approval workflows for high-cost/sensitive queries
- Scale horizontally with FastAPI + Celery workers

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain](https://python.langchain.com/)
- [Vega-Lite Visualization Specification](https://vega.github.io/vega-lite/)
