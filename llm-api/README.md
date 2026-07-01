# LLM-based Product Labeling API

FastAPI service for e-commerce product categorization and recommendation scoring using deterministic business rules with optional LLM enrichment.

## Features

- FastAPI REST API
- API key authentication with `X-API-Key`
- PostgreSQL database integration
- SQLAlchemy ORM models
- Rule-based product classification
- Rule-based recommendation scoring
- Optional LLM enrichment using an OpenAI-compatible API
- Structured logging
- Docker support
- Unit and integration tests
- Swagger/OpenAPI documentation

## Project Structure

```text
llm-api/
├── src/
│   ├── main.py
│   ├── api/
│   │   ├── middleware/
│   │   │   └── auth.py
│   │   └── routes/
│   │       └── classify.py
│   ├── core/
│   │   ├── business_rules_engine.py
│   │   ├── container.py
│   │   ├── llm_client.py
│   │   ├── logger.py
│   │   └── settings.py
│   ├── database/
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── session.py
│   ├── schemas/
│   │   ├── common.py
│   │   └── product.py
│   └── services/
│       ├── category_classifier.py
│       └── recommendation_scorer.py
├── tests/
├── docker/
├── requirements.txt
├── .env.example
├── QUICKSTART.md
├── PROJECT_SUMMARY.md
└── README.md
```

## Tech Stack

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- PostgreSQL
- Docker
- OpenAI Python SDK
- Pytest

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Arash-Maleki-Nazari/llm-api.git
cd llm-api/llm-api
```

### 2. Create and activate a virtual environment

Windows:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file:

```bash
cp .env.example .env
```

Example `.env`:

```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

DATABASE_URL=postgresql://labeling_user:labeling_password@127.0.0.1:5433/labeling_db

OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2
OPENAI_MAX_TOKENS=500

API_KEY_SECRET=my-local-api-key
RATE_LIMIT_PER_MINUTE=100

LOG_FORMAT=json
```

Do not commit `.env` to GitHub.

### 5. Start PostgreSQL with Docker

```powershell
docker run --name llm-api-postgres `
  -e POSTGRES_USER=labeling_user `
  -e POSTGRES_PASSWORD=labeling_password `
  -e POSTGRES_DB=labeling_db `
  -p 5433:5432 `
  -d postgres:16-alpine
```

### 6. Run the API

```bash
python -m uvicorn src.main:app --reload
```

Open Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## Authentication

Protected endpoints require this header:

```text
X-API-Key: my-local-api-key
```

The value must match `API_KEY_SECRET` in `.env`.

## API Endpoints

### Health Check

```http
GET /health
```

### Category Classification

```http
POST /api/v1/classify/category
```

Example request:

```json
{
  "name": "Sony WH-1000XM5 Wireless Headphones",
  "description": "Premium wireless headphones with active noise cancellation, long battery life, comfortable design, and high-quality sound for travel, study, and office work.",
  "price": 349.99,
  "inventory": 120
}
```

Example response:

```json
{
  "status": "success",
  "data": {
    "primary_category": "premium",
    "confidence": 0.8,
    "tags": [],
    "applied_rules": ["price_tier_rule"],
    "llm_enhancement": {
      "subcategory": "wireless headphones",
      "quality_assessment": "excellent",
      "recommended_marketing_angle": "Premium noise cancellation and comfort for travel and work",
      "potential_customer_segment": "professionals, commuters, students, and frequent travelers"
    },
    "processing_time_ms": 2500.4,
    "error": null
  },
  "trace_id": "example-trace-id",
  "timestamp": "2026-07-01T11:08:15.812460"
}
```

If the LLM provider is unavailable, the API still returns the rule-based result:

```json
{
  "status": "success",
  "data": {
    "primary_category": "premium",
    "confidence": 0.8,
    "tags": [],
    "applied_rules": ["price_tier_rule"],
    "llm_enhancement": null,
    "processing_time_ms": 12470.6,
    "error": "OpenAI rate limit/quota error: insufficient_quota"
  }
}
```

### Recommendation Scoring

```http
POST /api/v1/classify/recommendation
```

Example request:

```json
{
  "name": "Wireless Headphones",
  "description": "Premium wireless headphones with active noise cancellation and long battery life.",
  "price": 149.99,
  "inventory": 250
}
```

## Business Rules

### Category Classification

Price tier:

```text
price < 50          -> budget
50 <= price <= 200  -> mid-range
price > 200         -> premium
```

Inventory:

```text
inventory > 1000 -> high-stock
inventory < 10   -> low-stock, trigger-reorder
```

Description:

```text
description length > 500 characters -> detailed-description
```

### Recommendation Scoring

Base score:

```text
50
```

Adjustments:

```text
mid-range or premium price -> +15
high inventory             -> +10
low inventory              -> -20
detailed description        -> +20
new product                 -> +15
```

A product is recommended when:

```text
final_recommendation_score >= 60
```

## Testing

Run unit tests:

```bash
pytest tests/unit -v
```

Run integration tests:

```bash
pytest tests/integration -v
```

Run all tests:

```bash
pytest -v
```

## LLM Integration

The project uses the OpenAI Python SDK.

The LLM step is optional. Business rules are evaluated first, then the app attempts LLM enrichment. If the LLM provider fails, the API falls back to rule-based output.

Common LLM failure causes:

```text
invalid API key
missing API quota
billing not enabled
model not available
provider timeout
local LLM server not running
```

## Security Notes

Do not commit:

```text
.env
venv/
__pycache__/
API keys
database passwords
personal tokens
```

Commit only safe templates such as:

```text
.env.example
```

## Troubleshooting

### `llm_enhancement` is null

The LLM provider failed or is unavailable. Check the `error` field in the API response and the Uvicorn logs.

### OpenAI insufficient quota

The OpenAI API requires available API quota or billing. A ChatGPT subscription does not automatically provide API credits.

The API still works without LLM enrichment because rule-based classification does not require OpenAI.

### API key required

Add the API key header:

```text
X-API-Key: my-local-api-key
```

### Invalid API key

The value in the request header does not match `API_KEY_SECRET` in `.env`.

### Database connection failed

Check that PostgreSQL is running:

```bash
docker ps
```

Check that `.env` uses the correct database URL:

```env
DATABASE_URL=postgresql://labeling_user:labeling_password@127.0.0.1:5433/labeling_db
```

### Port already in use

Stop the existing Python process or use a different port.

Windows:

```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

## Future Improvements

- Add configurable local LLM support with Ollama
- Add Hugging Face provider support
- Add Azure OpenAI configuration
- Add Redis caching
- Add Alembic database migrations
- Add GitHub Actions CI
- Add deployment guide
- Improve test coverage for LLM failure modes

