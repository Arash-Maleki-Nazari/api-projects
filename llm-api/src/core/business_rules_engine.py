"""Business rules engine for product labeling."""
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class ProductContext:
    """Context for product evaluation."""

    name: str
    description: str
    price: float
    inventory: int
    created_date: str = None


@dataclass
class RuleResult:
    """Result of a rule evaluation."""

    rule_name: str
    triggered: bool
    label: str = None
    confidence: float = 1.0


class BusinessRulesEngine:
    """Engine for evaluating business rules."""

    @staticmethod
    def evaluate_price_tier(price: float) -> Tuple[str, str]:
        """
        Evaluate price tier based on product price.

        Args:
            price: Product price

        Returns:
            Tuple of (tier, rule_name)
        """
        if price < 50:
            return "budget", "price_tier_rule"
        elif price <= 200:
            return "mid-range", "price_tier_rule"
        else:
            return "premium", "price_tier_rule"

    @staticmethod
    def evaluate_inventory_level(inventory: int) -> List[str]:
        """
        Evaluate inventory status and return applicable tags.

        Args:
            inventory: Current inventory count

        Returns:
            List of inventory-related tags
        """
        tags = []
        if inventory > 1000:
            tags.append("high-stock")
        if inventory < 10:
            tags.append("low-stock")
            tags.append("trigger-reorder")
        return tags

    @staticmethod
    def evaluate_description_quality(description: str) -> bool:
        """
        Check if description is detailed.

        Args:
            description: Product description

        Returns:
            True if description is detailed (> 500 chars)
        """
        if not description:
            return False
        return len(description) > 500

    @staticmethod
    def evaluate_category_rules(context: ProductContext) -> Dict[str, Any]:
        """
        Evaluate all category classification rules.

        Args:
            context: ProductContext object

        Returns:
            Dictionary with rule results and final categorization
        """
        results = {
            "primary_category": None,
            "tags": [],
            "applied_rules": [],
            "fallback_to_llm": False,
        }

        # Price tier rule
        tier, rule_name = BusinessRulesEngine.evaluate_price_tier(context.price)
        results["primary_category"] = tier
        results["applied_rules"].append(rule_name)

        # Inventory tags
        inventory_tags = BusinessRulesEngine.evaluate_inventory_level(context.inventory)
        results["tags"].extend(inventory_tags)
        if inventory_tags:
            results["applied_rules"].append("inventory_level_rule")

        # Description quality
        is_detailed = BusinessRulesEngine.evaluate_description_quality(context.description)
        if is_detailed:
            results["tags"].append("detailed-description")
            results["applied_rules"].append("description_quality_rule")

        return results

    @staticmethod
    def evaluate_recommendation_score(context: ProductContext) -> Dict[str, Any]:
        """
        Calculate recommendation score using business rules.

        Args:
            context: ProductContext object

        Returns:
            Dictionary with score and breakdown
        """
        score = 50  # Base score
        breakdown = {"base_score": 50}

        # Price tier bonus
        tier, _ = BusinessRulesEngine.evaluate_price_tier(context.price)
        if tier in ["mid-range", "premium"]:
            score += 15
            breakdown["price_tier_bonus"] = 15
        else:
            breakdown["price_tier_bonus"] = 0

        # Inventory bonus/penalty
        inventory_tags = BusinessRulesEngine.evaluate_inventory_level(context.inventory)
        if "high-stock" in inventory_tags:
            score += 10
            breakdown["inventory_bonus"] = 10
        if "low-stock" in inventory_tags:
            score -= 20
            breakdown["inventory_penalty"] = -20
        if "inventory_bonus" not in breakdown and "inventory_penalty" not in breakdown:
            breakdown["inventory_neutral"] = 0

        # Description bonus
        is_detailed = BusinessRulesEngine.evaluate_description_quality(context.description)
        if is_detailed:
            score += 20
            breakdown["description_bonus"] = 20
        else:
            breakdown["description_bonus"] = 0

        # Cap score between 0-100
        score = max(0, min(100, score))

        return {
            "recommendation_score": score,
            "score_breakdown": breakdown,
            "applied_rules": ["price_rule", "inventory_rule", "description_rule"],
        }
