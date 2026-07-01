"""Unit tests for Business Rules Engine."""
import pytest
from src.core.business_rules_engine import BusinessRulesEngine, ProductContext


@pytest.fixture
def engine():
    """Business rules engine instance."""
    return BusinessRulesEngine()


class TestPriceTierRule:
    """Tests for price tier evaluation."""

    def test_budget_price_tier(self, engine):
        """Test budget tier for prices < $50."""
        tier, rule_name = engine.evaluate_price_tier(29.99)
        assert tier == "budget"
        assert rule_name == "price_tier_rule"

    def test_midrange_price_tier_lower_bound(self, engine):
        """Test mid-range tier at lower bound ($50)."""
        tier, rule_name = engine.evaluate_price_tier(50.00)
        assert tier == "mid-range"

    def test_midrange_price_tier_upper_bound(self, engine):
        """Test mid-range tier at upper bound ($200)."""
        tier, rule_name = engine.evaluate_price_tier(200.00)
        assert tier == "mid-range"

    def test_premium_price_tier(self, engine):
        """Test premium tier for prices > $200."""
        tier, rule_name = engine.evaluate_price_tier(299.99)
        assert tier == "premium"


class TestInventoryRule:
    """Tests for inventory level evaluation."""

    def test_high_stock_threshold(self, engine):
        """Test high-stock tag for inventory > 1000."""
        tags = engine.evaluate_inventory_level(1500)
        assert "high-stock" in tags

    def test_boundary_high_stock(self, engine):
        """Test boundary at 1000 inventory."""
        tags_at_1000 = engine.evaluate_inventory_level(1000)
        tags_at_1001 = engine.evaluate_inventory_level(1001)
        assert "high-stock" not in tags_at_1000
        assert "high-stock" in tags_at_1001

    def test_low_stock_threshold(self, engine):
        """Test low-stock tags for inventory < 10."""
        tags = engine.evaluate_inventory_level(5)
        assert "low-stock" in tags
        assert "trigger-reorder" in tags

    def test_boundary_low_stock(self, engine):
        """Test boundary at 10 inventory."""
        tags_at_10 = engine.evaluate_inventory_level(10)
        tags_at_9 = engine.evaluate_inventory_level(9)
        assert "low-stock" not in tags_at_10
        assert "low-stock" in tags_at_9

    def test_normal_inventory(self, engine):
        """Test normal inventory (no tags)."""
        tags = engine.evaluate_inventory_level(500)
        assert "high-stock" not in tags
        assert "low-stock" not in tags


class TestDescriptionQualityRule:
    """Tests for description quality evaluation."""

    def test_detailed_description_threshold(self, engine):
        """Test detailed description > 500 chars."""
        description = "A" * 501
        assert engine.evaluate_description_quality(description) is True

    def test_boundary_description(self, engine):
        """Test boundary at 500 chars."""
        description_500 = "A" * 500
        description_501 = "A" * 501
        assert engine.evaluate_description_quality(description_500) is False
        assert engine.evaluate_description_quality(description_501) is True

    def test_short_description(self, engine):
        """Test short description."""
        description = "Short description"
        assert engine.evaluate_description_quality(description) is False

    def test_none_description(self, engine):
        """Test None description."""
        assert engine.evaluate_description_quality(None) is False

    def test_empty_description(self, engine):
        """Test empty description."""
        assert engine.evaluate_description_quality("") is False


class TestCategoryRulesEvaluation:
    """Tests for complete category rules evaluation."""

    def test_category_rules_budget_product(self, engine):
        """Test category rules for budget product."""
        context = ProductContext(
            name="Budget Product",
            description="A" * 600,
            price=29.99,
            inventory=1500,
        )
        result = engine.evaluate_category_rules(context)

        assert result["primary_category"] == "budget"
        assert "detailed-description" in result["tags"]
        assert "high-stock" in result["tags"]

    def test_category_rules_premium_low_stock(self, engine):
        """Test category rules for premium product with low stock."""
        context = ProductContext(
            name="Premium Product",
            description="Short",
            price=299.99,
            inventory=5,
        )
        result = engine.evaluate_category_rules(context)

        assert result["primary_category"] == "premium"
        assert "low-stock" in result["tags"]
        assert "trigger-reorder" in result["tags"]


class TestRecommendationScoringRules:
    """Tests for recommendation scoring."""

    def test_base_score_initialization(self, engine):
        """Test base score starts at 50."""
        context = ProductContext(
            name="Product",
            description="Short",
            price=50.00,
            inventory=100,
        )
        result = engine.evaluate_recommendation_score(context)

        assert result["score_breakdown"]["base_score"] == 50

    def test_price_tier_bonus_budget(self, engine):
        """Test no price bonus for budget tier."""
        context = ProductContext(
            name="Budget Product",
            description="Short",
            price=29.99,
            inventory=100,
        )
        result = engine.evaluate_recommendation_score(context)

        assert result["score_breakdown"]["price_tier_bonus"] == 0

    def test_price_tier_bonus_midrange(self, engine):
        """Test price bonus for mid-range tier."""
        context = ProductContext(
            name="Mid-range Product",
            description="Short",
            price=100.00,
            inventory=100,
        )
        result = engine.evaluate_recommendation_score(context)

        assert result["score_breakdown"]["price_tier_bonus"] == 15

    def test_price_tier_bonus_premium(self, engine):
        """Test price bonus for premium tier."""
        context = ProductContext(
            name="Premium Product",
            description="Short",
            price=250.00,
            inventory=100,
        )
        result = engine.evaluate_recommendation_score(context)

        assert result["score_breakdown"]["price_tier_bonus"] == 15

    def test_inventory_bonus_high_stock(self, engine):
        """Test inventory bonus for high stock."""
        context = ProductContext(
            name="Product",
            description="Short",
            price=100.00,
            inventory=1500,
        )
        result = engine.evaluate_recommendation_score(context)

        assert result["score_breakdown"]["inventory_bonus"] == 10

    def test_inventory_penalty_low_stock(self, engine):
        """Test inventory penalty for low stock."""
        context = ProductContext(
            name="Product",
            description="Short",
            price=100.00,
            inventory=5,
        )
        result = engine.evaluate_recommendation_score(context)

        assert result["score_breakdown"]["inventory_penalty"] == -20

    def test_description_bonus(self, engine):
        """Test bonus for detailed description."""
        context = ProductContext(
            name="Product",
            description="A" * 600,
            price=100.00,
            inventory=100,
        )
        result = engine.evaluate_recommendation_score(context)

        assert result["score_breakdown"]["description_bonus"] == 20

    def test_score_capped_at_100(self, engine):
        """Test that score is capped at 100."""
        context = ProductContext(
            name="Premium Product",
            description="A" * 1000,
            price=300.00,
            inventory=5000,
        )
        result = engine.evaluate_recommendation_score(context)

        assert result["recommendation_score"] <= 100

    def test_score_minimum_0(self, engine):
        """Test that score doesn't go below 0."""
        context = ProductContext(
            name="Poor Product",
            description="Bad",
            price=10.00,
            inventory=2,
        )
        result = engine.evaluate_recommendation_score(context)

        assert result["recommendation_score"] >= 0
