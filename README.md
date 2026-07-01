# API Projects

This repository contains backend API projects focused on APIs, databases, authentication, Docker, and LLM integrations.

## Overview

The goal of this repository is to keep API-based projects organized in one place. Each project has its own folder, source code, documentation, tests, and setup files.

The current project is `llm-api`, a FastAPI backend for product labeling and recommendation scoring.

## Projects

### llm-api

`llm-api` is a FastAPI product labeling API that combines rule-based business logic with optional LLM enrichment.

The API receives product information such as name, description, price, and inventory. It then returns category classification, recommendation scoring, applied business rules, and optional LLM-generated insights.

Main features:

- FastAPI REST API
- Product category classification
- Recommendation scoring
- Rule-based business logic
- Optional LLM enrichment
- PostgreSQL database support
- SQLAlchemy ORM models
- API key authentication
- Docker setup
- Unit and integration tests
- Swagger/OpenAPI documentation

Project folder:

```text
llm-api/
```

## Repository Structure

```text
api-projects/
├── README.md
├── .gitignore
└── llm-api/
    ├── README.md
    ├── QUICKSTART.md
    ├── PROJECT_SUMMARY.md
    ├── requirements.txt
    ├── pytest.ini
    ├── .env.example
    ├── .gitignore
    ├── docker/
    │   ├── Dockerfile
    │   └── docker-compose.yml
    ├── src/
    │   ├── main.py
    │   ├── api/
    │   │   ├── middleware/
    │   │   │   ├── auth.py
    │   │   │   └── __init__.py
    │   │   └── routes/
    │   │       ├── classify.py
    │   │       └── __init__.py
    │   ├── core/
    │   │   ├── business_rules_engine.py
    │   │   ├── container.py
    │   │   ├── llm_client.py
    │   │   ├── logger.py
    │   │   ├── settings.py
    │   │   └── __init__.py
    │   ├── database/
    │   │   ├── models.py
    │   │   ├── repository.py
    │   │   ├── session.py
    │   │   └── __init__.py
    │   ├── schemas/
    │   │   ├── common.py
    │   │   ├── product.py
    │   │   └── __init__.py
    │   └── services/
    │       ├── category_classifier.py
    │       ├── recommendation_scorer.py
    │       └── __init__.py
    └── tests/
        ├── conftest.py
        ├── __init__.py
        ├── integration/
        │   └── test_endpoints.py
        └── unit/
            ├── test_business_rules_engine.py
            ├── test_category_classifier.py
            └── test_recommendation_scorer.py
```

## Branch Strategy

- `main` — stable working version
- `feature/*` — experiments, improvements, or alternative implementations

Example future branches:

```text
feature/ollama-llm
feature/huggingface-llm
feature/sqlite-db
feature/azure-openai
feature/docker-improvements
```

## Security Notes

Sensitive files are not committed to this repository.

Do not commit:

```text
.env
API keys
database passwords
personal access tokens
venv/
__pycache__/
local database files
```

Only safe templates such as `.env.example` should be committed.

## Git Workflow

Check changes:

```bash
git status
```

Stage changes:

```bash
git add .
```

Commit changes:

```bash
git commit -m "Describe the change"
```

Push to GitHub:

```bash
git push
```

Pull latest changes:

```bash
git pull
```

## Current Status

The `llm-api` project is set up as a local FastAPI backend with PostgreSQL, Docker support, API authentication, business rules, and optional LLM integration.

Future work may include adding support for different LLM providers, different databases, deployment workflows, and CI/CD.