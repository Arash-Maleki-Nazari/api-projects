"""FastAPI application entry point."""

from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import get_settings
from src.core.logger import setup_logger
from src.database.session import init_db
from src.api.routes import classify
from src.api.routes.rag import router as rag_router
from src.schemas.common import SuccessResponse


# Initialize settings
settings = get_settings()

# Setup logger
app_logger = setup_logger(
    "llm-api",
    log_level=settings.log_level,
    use_json=(settings.log_format.lower() == "json"),
)


# Create FastAPI app
app = FastAPI(
    title="LLM-based Product Labeling API",
    description=(
        "FastAPI service for product categorization, recommendation scoring, "
        "business-rule classification, optional LLM enrichment, and local RAG search."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and log startup."""
    try:
        init_db()
        app_logger.info(
            f"Application started in {settings.environment} mode | "
            f"Debug: {settings.debug} | "
            f"Log Level: {settings.log_level}"
        )
    except Exception as e:
        app_logger.error(f"Startup error: {str(e)}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown."""
    app_logger.info("Application shutting down")


@app.get("/health", tags=["Health"], summary="Health check endpoint")
async def health_check() -> dict:
    """Return application health status."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
    }


# Include routers
app.include_router(classify.router)
app.include_router(rag_router, prefix="/api/v1/rag", tags=["RAG"])


@app.get("/", tags=["Root"], summary="API root")
async def root() -> SuccessResponse:
    """Return API information."""
    return SuccessResponse(
        status="success",
        data={
            "service": "LLM-based Product Labeling API",
            "version": "1.0.0",
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "classify_category": "/api/v1/classify/category",
                "classify_recommendation": "/api/v1/classify/recommendation",
                "rag_search": "/api/v1/rag/search",
            },
        },
        timestamp=datetime.utcnow(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower(),
    )