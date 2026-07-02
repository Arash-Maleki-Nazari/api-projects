# Project Summary

## LLM-based Product Labeling API

This project is a FastAPI backend for e-commerce product classification and recommendation scoring.

It combines rule-based business logic with optional LLM enrichment. The API can classify products by price tier, inventory level, and description quality, then optionally use an LLM to add marketing insights such as subcategory, quality assessment, target audience, and selling angle.

## Main Features

- FastAPI REST API
- Product category classification
- Recommendation scoring
- Rule-based business logic
- Optional LLM enrichment
- PostgreSQL database integration
- SQLAlchemy ORM models
- API key authentication
- Docker support
- Unit and integration tests
- Swagger/OpenAPI documentation

## Current AI / LLM Work

Implemented:

- OpenAI-compatible LLM API integration
- Structured JSON response handling
- LLM error handling and fallback behavior
- Local RAG/vector search branch using ChromaDB and SentenceTransformers

In progress:

- RAG API endpoint for searching local knowledge-base documents

Future work:

- Ollama local LLM support
- Hugging Face integration
- LangChain workflow branch
- pgvector/PostgreSQL vector search

## Tech Stack

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- PostgreSQL
- Docker
- OpenAI Python SDK
- ChromaDB
- SentenceTransformers
- Pytest

## API Endpoints

- `GET /health`
- `POST /api/v1/classify/category`
- `POST /api/v1/classify/recommendation`
- `POST /api/v1/rag/search` on the RAG feature branch

## What This Project Demonstrates

- Backend API design with FastAPI
- Clean service-layer architecture
- Business rule implementation
- LLM API integration
- RAG/vector search fundamentals
- PostgreSQL integration
- Docker-based local development
- Git branching for experimental features
- API documentation and testing

## Status

The main API is working locally with PostgreSQL, authentication, rule-based classification, and optional LLM enrichment.

The `feature/rag-vector-db` branch adds local RAG/vector search using ChromaDB and SentenceTransformers.