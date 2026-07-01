# LLM-based Product Labeling API

Production-grade FastAPI service for intelligent e-commerce product categorization and recommendation scoring using a hybrid approach of deterministic business rules and GPT-4 LLM.

## Features

- **Two Specialized Services**
  - **CategoryClassifier**: Categorizes products (budget/mid-range/premium) with tags (high-stock, low-stock, detailed-description)
  - **RecommendationScorer**: Scores products (0-100) for recommendation viability with marketing insights

- **Hybrid Approach**: Fast deterministic rules + LLM enrichment for nuanced insights
- **Production-Ready**: Structured logging, API authentication, error handling, Docker support
- **Dependency Injection**: Clean architecture with inversion of control
- **FastAPI**: Modern async Python web framework with auto-generated OpenAPI docs
- **SQLAlchemy ORM**: Type-safe database access with PostgreSQL
- **Configurable**: Pydantic Settings for environment-based configuration

## Project Structure

```
llm-api/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── core/                   # Core utilities
│   │   ├── settings.py         # Pydantic settings with env support
│   │   ├── logger.py           # Structured JSON logging
│   │   ├── container.py        # Dependency injection
│   │   ├── llm_client.py       # OpenAI wrapper with retry logic
│   │   └── business_rules_engine.py  # Rule evaluation engine
│   ├── database/               # Database layer
│   │   ├── models.py           # SQLAlchemy ORM models
│   │   ├── session.py          # DB session management
│   │   └── repository.py       # CRUD operations
│   ├── services/               # Business logic
│   │   ├── category_classifier.py    # Category classification service
│   │   └── recommendation_scorer.py  # Recommendation scoring service
│   ├── schemas/                # Pydantic request/response models
│   │   ├── product.py          # Product schemas
│   │   └── common.py           # Common response schemas
│   └── api/                    # API layer
│       ├── routes/
│       │   └── classify.py     # Classification endpoints
│       └── middleware/
│           └── auth.py         # API key authentication
├── tests/                      # Test suite (unit & integration)
├── docker/                     # Docker configuration
│   ├── Dockerfile              # Multi-stage production build
│   └── docker-compose.yml      # Local dev environment
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 12+ (or use Docker)
- OpenAI API key
- Docker & Docker Compose (optional, for containerized setup)

### Local Development Setup

1. **Clone and setup environment**
   ```bash
   cd d:\Mahsa\llm-api
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key and database URL
   ```

4. **Run with Uvicorn (local)**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Visit: http://localhost:8000/docs for interactive API documentation

### Docker Setup

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

2. **Build and run with docker-compose**
   ```bash
   cd docker
   docker-compose up -d
   ```

   API will be available at: http://localhost:8000/docs

3. **Stop services**
   ```bash
   docker-compose down
   ```

## API Endpoints

### Health Check
```bash
GET /health
```

### Category Classification
```bash
POST /api/v1/classify/category
Content-Type: application/json
X-API-Key: your-api-key

{
  "name": "Wireless Headphones",
  "description": "Premium wireless headphones with active noise cancellation...",
  "price": 149.99,
  "inventory": 250,
  "created_date": "2024-01-01"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "primary_category": "mid-range",
    "confidence": 0.85,
    "tags": ["detailed-description", "high-stock"],
    "applied_rules": ["price_tier_rule", "inventory_level_rule"],
    "llm_enhancement": {
      "subcategory": "electronics",
      "quality_assessment": "excellent",
      "recommended_marketing_angle": "premium sound quality",
      "potential_customer_segment": "audiophiles, professionals"
    },
    "processing_time_ms": 1250.5
  },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Recommendation Scoring
