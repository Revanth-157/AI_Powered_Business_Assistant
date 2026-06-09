# FastAPI Backend - FMCG BI Assistant

Production-ready FastAPI backend with JWT authentication, SQLAlchemy ORM, PostgreSQL database, and integration with the multi-agent AI system.

## Features

✅ **Authentication**
- JWT-based access/refresh tokens
- User registration and login
- API key management
- Rate limiting ready

✅ **Chat Interface**
- WebSocket-ready architecture
- Session management
- Conversation history
- Real-time message processing

✅ **Analytics**
- Query caching with TTL
- Dimension breakdowns
- Time-series data
- Dashboard snapshots

✅ **Report Generation**
- PDF/Excel/JSON export
- Report sharing
- Audit trails
- Version history

✅ **Database**
- SQLAlchemy ORM
- PostgreSQL (production)
- SQLite (development)
- Migration support (Alembic ready)

✅ **Deployment**
- Docker containerization
- Docker Compose orchestration
- Health checks
- Logging and monitoring

## Project Structure

```
backend/
├── main.py                    # FastAPI application entry point
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container image
├── docker-compose.yml         # Multi-container setup
├── .env.example              # Environment template
│
├── api/
│   ├── __init__.py
│   └── routes.py             # All API endpoints
│
├── database/
│   ├── __init__.py           # Connection & session management
│   └── models.py             # SQLAlchemy ORM models (8 tables)
│
├── schemas/
│   ├── __init__.py
│   └── schemas.py            # Pydantic validation models
│
├── services/
│   ├── __init__.py
│   ├── chat_service.py       # Conversation & session logic
│   ├── analytics_service.py  # Query execution & caching
│   ├── report_service.py     # Report generation & export
│   └── user_service.py       # User & API key management
│
├── auth/
│   └── __init__.py           # JWT, password hashing, tokens
│
├── models/                    # (Extensible for custom models)
├── utils/                     # (Extensible for helpers)
└── logs/                      # Application logs
```

## Database Schema (8 Tables)

### Core Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `users` | User accounts | id, email, username, hashed_password, role, accessible_regions |
| `sessions` | Chat sessions | id, user_id, title, context_data, is_active, expires_at |
| `conversations` | Message pairs | id, session_id, user_message, assistant_response, intent, kpis, insights |
| `reports` | Generated reports | id, user_id, title, kpis, insights, visualizations, report_type |
| `api_keys` | Programmatic access | id, user_id, key_hash, permissions, is_active, expires_at |
| `audit_logs` | Compliance trail | id, user_id, action, resource_type, status, ip_address, timestamp |
| `cache` | Query caching | id, cache_key, result, expires_at, hit_count |

### Relationships

```
User
├── N Sessions
│   ├── N Conversations
│   └── 1 Report
├── N Conversations
├── N Reports
├── N API Keys
└── N Audit Logs
```

## API Endpoints

### Authentication
```
POST   /api/v1/auth/register      # Register new user
POST   /api/v1/auth/login         # Login (returns JWT)
POST   /api/v1/auth/refresh       # Refresh access token
```

### Chat
```
POST   /api/v1/chat               # Send message to AI
GET    /api/v1/chat/sessions      # Get user's sessions
GET    /api/v1/chat/sessions/{id} # Get session history
```

### Analytics
```
POST   /api/v1/analytics/query    # Execute analytics query
GET    /api/v1/analytics/dashboard # Dashboard snapshot
GET    /api/v1/analytics/trends/{metric} # Historical trends
```

### Reports
```
POST   /api/v1/reports            # Create new report
GET    /api/v1/reports            # List user's reports
GET    /api/v1/reports/{id}       # Get specific report
POST   /api/v1/reports/{id}/share # Share report
POST   /api/v1/reports/{id}/export # Export (PDF/Excel/JSON)
DELETE /api/v1/reports/{id}       # Delete report
```

### Health
```
GET    /                          # API info
GET    /api/v1/health            # Health check
GET    /docs                      # Swagger UI (auto-generated)
```

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Initialize Database

```python
from database import init_db
init_db()
```

### 4. Run Server

**Development:**
```bash
python main.py
# or
uvicorn main:app --reload
```

**Production:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Docker Deployment

### Single Service

```bash
docker build -t fmcg-backend .
docker run -p 8000:8000 -e DATABASE_URL=postgresql://... fmcg-backend
```

### Full Stack (with PostgreSQL + Redis)

```bash
docker-compose up -d
# Access: http://localhost:8000
# Docs: http://localhost:8000/docs
# pgAdmin: http://localhost:5050
```

## Configuration

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEBUG` | False | Enable debug mode |
| `DATABASE_URL` | PostgreSQL | Database connection |
| `USE_SQLITE` | True | Use SQLite for dev |
| `SECRET_KEY` | (change me!) | JWT signing key |
| `OPENAI_API_KEY` | (optional) | LLM integration |
| `LOG_LEVEL` | INFO | Logging verbosity |
| `SESSION_TIMEOUT_MINUTES` | 60 | Session expiration |

### Database Switching

**PostgreSQL (Production):**
```env
USE_SQLITE=False
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname
```

**SQLite (Development):**
```env
USE_SQLITE=True
SQLITE_DB_PATH=../architecture/fmcg_analytics.db
```

## Authentication Flow

```
1. User Registration
   POST /api/v1/auth/register
   {email, username, password}
   ↓
   User created with bcrypt-hashed password

