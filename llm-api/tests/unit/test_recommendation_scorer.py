"""Unit tests for RecommendationScorer service."""
import pytest
from unittest.mock import MagicMock
from src.services.recommendation_scorer import RecommendationScorer
from src.core.llm_client import LLMClient
from src.core.business_rules_engine import BusinessRulesEngine


@pytest.fixture
def llm_client():
    """Mock LLM client."""
    client = MagicMock(spec=LLMClient)
    return client


@pytest.fixture
def rules_engine():
    """Real business rules engine."""
    return BusinessRulesEngine()


@pytest.fixture
def scorer(llm_client, rules_engine):
    """RecommendationScorer instance."""
    return RecommendationScorer(llm_client=llm_client, rules_engine=rules_engine)


def test_score_budget_product(scorer):
    """Test scoring of budget product."""
    result = scorer.score(
        product_name="Budget Headphones",
        product_description="Affordable option",
        price=29.99,
        inventory=100,
    )

    assert "base_score" in result
    assert "final_recommendation_score" in result
    assert "score_breakdown" in result


def test_score_high_inventory_product(scorer):
    """Test scoring of high-inventory product."""
    result = scorer.score(
        product_name="Popular Headphones",
        product_description="Best seller",
        price=99.99,
        inventory=2000,
    )

    assert result["base_score"] >= 50
    assert result["score_breakdown"]["inventory_bonus"] == 10


def test_score_low_inventory_product(scorer):
    """Test scoring of low-inventory product."""
    result = scorer.score(
        product_name="Rare Headphones",
        product_description="Limited stock",
        price=199.99,
        inventory=3,
    )

    assert result["score_breakdown"].get("inventory_penalty", 0) == -20


def test_score_detailed_description_product(scorer):
    """Test scoring of product with detailed description."""
    long_description = "High quality " * 100  # > 500 chars

    result = scorer.score(
        product_name="Premium Headphones",
        product_description=long_description,
        price=149.99,
        inventory=100,
    )

    assert result["score_breakdown"]["description_bonus"] == 20


def test_score_with_llm_enhancement(scorer):
    """Test scoring with LLM enhancement."""
    scorer.llm_client.score_recommendation.return_value = {
        "recommendation_reason": "Excellent product",
        "target_audience": "Professionals",
        "confidence_adjustment": 0.15,
        "key_selling_points": ["Quality", "Features"],
    }

    result = scorer.score(
        product_name="Premium Headphones",
        product_description="High quality sound",
        price=199.99,
        inventory=500,
    )

    assert result["recommendation_reason"] is not None
    assert result["target_audience"] is not None
    assert result["key_selling_points"] is not None


def test_score_recommendation_threshold(scorer):
    """Test recommendation threshold (>= 60)."""
    # High score case
    result_high = scorer.score(
        product_name="Premium Headphones",
        product_description="Detailed description " * 30,
        price=199.99,
        inventory=2000,
    )
    assert result_high["is_recommended"] == (result_high["final_recommendation_score"] >= 60)

    # Low score case
    result_low = scorer.score(
        product_name="Basic Headphones",
        product_description="Basic",
        price=29.99,
        inventory=2,
    )
    assert result_low["is_recommended"] == (result_low["final_recommendation_score"] >= 60)


def test_score_capped_at_100(scorer):
    """Test that score is capped at 100."""
    result = scorer.score(
        product_name="Premium Headphones",
        product_description="Excellent product description " * 50,
        price=299.99,
        inventory=5000,
    )

    assert result["final_recommendation_score"] <= 100


def test_score_minimum_0(scorer):
    """Test that score doesn't go below 0."""
    result = scorer.score(
        product_name="Poor Headphones",
        product_description="Bad",
        price=9.99,
        inventory=2,
    )

    assert result["final_recommendation_score"] >= 0


def test_score_processing_time(scorer):
    """Test that processing time is recorded."""
    result = scorer.score(
        product_name="Headphones",
        product_description="Wireless headphones",
        price=99.99,
        inventory=100,
    )

    assert "processing_time_ms" in result
    assert result["processing_time_ms"] >= 0


def test_score_error_handling(scorer):
    """Test error handling in scoring."""
    scorer.rules_engine.evaluate_recommendation_score.side_effect = Exception("Test error")

    result = scorer.score(
        product_name="Headphones",
        product_description="Wireless headphones",
        price=99.99,
        inventory=100,
    )

    assert result["error"] is not None
    assert result["base_score"] == 0
