# Autonomous FMCG Business Intelligence Assistant

## 1. High-level Architecture Diagram Description

A production-style architecture for the Autonomous FMCG BI Assistant includes: 

- Data ingestion and synthetic data generation
- Data storage and transformation in PostgreSQL
- API / application backend in Python + FastAPI
- AI orchestration in LangGraph with OpenAI/Gemini connectors
- Conversational UI in Streamlit for business users
- Role-based access via Supabase auth and policy enforcement
- Visualization rendering and executive summary generation

### Diagram description

1. User Layer
   - Business users access the assistant through a Streamlit conversational dashboard.
   - Role-based access controls ensure executives, sales managers, and analysts see only permitted KPIs.

2. Application Layer
   - FastAPI serves REST/GraphQL endpoints, session management, and security.
   - LangGraph orchestrates AI workflows: intent extraction, question answering, insight generation, follow-up context.
   - OpenAI/Gemini provides LLM responses, natural language understanding, and summarization.

3. Data Layer
   - PostgreSQL holds synthetic FMCG datasets in normalized tables.
   - Data engineering processes populate and aggregate sales, promotions, inventory, product master, and store master tables.
   - Supabase provides auth, RLS policies, and optionally a realtime layer.

4. Analytics Layer
   - KPI service computes metrics such as revenue, promo lift, inventory turn, and regional growth.
   - Visualization engine builds charts on demand using generated query results.
   - Automatic insight engine identifies anomalies, trends, and campaign impact summaries.

5. Deployment Layer
   - Containerized services run in Kubernetes or managed container service.
   - CI/CD deploys the FastAPI backend, LangGraph workflows, and Streamlit frontend.
   - Monitoring and logging capture user sessions, query performance, and model usage.

## 2. Components

- Synthetic Data Generator
  - Python service to create FMCG sample data for sales, promotions, inventory, product master, and store master.
  - Runs on schedule or as part of data seeding.

- PostgreSQL Database
  - Stores all transactional and master data.
  - Supports analytical aggregates and KPI queries.

- FastAPI Backend
  - Handles authentication, authorization, data access, and API endpoints for the UI.
  - Exposes services for query execution, summary generation, and report retrieval.

- LangGraph Orchestration
  - Manages AI agent flows for natural language parsing, follow-up context, and multi-step reasoning.
  - Coordinates calls to OpenAI/Gemini and the database query layer.

- AI Layer
  - Intent extraction
  - Question classification
  - KPI computation
  - Executive summary generation
  - Insight explanation and visualization recommendation

- Streamlit UI
  - Conversational chat interface
  - Dynamic dashboards and chart rendering
  - Follow-up conversation history
  - KPI panels and snapshot cards

- Supabase Auth and Access Control
  - User authentication using email, SSO, or enterprise provider.
  - Role-based policies for data access and feature gating.

## 3. Data Flow

1. Synthetic Data Generation
   - Generator creates datasets covering sales, promotions, inventory, and masters.
   - Data loads into PostgreSQL through batch inserts.

2. Query Execution
   - User sends natural language query via Streamlit.
   - FastAPI forwards the request to LangGraph AI workflow.
   - LangGraph extracts entities, intents, and relevant dimensions.
   - The backend translates intent to SQL or analytical query against PostgreSQL.
   - Results return to LangGraph for insight generation.

3. Insight and Visualization
   - AI layer generates narrative insights, KPI calculations, and recommended visuals.
   - Streamlit renders charts and executive summaries.
   - Follow-up context is maintained in session state.

4. Access Enforcement
   - Supabase validates user identity.
   - FastAPI applies role-based filters and row-level security for query data.

## 4. Database Design

### Core tables

- `product_master`
  - `product_id`
  - `product_name`
  - `brand`
  - `category`
  - `sub_category`
  - `pack_size`
  - `launch_date`
  - `price`

- `store_master`
  - `store_id`
  - `store_name`
  - `region`
  - `sub_region`
  - `channel`
  - `market_type`

