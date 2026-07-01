"""RecommendationScorer service for e-commerce product recommendation scoring."""
import time
from typing import Dict, Any, Optional
from src.core.business_rules_engine import BusinessRulesEngine, ProductContext
from src.core.llm_client import LLMClient
from src.core.logger import logger


class RecommendationScorer:
    """Service for scoring product recommendations."""

    def __init__(self, llm_client: LLMClient, rules_engine: BusinessRulesEngine):
        """
        Initialize RecommendationScorer.

        Args:
            llm_client: LLM client for enhanced scoring insights
            rules_engine: Business rules engine for rule-based scoring
        """
        self.llm_client = llm_client
        self.rules_engine = rules_engine

    def score(
        self,
        product_name: str,
        product_description: str,
        price: float,
        inventory: int,
        created_date: str = None,
    ) -> Dict[str, Any]:
        """
        Score product recommendation using hybrid approach (rules + LLM).

        Args:
            product_name: Product name
            product_description: Product description
            price: Product price
            inventory: Current inventory count
            created_date: Product creation date

        Returns:
            Dictionary with recommendation score and detailed insights
        """
        start_time = time.time()

        try:
            # Create context
            context = ProductContext(
                name=product_name,
                description=product_description,
                price=price,
                inventory=inventory,
                created_date=created_date,
            )

            # Step 1: Calculate score using business rules
            rules_result = self.rules_engine.evaluate_recommendation_score(context)
            base_score = rules_result["recommendation_score"]
            logger.info(f"Base score calculated: {base_score}")

            # Step 2: Get LLM enhancement
            llm_enhancement = self._get_llm_enhancement(context, base_score)

            # Step 3: Combine results
            final_result = self._combine_results(
                rules_result=rules_result,
                llm_result=llm_enhancement,
            )

            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            final_result["processing_time_ms"] = processing_time

            logger.info(
                f"Recommendation scoring completed in {processing_time:.2f}ms: "
                f"score={final_result['final_recommendation_score']}"
            )

            return final_result

        except Exception as e:
            logger.error(f"Recommendation scoring error: {str(e)}", exc_info=True)
            processing_time = (time.time() - start_time) * 1000
            return {
                "final_recommendation_score": 0,
                "base_score": 0,
                "score_breakdown": {},
                "recommendation_reason": None,
                "target_audience": None,
                "error": str(e),
                "processing_time_ms": processing_time,
            }

    def _get_llm_enhancement(
        self, context: ProductContext, base_score: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get LLM enhancement for recommendation scoring.

        Args:
            context: ProductContext object
            base_score: Base score from rules engine

        Returns:
            LLM enhancement result or None if LLM call fails
        """
        product_info = (
            f"Product Name: {context.name}\n"
            f"Description: {context.description or 'N/A'}\n"
            f"Price: ${context.price}\n"
            f"Inventory: {context.inventory}"
        )

        llm_result = self.llm_client.score_recommendation(product_info, base_score)

        if llm_result:
            logger.info("LLM enhancement successful for recommendation")
            return llm_result
        else:
            logger.warning("LLM enhancement failed for recommendation, using rules only")
            return None

    def _combine_results(
        self,
        rules_result: Dict[str, Any],
        llm_result: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Combine rule-based and LLM results into final recommendation score.

        Args:
            rules_result: Result from business rules engine
            llm_result: Result from LLM or None

        Returns:
            Combined final result
        """
        base_score = rules_result["recommendation_score"]
        final_score = base_score

        combined = {
            "base_score": base_score,
            "final_recommendation_score": final_score,
            "score_breakdown": rules_result["score_breakdown"],
            "applied_rules": rules_result["applied_rules"],
            "recommendation_reason": None,
            "target_audience": None,
            "key_selling_points": [],
            "llm_enhancement": None,
            "is_recommended": final_score >= 60,  # Threshold
        }

        if llm_result:
            # Merge LLM results
            combined["llm_enhancement"] = True
            combined["recommendation_reason"] = llm_result.get("recommendation_reason")
            combined["target_audience"] = llm_result.get("target_audience")
            combined["key_selling_points"] = llm_result.get("key_selling_points", [])

            # Adjust score based on LLM confidence adjustment
            confidence_adjustment = llm_result.get("confidence_adjustment", 0)
            adjustment_value = int(confidence_adjustment * 20)  # Scale to 0-20 point adjustment
            final_score = max(0, min(100, base_score + adjustment_value))

            combined["final_recommendation_score"] = final_score
            combined["score_adjustment_from_llm"] = adjustment_value
            combined["is_recommended"] = final_score >= 60

        return combined
