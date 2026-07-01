"""Classification routes for category and recommendation services."""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from src.schemas.product import ProductInput, CategoryClassificationResponse, RecommendationScoringResponse
from src.schemas.common import SuccessResponse, ErrorResponse
from src.services.category_classifier import CategoryClassifier
from src.services.recommendation_scorer import RecommendationScorer
from src.database.session import get_db
from src.database.repository import LabelingHistoryRepository
from src.api.middleware.auth import verify_api_key
from src.core.container import get_llm_client, get_business_rules_engine, get_logger
from src.core.logger import logger

router = APIRouter(prefix="/api/v1/classify", tags=["Classification"])


@router.post(
    "/category",
    response_model=SuccessResponse,
    summary="Classify product into category",
    description="Classify a product using hybrid business rules and LLM approach",
)
async def classify_category(
    product: ProductInput,
    request: Request,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
) -> SuccessResponse:
    """
    Classify product into category using CategoryClassifier service.

    Args:
        product: Product input data
        request: FastAPI request object
        db: Database session
        api_key: Verified API key

    Returns:
        SuccessResponse with category classification result
    """
    trace_id = str(uuid.uuid4())
    logger.info(f"[{trace_id}] Category classification request received")

    try:
        # Initialize service
        llm_client = get_llm_client()
        rules_engine = get_business_rules_engine()
        classifier = CategoryClassifier(llm_client=llm_client, rules_engine=rules_engine)

        # Classify product
        result = classifier.classify(
            product_name=product.name,
            product_description=product.description,
            price=product.price,
            inventory=product.inventory,
            created_date=product.created_date,
        )

        # Log to history
        LabelingHistoryRepository.create_history(
            db=db,
            product_id=0,  # Product not stored in DB for this MVP
            input_payload=product.model_dump(),
            output_payload=result,
            service_name="category_classifier",
            processing_time_ms=result.get("processing_time_ms", 0),
            api_key_used=api_key,
            trace_id=trace_id,
        )

        logger.info(
            f"[{trace_id}] Category classification completed: "
            f"{result.get('primary_category')}"
        )

        # Return success response
        return SuccessResponse(
            status="success",
            data=CategoryClassificationResponse(**result),
            trace_id=trace_id,
            timestamp=datetime.utcnow(),
        )

    except ValueError as e:
        logger.error(f"[{trace_id}] Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"[{trace_id}] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post(
    "/recommendation",
    response_model=SuccessResponse,
    summary="Score product recommendation",
    description="Score a product recommendation using hybrid business rules and LLM approach",
)
async def score_recommendation(
    product: ProductInput,
    request: Request,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
) -> SuccessResponse:
    """
    Score product recommendation using RecommendationScorer service.

    Args:
        product: Product input data
        request: FastAPI request object
        db: Database session
        api_key: Verified API key

    Returns:
        SuccessResponse with recommendation scoring result
    """
    trace_id = str(uuid.uuid4())
    logger.info(f"[{trace_id}] Recommendation scoring request received")

    try:
        # Initialize service
        llm_client = get_llm_client()
        rules_engine = get_business_rules_engine()
        scorer = RecommendationScorer(llm_client=llm_client, rules_engine=rules_engine)

        # Score product
        result = scorer.score(
            product_name=product.name,
            product_description=product.description,
            price=product.price,
            inventory=product.inventory,
            created_date=product.created_date,
        )

        # Log to history
        LabelingHistoryRepository.create_history(
            db=db,
            product_id=0,  # Product not stored in DB for this MVP
            input_payload=product.model_dump(),
            output_payload=result,
            service_name="recommendation_scorer",
            processing_time_ms=result.get("processing_time_ms", 0),
            api_key_used=api_key,
            trace_id=trace_id,
        )

        logger.info(
            f"[{trace_id}] Recommendation scoring completed: "
            f"score={result.get('final_recommendation_score')}"
        )

        # Return success response
        return SuccessResponse(
            status="success",
            data=RecommendationScoringResponse(**result),
            trace_id=trace_id,
            timestamp=datetime.utcnow(),
        )

    except ValueError as e:
        logger.error(f"[{trace_id}] Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"[{trace_id}] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