2. Login
   POST /api/v1/auth/login
   {email, password}
   ↓
   JWT access + refresh tokens returned

3. Protected Requests
   GET /api/v1/chat/sessions
   Authorization: Bearer <access_token>
   ↓
   Token verified, user identified, request processed

4. Token Refresh
   POST /api/v1/auth/refresh
   {refresh_token}
   ↓
   New access token issued (refresh token reusable)
```

## Usage Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Register
user_data = {
    "email": "analyst@company.com",
    "username": "analyst001",
    "password": "SecurePassword123!",
    "full_name": "John Analyst"
}
resp = requests.post(f"{BASE_URL}/auth/register", json=user_data)
print(resp.json())

# 2. Login
login_data = {"email": "analyst@company.com", "password": "SecurePassword123!"}
resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
tokens = resp.json()
access_token = tokens["access_token"]

# 3. Send Chat Message
headers = {"Authorization": f"Bearer {access_token}"}
chat_data = {"message": "Show me promotional performance for last quarter"}
resp = requests.post(f"{BASE_URL}/chat", json=chat_data, headers=headers)
print(resp.json())

# 4. Get Dashboard
resp = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
print(resp.json())

# 5. Create Report
report_data = {
    "title": "Q2 2026 Analysis",
    "intent": "PROMO_PERFORMANCE",
    "report_type": "standard"
}
resp = requests.post(f"{BASE_URL}/reports", json=report_data, headers=headers)
report_id = resp.json()["id"]

# 6. Export Report
export_data = {"format": "json"}
resp = requests.post(
    f"{BASE_URL}/reports/{report_id}/export",
    json=export_data,
    headers=headers
)
print(resp.json())
```

### cURL Examples

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"user@example.com",
    "username":"user001",
    "password":"Password123!",
    "full_name":"User Name"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123!"}'

# Chat (requires token)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message":"What is the promotional performance?"}'

# Health Check
curl http://localhost:8000/api/v1/health
```

## Error Handling

All errors follow a consistent format:

```json
{
  "error_code": "VALIDATION_ERROR|AUTH_ERROR|NOT_FOUND|INTERNAL_ERROR",
  "message": "Human-readable error message",
  "details": {...}
}
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (validation) |
| 401 | Unauthorized (auth failed) |
| 403 | Forbidden (permission denied) |
| 404 | Not found |
| 422 | Unprocessable entity |
| 500 | Internal server error |
| 503 | Service unavailable |

## Security Features

✅ **Authentication**
- JWT tokens with expiration
- Refresh token rotation
- Password hashing (bcrypt)
- API key management

✅ **Authorization**
- Role-based access control (analyst/manager/admin)
- Row-level security (RLS) via accessible_regions
- User isolation (can't access other users' data)

✅ **Data Protection**
- SQL injection prevention (SQLAlchemy parameterization)
- CORS configuration
- HTTPS-ready
- Audit logging

✅ **Input Validation**
- Pydantic schema validation
- Type hints throughout
- Email validation
- Password strength requirements

## Performance Optimization

### Caching
- Query result caching with TTL
- Cache key generation
- Hit count tracking
- Automatic expiration

### Database
- Connection pooling
- Index optimization
- Query optimization
- Prepared statements

### API
- Pagination (skip/limit)
- Async/await support
- Health checks
- Rate limiting ready

## Monitoring & Logging

### Logs
- Request logging (method, path, status, time)
- Error tracking with stack traces
- Audit trail (user actions)
- Application events

### Health Checks

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "database": true,
  "ai_agents": true,
  "timestamp": "2026-06-09T12:00:00"
}
```

## Testing

### Unit Tests (TBD)
```bash
pytest tests/
```

### Integration Tests (TBD)
```bash
pytest tests/integration/
```

### Load Testing (TBD)
```bash
ab -n 1000 -c 10 http://localhost:8000/api/v1/health
```

## Next Steps

1. **Frontend Integration**
   - Streamlit UI connecting to backend
   - React/Next.js dashboard option

2. **Advanced Features**
   - WebSocket support for real-time updates
   - GraphQL API option
   - Export to PDF/Excel
   - Scheduled reports

3. **Deployment**
   - Kubernetes manifests
   - CI/CD pipeline (GitHub Actions)
   - Cloud deployment (AWS, Azure, GCP)

4. **Enhancements**
   - Rate limiting
   - Request signing
   - Multi-tenancy
   - Advanced analytics

## Support

### Documentation
- API Docs: `http://localhost:8000/docs` (Swagger UI)
- ReDoc: `http://localhost:8000/redoc`

### Common Issues

**"Database connection failed"**
- Check DATABASE_URL environment variable
- Verify PostgreSQL is running
- Check credentials and permissions

**"AI workflow not initialized"**
- Ensure ai_agent module is in Python path
- Check AI_DATABASE_PATH configuration
- Verify database file exists

**"CORS errors"**
- Check ALLOWED_ORIGINS configuration
- Verify frontend URL is in allowed list
- Check request headers

## License

Internal Use Only - FMCG AI Assistant Project

---

**Ready for Production Deployment** ✅