- `sales`
  - `sale_id`
  - `transaction_date`
  - `store_id`
  - `product_id`
  - `units_sold`
  - `sales_value`
  - `cost`
  - `gross_margin`

- `promotions`
  - `promotion_id`
  - `product_id`
  - `store_id`
  - `promo_type`
  - `start_date`
  - `end_date`
  - `discount_pct`
  - `promo_description`

- `inventory_movements`
  - `inventory_id`
  - `movement_date`
  - `store_id`
  - `product_id`
  - `opening_qty`
  - `received_qty`
  - `sold_qty`
  - `closing_qty`
  - `shrinkage_qty`

### Analytical views

- `vw_promo_performance`
- `vw_regional_sales`
- `vw_inventory_turn`
- `vw_campaign_impact`

### KPI calculations

- Revenue = SUM(`sales_value`)
- Promo Lift = `promo_period_sales` / `baseline_sales` - 1
- Inventory Turn = `COALESING_QTY` / `average_inventory`
- Sell-through = `sold_qty` / `received_qty`

## 5. AI Layer Design

- Natural Language Understanding
  - Use LangGraph to build an AI workflow for intent and entity extraction.
  - Map phrases to analytics use cases: promotional performance, inventory movement, regional comparisons, campaign impact.

- Query Generation
  - Convert extracted intent into parameterized SQL queries or metric lookups.
  - Validate queries against allowed tables and RLS policies.

- Insight Generation
  - Use LLM calls to create narrative summaries and explain findings.
  - Automatically highlight anomalies, trends, and business impact.

- Follow-up Conversation
  - Persist conversation context in session memory.
  - Support clarifying questions, drill-downs, and chained queries.

- Executive Summaries
  - Generate short bullet-point summaries of results.
  - Include top KPIs, performance drivers, and recommended actions.

- Visualization Support
  - Detect appropriate chart types: time series, bar comparisons, heat maps, pie breakdowns.
  - Return visualization metadata for Streamlit to render.

## 6. Agent Architecture

- User Agent
  - Handles natural language input and turn-taking.
  - Maintains conversation state and follow-up references.

- Data Agent
  - Responsible for constructing queries and retrieving data.
  - Applies RLS and business filters.

- Insight Agent
  - Synthesizes results into narratives and summary insights.
  - Suggests next questions and business actions.

- Visualization Agent
  - Chooses charts and table formats.
  - Prepares metadata for frontend rendering.

- Security Agent
  - Enforces role-based access and policy validation on every request.

## 7. Deployment Architecture

- Containerization
  - Package FastAPI, LangGraph workflows, and Streamlit app as Docker containers.

- Orchestration
  - Deploy on Kubernetes or managed container service.
  - Use separate namespaces or services for backend, AI orchestration, and frontend.

- Database
  - Host PostgreSQL in managed service or self-managed cluster.
  - Use backups, replication, and monitoring.

- Auth
  - Use Supabase for user auth, roles, and row-level security.

- CI/CD
  - Use pipelines to build images, run tests, and deploy to staging/production.

- Monitoring
  - Collect app metrics, query performance, and model usage.
  - Use logging and alerting for failures.

## 8. Technology Stack Recommendations

- Python ecosystem
  - FastAPI for backend services
  - SQLAlchemy / asyncpg for database access
  - Pandas for analytics and KPI pre-processing

- AI and Orchestration
  - LangGraph to coordinate AI workflows and agents
  - OpenAI / Gemini for LLM responses and summarization

- Frontend
  - Streamlit for conversational UI and visualizations
  - Plotly or Altair for charts

- Data Storage
  - PostgreSQL for transactional and analytical data
  - Supabase for auth, policies, and realtime if needed

- Deployment
  - Docker for container packaging
  - Kubernetes or managed container platform for production deployment
  - CI/CD with GitHub Actions or equivalent

- Security and Governance
  - Supabase authentication with role-based policies
  - API gateway or service mesh for perimeter security
  - Data access logging and audit trails
