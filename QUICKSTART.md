"""
Autonomous BI System - Quick Start Guide

This guide helps you run the complete autonomous BI system with:
- FastAPI Backend (Prompts 5-8)
- Streamlit Frontend (Prompt 9)
- All services integrated
"""

# Quick Start Guide for Users

## PREREQUISITES

Before starting, ensure you have:
- Python 3.13+ installed
- pip package manager
- PostgreSQL or SQLite (backend configured)
- Administrator access to install dependencies

## INSTALLATION STEPS

### 1. Install Backend Dependencies

```bash
cd C:\Users\revan\Downloads\AI_Project\backend

# Install required packages
pip install -r requirements.txt

# Verify FastAPI installation
python -c "import fastapi; print(f'FastAPI {fastapi.__version__} installed')"
```

### 2. Install Frontend Dependencies

```bash
cd C:\Users\revan\Downloads\AI_Project\frontend

# Install Streamlit and dependencies
pip install -r requirements.txt

# Verify Streamlit installation
streamlit --version
```

### 3. Verify Database

The backend uses SQLite by default. To verify:

```bash
cd C:\Users\revan\Downloads\AI_Project\backend

# Check if database file exists
python -c "
from database import engine
from base import Base
Base.metadata.create_all(bind=engine)
print('Database initialized successfully')
"
```

## RUNNING THE SYSTEM

### Option 1: Manual Start (Separate Terminals)

**Terminal 1 - Start Backend:**

```bash
cd C:\Users\revan\Downloads\AI_Project\backend

# Start FastAPI server
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8001
# INFO:     Application startup complete
```

**Terminal 2 - Start Frontend:**

```bash
cd C:\Users\revan\Downloads\AI_Project\frontend

# Start Streamlit dashboard
streamlit run streamlit_app.py

# Expected output:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
```

### Option 2: Automated Start Script

Run this PowerShell script to start both services:

```powershell
# Stop any existing processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Start backend
Start-Process powershell -ArgumentList {
    cd 'C:\Users\revan\Downloads\AI_Project\backend'
    & 'C:\Python313\python.exe' -m uvicorn main:app --host 0.0.0.0 --port 8001
}

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend
Start-Process powershell -ArgumentList {
    cd 'C:\Users\revan\Downloads\AI_Project\frontend'
    & 'C:\Python313\python.exe' -m streamlit run streamlit_app.py
}

Write-Host "System started!"
Write-Host "Backend: http://localhost:8001"
Write-Host "Frontend: http://localhost:8501"
```

## ACCESS THE SYSTEM

Once running, access:

### Backend API
- **Health Check:** http://localhost:8001/api/v1/health
- **API Documentation:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

### Frontend Dashboard
- **Main Dashboard:** http://localhost:8501
- **Direct Access:** http://localhost:8501/?page=Dashboard

## TESTING

### Test Backend

```bash
cd C:\Users\revan\Downloads\AI_Project\backend

# Run backend tests
python test_insight_generation.py
python test_report_generation.py
python test_text_to_sql.py
```

### Test Frontend

```bash
cd C:\Users\revan\Downloads\AI_Project\frontend

# Run frontend tests
python test_frontend.py
```

### End-to-End Test

```bash
# 1. Start backend (if not running)
# 2. Run this Python script

import requests
import json

# Test backend health
response = requests.get('http://localhost:8001/api/v1/health')
print("✓ Backend health:", response.json())

# Test sample API call
response = requests.get('http://localhost:8001/api/v1/text-to-sql/samples')
print("✓ Sample queries loaded:", len(response.json().get('samples', [])))
```

## TROUBLESHOOTING

### Backend Won't Start

**Error: Address already in use**
```powershell
# Kill process using port 8001
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Then restart
```

**Error: Module not found**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Or specific package
pip install fastapi uvicorn
```

### Frontend Won't Start

**Error: Streamlit not found**
```bash
pip install streamlit
streamlit --version
```

**Error: Can't connect to backend**
- Verify backend is running: `curl http://localhost:8001/api/v1/health`
- Check firewall settings
- Update API URL in Settings page

### Database Issues

**Error: Database locked**
```bash
# Close any other connections and restart backend
```

**Error: No database file**
```bash
# Initialize database
cd backend
python main.py  # Let it auto-initialize
```

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    USER BROWSER                              │
│              http://localhost:8501                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Streamlit  │
                    │  Frontend   │
                    │  (Port 8501)│
                    └──────┬──────┘
                           │
                    ┌──────▼──────────────┐
                    │   REST API Calls    │
                    │   (HTTP Requests)   │
                    └──────┬──────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│               FastAPI Backend                                │
