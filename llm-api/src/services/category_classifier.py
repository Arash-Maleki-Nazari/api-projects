"""CategoryClassifier service for e-commerce product categorization."""

import time
from typing import Dict, Any, Optional

from src.core.business_rules_engine import BusinessRulesEngine, ProductContext
from src.core.llm_client import LLMClient
from src.core.logger import logger


class CategoryClassifier:
    """Service for classifying products into categories."""

    def __init__(self, llm_client: LLMClient, rules_engine: BusinessRulesEngine):
        """
        Initialize CategoryClassifier.

        Args:
            llm_client: LLM client for enhanced classification
            rules_engine: Business rules engine for rule-based classification
        """
        self.llm_client = llm_client
        self.rules_engine = rules_engine

    def classify(
        self,
        product_name: str,
        product_description: str,
        price: float,
        inventory: int,
        created_date: str = None,
    ) -> Dict[str, Any]:
        """
        Classify a product using hybrid approach: rules + LLM.

        Args:
            product_name: Product name
            product_description: Product description
            price: Product price
            inventory: Current inventory count
            created_date: Product creation date

        Returns:
            Dictionary with classification result.
        """
        start_time = time.time()

        try:
            context = ProductContext(
                name=product_name,
                description=product_description,
                price=price,
                inventory=inventory,
                created_date=created_date,
            )

            rules_result = self.rules_engine.evaluate_category_rules(context)
            logger.info(f"Rules evaluation completed: {rules_result['applied_rules']}")

            llm_result = self._get_llm_enhancement(context)

            final_result = self._combine_results(
                rules_result=rules_result,
                llm_result=llm_result,
            )

            processing_time = (time.time() - start_time) * 1000
            final_result["processing_time_ms"] = processing_time

            logger.info(
                f"Classification completed in {processing_time:.2f}ms: "
                f"{final_result['primary_category']}"
            )

            return final_result

        except Exception as e:
            logger.error(f"Classification error: {str(e)}", exc_info=True)
            processing_time = (time.time() - start_time) * 1000
            return {
                "primary_category": None,
                "confidence": 0.0,
                "tags": [],
                "applied_rules": [],
                "llm_enhancement": None,
                "error": str(e),
                "processing_time_ms": processing_time,
            }

    def _get_llm_enhancement(self, context: ProductContext) -> Optional[Dict[str, Any]]:
        """
        Get LLM enhancement for category classification.

        Args:
            context: ProductContext object

        Returns:
            LLM enhancement result, or diagnostic failure dictionary.
        """
        product_info = (
            f"Product Name: {context.name}\n"
            f"Description: {context.description or 'N/A'}\n"
            f"Price: ${context.price}\n"
            f"Inventory: {context.inventory}"
        )

        logger.info("Calling LLM for category enhancement")

        llm_result = self.llm_client.classify_product(product_info)

        if llm_result:
            logger.info("LLM enhancement successful")
            return llm_result

        llm_error = getattr(self.llm_client, "last_error", None)

        if not llm_error:
            llm_error = (
                "LLM returned None but did not set last_error. "
                "This usually means the running server is still using an old LLMClient "
                "or the failure path does not set self.last_error."
            )

        logger.warning(f"LLM enhancement failed, using rules only. Cause: {llm_error}")

        return {
            "_llm_failed": True,
            "_llm_error": llm_error,
        }

    def _combine_results(
        self,
        rules_result: Dict[str, Any],
        llm_result: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Combine rule-based and LLM results into final classification.

        Args:
            rules_result: Result from business rules engine
            llm_result: Result from LLM or diagnostic failure object

        Returns:
            Combined final result
        """
        combined = {
            "primary_category": rules_result["primary_category"],
            "confidence": 0.8,
            "tags": rules_result["tags"],
            "applied_rules": rules_result["applied_rules"],
            "llm_enhancement": None,
            "error": None,
        }

        if not llm_result:
            combined["error"] = "LLM enhancement returned no result."
            return combined

        if llm_result.get("_llm_failed"):
            combined["error"] = llm_result.get("_llm_error")
            return combined

        combined["llm_enhancement"] = {
            "subcategory": llm_result.get("subcategory"),
            "quality_assessment": llm_result.get("quality_assessment"),
            "recommended_marketing_angle": llm_result.get("recommended_marketing_angle"),
            "potential_customer_segment": llm_result.get("potential_customer_segment"),
        }

        llm_confidence = llm_result.get("confidence", 0.7)
        combined["confidence"] = round(0.8 * 0.8 + llm_confidence * 0.2, 2)

        return combined