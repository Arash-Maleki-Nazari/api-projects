"""Quick start guide and deployment instructions."""

# LLM-API: Quick Start Guide

## 🚀 First Time Setup (5 minutes)

### Windows PowerShell

```powershell
# 1. Navigate to project
cd d:\Mahsa\llm-api

# 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file from template
Copy-Item .env.example .env

# 5. Edit .env and add your OpenAI API key
notepad .env
# Add: OPENAI_API_KEY=sk-your-key-here
# Add: API_KEY_SECRET=your-secret-key

# 6. Initialize database (optional for local dev)
# Database is created automatically on first run

# 7. Run the application
python -m uvicorn src.main:app --reload

# 8. Open in browser
# http://localhost:8000/docs
```

### macOS/Linux

```bash
# 1. Navigate to project
cd ~/path/to/llm-api

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env

# 5. Edit and add your OpenAI API key
nano .env
# Add: OPENAI_API_KEY=sk-your-key-here
# Add: API_KEY_SECRET=your-secret-key

# 6. Run application
python -m uvicorn src.main:app --reload

# 7. Open http://localhost:8000/docs
```

---

## 🐳 Docker Quick Start

### Prerequisites
- Docker Desktop installed
- OpenAI API key

### Commands

```bash
# 1. Navigate to project
cd d:\Mahsa\llm-api

# 2. Create .env file
copy .env.example .env
# Edit .env and add OPENAI_API_KEY and API_KEY_SECRET

# 3. Build and run with docker-compose
cd docker
docker-compose up -d

# 4. View logs
docker-compose logs -f api

# 5. Access API
# http://localhost:8000/docs

# 6. Stop services
docker-compose down
```

---

## 📝 Testing the API

### Via Swagger UI (Easiest)
1. Go to http://localhost:8000/docs
2. Authorize with API key: Click "Authorize" button, enter `your-api-key-here` in value field
3. Try endpoints:
   - POST `/api/v1/classify/category`
   - POST `/api/v1/classify/recommendation`

### Via curl

```bash
# Category Classification
curl -X POST http://localhost:8000/api/v1/classify/category \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "name": "Wireless Headphones",
    "description": "Premium wireless headphones with active noise cancellation and 30-hour battery life",
    "price": 149.99,
    "inventory": 250
  }'

# Recommendation Scoring
curl -X POST http://localhost:8000/api/v1/classify/recommendation \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "name": "Wireless Headphones",
    "description": "Premium wireless headphones with active noise cancellation and 30-hour battery life",
    "price": 149.99,
    "inventory": 250
  }'
```

---

## 🧪 Running Tests

```bash
# Install test dependencies (already in requirements.txt)
pip install -r requirements.txt

# Run all tests
pytest

# Run unit tests only
pytest tests/unit -v

# Run integration tests only
pytest tests/integration -v

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_category_classifier.py -v
```

---

## 🔧 Development Workflow

### File Structure Overview

```
src/
├── main.py                          # FastAPI app
├── core/
│   ├── settings.py                  # Config (env-based)
│   ├── logger.py                    # Structured logging
│   ├── container.py                 # Dependency injection
│   ├── llm_client.py                # OpenAI wrapper
│   └── business_rules_engine.py     # Business logic
├── database/
│   ├── models.py                    # SQLAlchemy ORM
│   ├── session.py                   # DB session
│   └── repository.py                # CRUD operations
├── services/
│   ├── category_classifier.py       # Service 1
│   └── recommendation_scorer.py     # Service 2
├── schemas/
│   ├── product.py                   # Request/response models
│   └── common.py                    # Common models
└── api/
    ├── routes/
    │   └── classify.py              # Endpoints
    └── middleware/
        └── auth.py                  # Auth middleware
```

### Adding a New Feature

1. **Add business logic** to `src/core/business_rules_engine.py`
2. **Create service** in `src/services/` using the service
3. **Define schemas** in `src/schemas/`
4. **Add endpoints** in `src/api/routes/`
5. **Write tests** in `tests/unit/` or `tests/integration/`

---

## 🚀 Production Deployment

### Environment Variables to Set

```bash
# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json

# Database (use managed service like RDS)
DATABASE_URL=postgresql://user:pass@rds-instance:5432/db

# OpenAI
OPENAI_API_KEY=sk-your-production-key

# Security
API_KEY_SECRET=strong-random-key-here
RATE_LIMIT_PER_MINUTE=100
```

### Docker Image Build

```bash
# Build image
docker build -f docker/Dockerfile -t llm-api:latest -t llm-api:v1.0.0 .

# Push to registry (e.g., DockerHub)
docker tag llm-api:latest your-registry/llm-api:latest
docker push your-registry/llm-api:latest
```

### Deploy to Cloud

**AWS ECS/Fargate Example:**
```yaml
# task-definition.json
{
  "family": "llm-api",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "llm-api",
      "image": "your-registry/llm-api:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "LOG_FORMAT", "value": "json"}
      ],
      "secrets": [
        {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:..."}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/llm-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

---

## 📊 Monitoring & Logging

### View Application Logs

```bash
# Docker logs
docker-compose logs -f api

# Uvicorn logs (local)
# Automatic when running with --reload

# JSON logs can be aggregated to:
# - ELK Stack (Elasticsearch, Logstash, Kibana)
# - AWS CloudWatch
# - DataDog
# - Splunk
```

### Key Metrics to Monitor

- Request latency (p50, p95, p99)
- LLM API call latency
- Error rate (by endpoint)
- Database connection pool usage
- API key rate limit usage

---

## ❓ Troubleshooting

### Port 8000 Already in Use

```bash
# Find process on port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 PID  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Database Connection Error

```
Error: could not translate host name "postgres" to address
```
**Solution**: Check DATABASE_URL in .env, ensure PostgreSQL is running

### OpenAI API Error

```
Error: OPENAI_API_KEY not provided
```
**Solution**: Add valid key to .env: `OPENAI_API_KEY=sk-...`

### Import Error in Tests

```
ModuleNotFoundError: No module named 'src'
```
**Solution**: Run pytest from project root: `cd d:\Mahsa\llm-api && pytest`

---

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org
- **OpenAI API**: https://platform.openai.com/docs
- **Pydantic Settings**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **Docker Compose**: https://docs.docker.com/compose

---

## 🤝 Support

For issues or questions:
1. Check logs: `docker-compose logs api`
2. Review .env configuration
3. Test with Swagger UI at `/docs`
4. Check OpenAI API status
5. Verify database connectivity

---

Last updated: 2024-01-15