│              (http://localhost:8001)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  6 Core Components:                                     │ │
│  │  1. Text-to-SQL Engine (Prompt 6)                       │ │
│  │  2. Insight Generation (Prompt 7)                       │ │
│  │  3. Report Generation (Prompt 8)                        │ │
│  │  4. User Authentication                                 │ │
│  │  5. Query Processing                                    │ │
│  │  6. Data Caching                                        │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────▼──────────┐
                    │   SQLAlchemy    │
                    │     ORM         │
                    └──────┬──────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
     ┌──────▼──────┐ ┌───▼────┐ ┌──────▼────────┐
     │   SQLite    │ │ PostgreSQL   │ │   In-Memory  │
     │  (Default)  │ │              │ │   Cache      │
     └─────────────┘ └────────────┘ └──────────────┘
```

## FEATURES AVAILABLE

### Prompt 5: FastAPI Backend ✅
- RESTful API with 15+ endpoints
- JWT authentication
- Database connectivity
- Health monitoring

### Prompt 6: Text-to-SQL Engine ✅
- Natural language to SQL conversion
- Query validation
- Result interpretation
- Sample queries

### Prompt 7: Autonomous Insights ✅
- Anomaly detection
- KPI monitoring
- Opportunity finding
- Alert generation

### Prompt 8: Report Generation ✅
- Multiple report types
- 7 output formats
- Scheduled generation
- Multi-channel distribution

### Prompt 9: Streamlit Frontend ✅
- Interactive dashboard
- Real-time analytics
- Insight visualization
- Report management
- Natural language query interface

## NEXT STEPS

After Prompt 9, the system will progress to:

**Prompt 10: Autonomous Decision Agent**
- Automated recommendations
- Decision optimization
- Strategic planning
- Continuous improvement loops

## SUPPORT

For issues or questions:

1. Check troubleshooting section above
2. Review logs:
   - Backend: stdout in terminal
   - Frontend: Streamlit logs
3. Verify connectivity:
   ```bash
   curl http://localhost:8001/api/v1/health
   ```
4. Check database:
   ```bash
   python backend/main.py
   ```

## FILES AND DIRECTORIES

```
C:\Users\revan\Downloads\AI_Project\
├── backend/                          # FastAPI Backend
│   ├── main.py                      # App entry point
│   ├── database.py                  # Database config
│   ├── api/
│   │   └── routes.py                # All endpoints
│   ├── text_to_sql/                 # Prompt 6
│   ├── insight_generation/          # Prompt 7
│   ├── report_generation/           # Prompt 8
│   ├── services/
│   ├── test_*.py                    # Test suites
│   └── requirements.txt
│
└── frontend/                        # Streamlit Frontend
    ├── streamlit_app.py            # Main app
    ├── utils.py                    # Utilities
    ├── test_frontend.py            # Tests
    ├── requirements.txt
    ├── README.md
    └── .env                        # Configuration

```

## USEFUL COMMANDS

```bash
# Check backend health
curl http://localhost:8001/api/v1/health

# Get API documentation
curl http://localhost:8001/docs

# Test a query
curl -X POST http://localhost:8001/api/v1/text-to-sql/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are top products?"}'

# Clear Streamlit cache
streamlit cache clear

# Run with debug logging
streamlit run streamlit_app.py --logger.level=debug

# Run backend with auto-reload disabled
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --no-reload
```

## PERFORMANCE TIPS

1. **Backend Optimization:**
   - Use connection pooling
   - Enable query caching
   - Index frequently used columns
   - Monitor query execution time

2. **Frontend Optimization:**
   - Reduce date ranges for analytics
   - Use pagination for large datasets
   - Enable browser caching
   - Minimize API calls

3. **System Optimization:**
   - Run backend and frontend on same network
   - Use SSD for database
   - Monitor system resources
   - Enable compression on API responses

## SECURITY NOTES

1. Change default JWT secret key
2. Use HTTPS in production
3. Implement rate limiting
4. Validate all user inputs
5. Keep dependencies updated
6. Monitor access logs
7. Use environment variables for secrets
8. Enable CORS only for trusted domains

## VERSION INFO

- **System:** Autonomous BI v1.0
- **Backend:** FastAPI 0.128.0
- **Frontend:** Streamlit 1.40.1
- **Python:** 3.13+
- **Database:** SQLite/PostgreSQL
- **Date:** 2026-06-09
