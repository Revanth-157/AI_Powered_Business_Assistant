# AI-Powered FMCG Business Intelligence Assistant

A polished, multi-agent AI platform for FMCG analytics that turns plain English business questions into actionable insights. This project helps teams explore sales, promotions, inventory, and product performance using natural language, AI-generated SQL, smart analysis, visual dashboards, and executive-ready reports.

![Project Banner](https://img.shields.io/badge/Status-Complete-brightgreen) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Ready-009688) ![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-ff4b4b)

---

## Why this project matters

Modern retail and FMCG teams often struggle with fragmented data, slow manual reporting, and the need for fast business answers. This project solves that by combining:

- Natural language querying
- AI-driven SQL generation
- Automated analytics and forecasting-style insight detection
- Interactive dashboards
- Executive report generation

In short, it acts like a smart business analyst that is available 24/7.

---

## What this system can do

### Core capabilities
- Ask questions in plain English such as:
  - “What was promotional performance last week?”
  - “Show regional sales comparison for the last quarter.”
  - “Which products are underperforming?”
  - “What inventory risks should we act on?”
- Convert those questions into safe, structured SQL queries
- Run analytics over synthetic FMCG business data
- Detect anomalies, opportunities, and alerts
- Generate visualizations and business-friendly summaries
- Produce report-ready outputs for stakeholders

### What makes it impressive
- Built as a multi-agent AI workflow
- Uses a clear orchestration layer for reasoning and execution
- Designed to be extended into a production-grade analytics product
- Includes both a Python-based agent workflow and a web dashboard experience

---

## Project highlights

### 1. Intelligent multi-agent workflow
The project is organized around a workflow where specialized agents handle different tasks:
- Query understanding
- SQL generation
- Analytics execution
- Insight detection
- Visualization generation
- Report assembly

### 2. FMCG-focused dataset
The project includes a rich synthetic dataset with:
- Products
- Stores
- Sales and promotion data
- Inventory information
- Multi-region business context

### 3. Full-stack-ready architecture
The repository contains:
- A Python-based AI engine
- A FastAPI backend
- A Streamlit frontend
- Database creation and schema utilities
- Documentation and deployment assets

---

## Tech stack

### AI & analytics
- Python
- LangGraph-style multi-agent orchestration
- SQL generation and analysis logic
- Data processing with pandas and numpy

### Backend
- FastAPI
- Pydantic
- SQLAlchemy
- JWT-based authentication structure
- REST API routes for analytics and reporting

### Frontend
- Streamlit
- Plotly
- Interactive dashboard experience

### Data layer
- SQLite for local development
- PostgreSQL-ready schema and architecture files

---

## Repository structure

```text
AI_Project/
├── ai_agent/              # Multi-agent reasoning workflow
├── backend/               # FastAPI API backend
├── frontend/              # Streamlit dashboard UI
├── architecture/          # Database schema and setup scripts
├── data/                  # Synthetic FMCG dataset generation
├── docs and guides/       # Setup and architecture documentation
└── README.md              # Project overview
```

---

## Quick start

### Option 1: Run the AI agent demo
This is the fastest way to see the core product in action.

```bash
cd AI_Project
python -m ai_agent.main
```

This will run example business questions through the workflow and print AI-generated responses.

### Option 2: Run the interactive assistant
```bash
cd AI_Project
python -m ai_agent.main interactive
```

You can type questions directly into the terminal and continue the conversation.

### Option 3: Launch the dashboard experience
Start the backend first, then open the frontend UI.

#### Backend
```bash
cd AI_Project/backend
python main.py
```

#### Frontend
```bash
cd AI_Project/frontend
streamlit run streamlit_app.py
```

Then open:
- Backend API docs: http://localhost:8000/docs
- Streamlit dashboard: http://localhost:8501

> If the frontend cannot connect to the backend, make sure the backend is running on the same URL expected by the Streamlit app.

---

## Example use cases

This project is ideal for:
- Sales analysts who need quick business summaries
- Marketing teams evaluating promotions
- Supply chain and inventory managers tracking stock risks
- Leadership teams who want concise reports and KPI snapshots
- Data teams building AI-powered analytics assistants

---

## Example questions you can try

- “Show me regional sales comparison for the last quarter.”
- “What products performed best last month?”
- “Which stores are showing unusual inventory movement?”
- “How did promotions affect revenue?”
- “Give me a dashboard snapshot of key metrics.”

---

## Architecture at a glance

```text
User Question
   ↓
AI Agent Workflow
   ↓
SQL + Analytics + Insights
   ↓
Visualization + Report Generation
   ↓
Business-ready response
```

This makes the project feel less like a simple script and more like an intelligent BI assistant.

---

## What makes this project special

- It combines AI reasoning with real business analytics use cases
- It is structured for both experimentation and future production scaling
- It turns complex data analysis into simple conversational interactions
- It is a strong foundation for building a real-world enterprise analytics assistant

---

## Future potential

This project can be expanded into:
- A production SaaS analytics product
- A chatbot for business users
- A custom internal BI copilot for organizations
- A reporting and insight automation platform
- A multi-tenant enterprise analytics system

---

## License

This project is intended for educational, experimental, and business demonstration purposes.

---

## Final note

If you are looking for a project that blends AI, data, automation, and business intelligence into something impressive and practical, this repository is a strong example of that vision.

