"""Unit tests for CategoryClassifier service."""
import pytest
from unittest.mock import MagicMock, patch
from src.services.category_classifier import CategoryClassifier
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
def classifier(llm_client, rules_engine):
    """CategoryClassifier instance."""
    return CategoryClassifier(llm_client=llm_client, rules_engine=rules_engine)


def test_classify_budget_product(classifier):
    """Test classification of budget product."""
    result = classifier.classify(
        product_name="Basic Headphones",
        product_description="Simple wireless headphones",
        price=29.99,
        inventory=100,
    )

    assert result["primary_category"] == "budget"
    assert result["confidence"] >= 0.0
    assert "price_tier_rule" in result["applied_rules"]


def test_classify_midrange_product(classifier):
    """Test classification of mid-range product."""
    result = classifier.classify(
        product_name="Premium Headphones",
        product_description="High-quality wireless headphones with noise cancellation. " * 10,
        price=149.99,
        inventory=2000,
    )

    assert result["primary_category"] == "mid-range"
    assert "high-stock" in result["tags"]
    assert "detailed-description" in result["tags"]


def test_classify_premium_product(classifier):
    """Test classification of premium product."""
    result = classifier.classify(
        product_name="Luxury Headphones",
        product_description="Elite sound quality.",
        price=299.99,
        inventory=50,
    )

    assert result["primary_category"] == "premium"
    assert "price_tier_rule" in result["applied_rules"]


def test_classify_low_stock_product(classifier):
    """Test classification of low-stock product."""
    result = classifier.classify(
        product_name="Headphones",
        product_description="Low stock item",
        price=99.99,
        inventory=5,
    )

    assert "low-stock" in result["tags"]
    assert "trigger-reorder" in result["tags"]


def test_classify_with_llm_enhancement(classifier):
    """Test classification with LLM enhancement."""
    classifier.llm_client.classify_product.return_value = {
        "subcategory": "audio-equipment",
        "quality_assessment": "excellent",
        "recommended_marketing_angle": "premium sound quality",
        "potential_customer_segment": "audiophiles",
        "confidence": 0.9,
    }

    result = classifier.classify(
        product_name="Premium Headphones",
        product_description="High quality sound.",
        price=199.99,
        inventory=100,
    )

    assert result["llm_enhancement"] is not None
    assert result["confidence"] >= 0.8


def test_classify_without_llm_enhancement(classifier):
    """Test classification when LLM returns None."""
    classifier.llm_client.classify_product.return_value = None

    result = classifier.classify(
        product_name="Headphones",
        product_description="Basic headphones",
        price=49.99,
        inventory=100,
    )

    assert result["llm_enhancement"] is None
    assert result["primary_category"] == "budget"


def test_classify_processing_time(classifier):
    """Test that processing time is recorded."""
    result = classifier.classify(
        product_name="Headphones",
        product_description="Wireless headphones",
        price=99.99,
        inventory=100,
    )

    assert "processing_time_ms" in result
    assert result["processing_time_ms"] >= 0


def test_classify_error_handling(classifier):
    """Test error handling in classification."""
    classifier.rules_engine.evaluate_category_rules.side_effect = Exception("Test error")

    result = classifier.classify(
        product_name="Headphones",
        product_description="Wireless headphones",
        price=99.99,
        inventory=100,
    )

    assert result["error"] is not None
    assert result["primary_category"] is None
