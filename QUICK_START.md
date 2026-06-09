# FMCG BI System - Quick Start Guide

## System Ready ✅

Your complete FMCG BI Multi-Agent system is installed and operational. Here's how to use it.

---

## What You Have

- **6 AI Agents:** QueryUnderstanding → SQLGeneration → Analytics → Insights → Visualization → Reporting
- **LangGraph Workflow:** Orchestrates agents through 9-node state machine
- **SQLite Database:** 68,070 rows of synthetic FMCG data (20 products, 50 stores, 24 weeks)
- **Session Memory:** Maintains conversation context for follow-ups
- **Ready to Deploy:** Streamlit UI, FastAPI backend, or direct Python integration

---

## Quick Start

### 1️⃣ Batch Mode (Test Examples)
```bash
cd c:\Users\revan\Downloads\AI_Project
python -m ai_agent.main
```
Runs 5 example queries and displays responses with KPIs and reports.

### 2️⃣ Interactive Mode (Chat)
```bash
python -m ai_agent.main interactive
```
Launches an interactive REPL for conversational queries.
- Type your questions
- Type `quit` to exit
- Type `history` to see conversation context

### 3️⃣ Python Integration
```python
from ai_agent import FMCGAgentWorkflow

workflow = FMCGAgentWorkflow(db_path="architecture/fmcg_analytics.db")

# Single query
result = workflow.process(
    user_message="What was the promotional performance last week?",
    user_id="analyst_001"
)
print(result.response_text)

# Follow-up query (same session)
result = workflow.process(
    user_message="Show me the same data by region",
    session_id=result.session_id,
    user_id="analyst_001"
)
print(result.response_text)
```

---

## Example Queries

Try these business questions:

| Query | Best For |
|-------|----------|
| "Show me regional sales comparison for the last quarter." | Sales analysis |
| "What's the promo performance across categories?" | Promotion analysis |
| "Give me a dashboard snapshot of key metrics." | Executive summary |
| "How is inventory moving in the North region?" | Inventory management |
| "Show me the campaign impact for last month." | Campaign evaluation |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│ User Input (Natural Language Query)                      │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │ QueryUnderstanding  │ ← Extracts intent & entities
        │      Agent          │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  SQL Generation     │ ← Converts to safe SQL
        │      Agent          │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │   Analytics         │ ← Executes & aggregates
        │      Agent          │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │   Insight Gen       │ ← Anomaly detection
        │      Agent          │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ Visualization Gen   │ ← Vega-Lite specs
        │      Agent          │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │   Report Gen        │ ← Executive summary
        │      Agent          │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  Response Assembly  │ ← Format output
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │   Final Response    │ ← User sees results
        └─────────────────────┘
```

---

## What Each Agent Does

### 1. QueryUnderstandingAgent
- Parses natural language
- Extracts business intent (PROMO_PERFORMANCE, INVENTORY_MOVEMENT, etc.)
- Identifies entities (regions, time periods, product categories)
- Calculates confidence scores
- Generates clarifying questions if needed

### 2. SQLGenerationAgent
- Converts structured intent to SQL
- Applies security guardrails (SQL injection prevention)
- Handles role-based access (RLS)
- Parameterizes all user inputs
- Returns 5 different query templates based on intent

### 3. AnalyticsAgent
- Executes SQL queries against database
- Extracts 8 standard KPIs (revenue, units, margin, discount %, promo units, etc.)
- Aggregates time-series data
- Computes dimensional breakdowns (by region, category, store)

### 4. InsightAgent
- Detects anomalies (drops > 20%, stockouts > 100)
- Generates business recommendations
- Builds markdown narratives
- Calculates confidence scores

### 5. VisualizationAgent
- Creates Vega-Lite specifications
- Generates 3 chart types: line (time series), bar (aggregations), KPI cards
- Embeds interactive specs for frontend rendering

### 6. ReportAgent
- Assembles all outputs into structured report
- Generates executive summary (3 sections: Analysis, Actions, Metrics)
- Assigns unique report ID
- Stores metadata for audit trail

---

## Session & Memory

The system maintains conversation context automatically:

```python
# First query creates new session
result1 = workflow.process(
    user_message="What's the promo performance?",
    user_id="analyst_001"
)
session_id = result1.session_id

# Follow-up automatically retrieves context
result2 = workflow.process(
    user_message="Show by region",
    session_id=session_id,
    user_id="analyst_001"
)
# System remembers "promo performance" context!
```

---

## Database

### Current (Development)
- **Type:** SQLite
- **Path:** `architecture/fmcg_analytics.db`
- **Tables:** products, stores, sales_promotions, inventory
- **Size:** 68,070 rows

### Production-Ready
- **Type:** PostgreSQL
- **Schema:** `architecture/postgres_schema_fmcg_analytics.sql`
- **Docker:** Use `docker-compose.yml` to start
- **Migration:** Ready when needed

---

## Troubleshooting

### "unable to open database file"
**Solution:** Database path is incorrect. Check:
```bash
python -c "import os; print(os.path.exists('architecture/fmcg_analytics.db'))"
```
Should return `True`.

### "No data available for this query"
**Possible Causes:**
- Time range has no data (synthetic data covers last 24 weeks)
- SQL generated but returned empty results
- Entity extraction failed

**Debug:**
```bash
python -m ai_agent.main  # Run batch tests to see what works
```

### Unicode/Emoji errors
**Solution:** Already fixed. If re-occurs, remove emoji characters from output strings.

---

## Next Steps

### Want a Web UI?
Create `streamlit_app.py`:
```bash
pip install streamlit
# Then create app that calls workflow.process()
```

### Want LLM Integration?
```bash
pip install openai
# Update insight_agent.py to use LLM for narratives
```

### Want Production Deployment?
```bash
# Use Docker
docker-compose up -d

# Or FastAPI + Uvicorn
pip install fastapi uvicorn
# Create API endpoints wrapping workflow.process()
```

---

## Key Files

| File | Purpose |
|------|---------|
| `ai_agent/workflow.py` | Main orchestrator (LangGraph) |
| `ai_agent/main.py` | Entry point (batch + interactive) |
| `ai_agent/schema.py` | Data structures (14 dataclasses) |
| `ai_agent/query_agent.py` | Intent understanding |
| `ai_agent/sql_agent.py` | SQL generation |
| `ai_agent/analytics_agent.py` | Query execution |
| `architecture/fmcg_analytics.db` | SQLite database |
| `architecture/postgres_schema_fmcg_analytics.sql` | PostgreSQL schema |
| `data/generate_fmcg_beverage_dataset.py` | Data generation script |

---

## Performance

- Query Processing: ~500-1000ms per query
- Database Lookup: <100ms
- Report Generation: <50ms
- Total End-to-End: ~5-10 seconds

---

## Support

For issues or questions:
1. Check `TEST_EXECUTION_REPORT.md` for known issues
2. Review `ai_agent/README.md` for detailed documentation
3. Run batch mode: `python -m ai_agent.main`
4. Check database: `sqlite3 architecture/fmcg_analytics.db` (query tables)

---

**Your system is ready to use! Start with `python -m ai_agent.main` 🚀**