```bash
POST /api/v1/classify/recommendation
Content-Type: application/json
X-API-Key: your-api-key

{
  "name": "Wireless Headphones",
  "description": "Premium wireless headphones...",
  "price": 149.99,
  "inventory": 250
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "base_score": 75,
    "final_recommendation_score": 80,
    "score_breakdown": {
      "base_score": 50,
      "price_tier_bonus": 15,
      "inventory_bonus": 10,
      "description_bonus": 20
    },
    "is_recommended": true,
    "recommendation_reason": "Excellent product with strong market demand",
    "target_audience": "Tech professionals and audiophiles",
    "key_selling_points": ["Noise cancellation", "Long battery life", "Premium build"],
    "applied_rules": ["price_rule", "inventory_rule", "description_rule"],
    "score_adjustment_from_llm": 5,
    "llm_enhancement": true,
    "processing_time_ms": 1500.25
  },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Configuration

### Environment Variables

```env
# Application
ENVIRONMENT=development              # development, staging, production
DEBUG=true                            # Enable debug mode
LOG_LEVEL=INFO                       # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json                      # json or text

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/labeling_db

# OpenAI / LLM
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4                   # LLM model to use
OPENAI_TEMPERATURE=0.7               # LLM temperature (0-1)
OPENAI_MAX_TOKENS=500                # Max tokens per LLM response

# API Security
API_KEY_SECRET=your-api-key          # API key for authentication
RATE_LIMIT_PER_MINUTE=100            # Rate limiting per API key
```

## Business Rules

### Category Classification Rules

1. **Price Tier Rule**
   - Price < $50 → "budget"
   - $50 ≤ Price ≤ $200 → "mid-range"
   - Price > $200 → "premium"

2. **Inventory Level Rule**
   - Inventory > 1000 → add "high-stock" tag
   - Inventory < 10 → add "low-stock" and "trigger-reorder" tags

3. **Description Quality Rule**
   - Description length > 500 chars → add "detailed-description" tag

### Recommendation Scoring Rules

**Base Score: 50**

- Price Tier Bonus: +15 if mid-range or premium
- Inventory Bonus: +10 if high-stock; -20 if low-stock
- Description Bonus: +20 if detailed (> 500 chars)
- New Product Bonus: +15 if created < 30 days
- Final Score: Capped 0-100
- Recommendation Threshold: score ≥ 60

## Testing

### Run Unit Tests
```bash
pytest tests/unit -v
```

### Run Integration Tests
```bash
pytest tests/integration -v
```

### Run All Tests
```bash
pytest -v --cov=src
```

## Performance Considerations

- **LLM Call Optimization**: Business rules evaluated first (< 1ms), LLM calls (~1-2 seconds) only if rules don't provide confidence
- **Caching**: Consider Redis caching for identical products (future enhancement)
- **Rate Limiting**: API key-based rate limiting at 100 requests/minute (configurable)
- **Database**: Connection pooling optimized for production

## Production Deployment

### Docker Image Build
```bash
docker build -f docker/Dockerfile -t llm-api:latest .
```

### Environment Considerations
- Set `ENVIRONMENT=production`
- Set `DEBUG=false`
- Use strong `API_KEY_SECRET`
- Use external PostgreSQL instance (not containerized)
- Configure proper logging aggregation (ELK, CloudWatch, etc.)
- Enable HTTPS/TLS
- Setup monitoring and alerting

### Cloud Deployment (AWS Example)
- Use ECS/Fargate for container orchestration
- Use RDS for PostgreSQL
- Use API Gateway for routing and rate limiting
- Use CloudWatch for logging and monitoring

## Troubleshooting

### Database Connection Error
```
Error: could not translate host name "postgres" to address
```
**Solution**: Ensure PostgreSQL is running and DATABASE_URL is correct

### OpenAI API Key Error
```
Error: OPENAI_API_KEY not provided
```
**Solution**: Add OPENAI_API_KEY to .env file

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change port or kill process on port 8000

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and test: `pytest`
3. Commit: `git commit -m "Add feature"`
4. Push: `git push origin feature/my-feature`
5. Create Pull Request

## License

MIT License

## Support

For issues or questions, please create an issue in the repository or contact the development team.
