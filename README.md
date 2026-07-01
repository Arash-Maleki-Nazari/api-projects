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


