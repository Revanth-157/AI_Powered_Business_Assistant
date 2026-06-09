# FastAPI Backend - Deployment Guide

**Quick Start: Get the backend running in 5 minutes**

---

## Prerequisites

✅ Docker and Docker Compose installed  
✅ Python 3.13 (for direct execution)  
✅ Port 8000, 5432 available (or modify docker-compose.yml)

---

## Option 1: Docker Compose (Recommended - 2 minutes)

### Step 1: Navigate to Backend
```bash
cd c:\Users\revan\Downloads\AI_Project\backend
```

### Step 2: Create Environment File
```bash
copy .env.example .env
```

### Step 3: Start Services
```bash
docker-compose up -d
```

### Step 4: Verify
```bash
docker logs fmcg_backend
# Should show: "Application startup complete"

# Test health
curl http://localhost:8000/api/v1/health
```

### Access Points
- **API Swagger Docs:** http://localhost:8000/docs
- **Database Admin:** http://localhost:5050 (pgAdmin - admin/admin)
- **API Health:** http://localhost:8000/api/v1/health

### Stop Services
```bash
docker-compose down
```

---

## Option 2: Direct Python (Dev Only - 3 minutes)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Create Environment File
```bash
copy .env.example .env
# Modify .env for SQLite (default):
# USE_SQLITE=True
# SQLITE_DB_PATH=../architecture/fmcg_analytics.db
```

### Step 3: Run Server
```bash
python main.py
```

Server runs on: http://localhost:8000

---

## Option 3: Production (Kubernetes)

### Generate manifests (recommended next step):
```bash
# Use Helm or manual K8s YAML
kubectl apply -f k8s/deployment.yaml
```

---

## Testing

### Run Test Suite
```bash
cd backend
python test_backend.py
```

Expected: 10/10 tests passing ✅

### Manual Test
```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@test.com",
    "username": "testuser",
    "password": "Test123456",
    "full_name": "Test User"
  }'

# 2. Login (copy access_token)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Test123456"}'

# 3. Chat
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message":"What is the promotional performance?"}'
```

---

## Configuration

### Development
```env
DEBUG=True
USE_SQLITE=True
LOG_LEVEL=DEBUG
```

### Production
```env
DEBUG=False
USE_SQLITE=False
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/fmcg_ai
SECRET_KEY=<generate-random-key>
OPENAI_API_KEY=sk-...
```

---

## Troubleshooting

### "Connection refused"
```
Issue: Backend won't connect to database
Fix: 
  1. Verify PostgreSQL is running: docker ps | grep postgres
  2. Check DATABASE_URL in .env
  3. Verify credentials
```

### "Module not found: ai_agent"
```
Issue: AI agents not available
Fix:
  1. Verify AI_DATABASE_PATH in .env
  2. AI workflow won't initialize, but backend still works
  3. Chat/Analytics endpoints will return 503 (Service Unavailable)
```

### "Port 8000 already in use"
```
Issue: Another process using port 8000
Fix:
  # Find process
  lsof -i :8000
  # Kill process or change port in docker-compose.yml
```

---

## Health Checks

```bash
# Check if backend is running
curl http://localhost:8000/api/v1/health

# Response indicates:
# "status": "healthy" - All systems go
# "database": true - DB connected
# "ai_agents": true - AI workflow available
```

---

## Common Commands

```bash
# View logs
docker logs -f fmcg_backend

# Stop backend
docker-compose down

# Stop with volume cleanup
docker-compose down -v

# Rebuild after code changes
docker-compose down
docker-compose build
docker-compose up -d

# Access database shell
docker exec -it fmcg_postgres psql -U postgres -d fmcg_ai

# Check running containers
docker-compose ps
```

---

## Next Steps

1. ✅ **Backend Running** - Confirm with health check
2. 🔄 **Frontend Integration** - Build Streamlit or React UI
3. 🔄 **LLM Integration** - Add OpenAI API key to .env
4. 🔄 **Production Deployment** - Move to cloud/on-premises

---

## Support

### Documentation
- Full API docs: http://localhost:8000/docs (Swagger UI)
- Backend README: `backend/README.md`
- Implementation summary: `BACKEND_IMPLEMENTATION_SUMMARY.md`

### Check Issues
1. Backend logs: `docker logs fmcg_backend`
2. Database logs: `docker logs fmcg_postgres`
3. Test suite: `python test_backend.py`

---

**Ready to deploy?** 🚀

```bash
cd backend
docker-compose up -d
```

Then visit: **http://localhost:8000/docs**

