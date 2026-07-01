"""Product-related request and response schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ProductInput(BaseModel):
    """Input schema for product classification/scoring."""

    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, max_length=5000, description="Product description")
    price: float = Field(..., ge=0, description="Product price in USD")
    inventory: int = Field(default=0, ge=0, description="Current inventory count")
    created_date: Optional[str] = Field(None, description="Product creation date (ISO format)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Wireless Noise-Cancelling Headphones",
                "description": "Premium wireless headphones with active noise cancellation, 30-hour battery life, and Bluetooth 5.0 connectivity. Features premium sound quality and comfortable over-ear design.",
                "price": 149.99,
                "inventory": 250,
                "created_date": "2024-01-01",
            }
        }


class CategoryClassificationResponse(BaseModel):
    """Response schema for category classification."""

    primary_category: str
    confidence: float
    tags: List[str]
    applied_rules: List[str]
    llm_enhancement: Optional[Dict[str, Any]] = None
    processing_time_ms: float
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "primary_category": "mid-range",
                "confidence": 0.85,
                "tags": ["detailed-description", "high-stock"],
                "applied_rules": ["price_tier_rule", "inventory_level_rule"],
                "llm_enhancement": {
                    "subcategory": "electronics",
                    "quality_assessment": "excellent",
                    "recommended_marketing_angle": "premium sound quality",
                    "potential_customer_segment": "audiophiles, professionals",
                },
                "processing_time_ms": 1250.5,
                "error": None,
            }
        }


class RecommendationScoringResponse(BaseModel):
    """Response schema for recommendation scoring."""

    base_score: int
    final_recommendation_score: int
    score_breakdown: Dict[str, Any]
    is_recommended: bool
    recommendation_reason: Optional[str] = None
    target_audience: Optional[str] = None
    key_selling_points: List[str] = []
    applied_rules: List[str]
    score_adjustment_from_llm: Optional[int] = None
    llm_enhancement: Optional[bool] = None
    processing_time_ms: float
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "base_score": 75,
                "final_recommendation_score": 80,
                "score_breakdown": {
                    "base_score": 50,
                    "price_tier_bonus": 15,
                    "inventory_bonus": 10,
                    "description_bonus": 20,
                },
                "is_recommended": True,
                "recommendation_reason": "Excellent product with strong market demand and premium features",
                "target_audience": "Tech-savvy professionals and audiophiles",
                "key_selling_points": ["Noise cancellation", "Long battery life", "Premium build"],
                "applied_rules": ["price_rule", "inventory_rule", "description_rule"],
                "score_adjustment_from_llm": 5,
                "llm_enhancement": True,
                "processing_time_ms": 1500.25,
                "error": None,
            }
        }


class HistoryQueryResponse(BaseModel):
    """Response schema for labeling history queries."""

    id: int
    product_id: int
    service_name: str
    input_payload: Dict[str, Any]
    output_payload: Dict[str, Any]
    processing_time_ms: float
    error_message: Optional[str] = None
    trace_id: Optional[str] = None
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "product_id": 123,
                "service_name": "category_classifier",
                "input_payload": {
                    "name": "Wireless Headphones",
                    "price": 149.99,
                    "inventory": 250,
                },
                "output_payload": {
                    "primary_category": "mid-range",
                    "confidence": 0.85,
                },
                "processing_time_ms": 1250.5,
                "error_message": None,
                "trace_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2024-01-15T10:30:00Z",
            }
        }
