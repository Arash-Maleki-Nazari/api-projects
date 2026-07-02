# Quick Start

This guide explains how to run the API locally.

## Prerequisites

- Python 3.11
- Docker Desktop
- Git
- PostgreSQL through Docker
- Optional: OpenAI API key for LLM enrichment

## 1. Clone the repository

```bash
git clone https://github.com/Arash-Maleki-Nazari/api-projects.git
cd api-projects/llm-api
```

## 2. Create a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3.11 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Create environment file

```powershell
Copy-Item .env.example .env
```

Edit `.env` and use this local setup:

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

If no OpenAI API quota is available, the API still runs with rule-based classification. LLM enrichment will be skipped.

## 5. Start PostgreSQL with Docker

```powershell
docker run --name llm-api-postgres `
  -e POSTGRES_USER=labeling_user `
  -e POSTGRES_PASSWORD=labeling_password `
  -e POSTGRES_DB=labeling_db `
  -p 5433:5432 `
  -d postgres:16-alpine
```

If the container already exists, start it with:

```powershell
docker start llm-api-postgres
```

Check it is running:

```powershell
docker ps --filter "name=llm-api-postgres"
```

## 6. Run the API

```bash
python -m uvicorn src.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## 7. Authenticate in Swagger

Click `Authorize` and enter:

```text
my-local-api-key
```

This value must match `API_KEY_SECRET` in `.env`.

## 8. Test the API

### Category Classification

Endpoint:

```text
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

### Recommendation Scoring

Endpoint:

```text
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

### RAG Search

Available on the RAG feature branch:

```text
feature/rag-vector-db
```

Endpoint:

```text
POST /api/v1/rag/search
```

Example request:

```json
{
  "query": "What makes a product premium?",
  "top_k": 3
}
```

## 9. Run tests

```bash
pytest
```

Run unit tests:

```bash
pytest tests/unit -v
```

Run integration tests:

```bash
pytest tests/integration -v
```

## Notes

Do not commit `.env`, API keys, virtual environments, or local database files.

Only `.env.example` should be committed.