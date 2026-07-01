"""OpenAI LLM client wrapper with retry logic and error handling."""

import json
import re
import time
from typing import Optional, Dict, Any

from openai import (
    OpenAI,
    RateLimitError,
    APIError,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
)

from src.core.settings import get_settings
from src.core.logger import logger


settings = get_settings()


class LLMClient:
    """Wrapper around OpenAI client with retry logic and safer JSON handling."""

    def __init__(self, api_key: str = None, max_retries: int = 3):
        """
        Initialize LLM client.

        Args:
            api_key: OpenAI API key. If None, uses settings.openai_api_key.
            max_retries: Maximum number of retry attempts.
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens
        self.max_retries = max_retries
        self.last_error: Optional[str] = None

        if not self.api_key:
            self.last_error = "OPENAI_API_KEY is missing."
            logger.error(self.last_error)

        logger.info(
            f"Initializing LLMClient with model={self.model}, "
            f"temperature={self.temperature}, max_tokens={self.max_tokens}, "
            f"api_key_loaded={bool(self.api_key)}"
        )

        self.client = OpenAI(api_key=self.api_key)

    def classify_product(self, product_info: str) -> Optional[Dict[str, Any]]:
        """
        Use LLM to classify a product with enhanced insights.

        Args:
            product_info: Product information as string.

        Returns:
            Dictionary with LLM classification result or None on failure.
        """
        prompt = f"""
Classify the following e-commerce product and provide detailed insights.

Product information:
{product_info}

Return only valid JSON with this exact structure:
{{
  "primary_category": "string, for example electronics, fashion, home, beauty, sports, books, toys, automotive, grocery, other",
  "subcategory": "string",
  "quality_assessment": "excellent, good, fair, or poor",
  "confidence": 0.0,
  "recommended_marketing_angle": "string",
  "potential_customer_segment": "string"
}}

Rules:
- Return JSON only.
- Do not use markdown.
- Do not wrap the JSON in ```json code fences.
- confidence must be a number between 0.0 and 1.0.
"""
        return self._call_gpt_with_retry(prompt)

    def score_recommendation(
        self,
        product_info: str,
        base_score: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Use LLM to enhance recommendation scoring.

        Args:
            product_info: Product information as string.
            base_score: Base score from rule engine, from 0 to 100.

        Returns:
            Dictionary with LLM recommendation insights or None on failure.
        """
        prompt = f"""
Given this e-commerce product and a base recommendation score of {base_score}/100,
provide enhanced recommendation insights.

Product information:
{product_info}

Return only valid JSON with this exact structure:
{{
  "recommendation_reason": "string explaining why this product is or is not recommended",
  "target_audience": "string describing who would benefit from this product",
  "confidence_adjustment": 0.0,
  "key_selling_points": ["string", "string", "string"]
}}

Rules:
- Return JSON only.
- Do not use markdown.
- Do not wrap the JSON in ```json code fences.
- confidence_adjustment must be a number between -0.2 and 0.2.
- key_selling_points must be a JSON array of strings.
"""
        return self._call_gpt_with_retry(prompt)

    def _call_gpt_with_retry(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Call OpenAI Chat Completions API with retry logic.

        Args:
            prompt: Prompt to send to the model.

        Returns:
            Parsed JSON response or None on failure.
        """
        self.last_error = None

        if not self.api_key:
            self.last_error = "OPENAI_API_KEY is missing or empty."
            logger.error(self.last_error)
            return None

        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"Calling OpenAI model={self.model} "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )

                response = self._create_chat_completion(
                    prompt=prompt,
                    use_json_mode=True,
                )

                content = response.choices[0].message.content

                if content is None:
                    self.last_error = "OpenAI response content was None."
                    logger.error(self.last_error)
                    return None

                logger.info(f"Raw LLM response: {content}")

                result = self._parse_json_response(content)

                if not isinstance(result, dict):
                    self.last_error = (
                        f"LLM response was valid JSON but not a JSON object: {result}"
                    )
                    logger.error(self.last_error)
                    return None

                logger.info(f"LLM call succeeded on attempt {attempt + 1}")
                return result

            except RateLimitError as e:
                self.last_error = f"OpenAI rate limit/quota error: {str(e)}"
                wait_time = 2 ** attempt

                logger.warning(
                    f"{self.last_error}. Retrying in {wait_time}s "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )

                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
                    continue

                logger.error("Max retries exceeded due to OpenAI rate limit/quota error.")
                return None

            except AuthenticationError as e:
                self.last_error = (
                    "OpenAI authentication failed. Check OPENAI_API_KEY. "
                    f"Error: {str(e)}"
                )
                logger.error(self.last_error)
                return None

            except BadRequestError as e:
                error_text = str(e)

                # Some older model/API combinations reject response_format.
                # In that case, retry once without JSON mode.
                if "response_format" in error_text.lower():
                    logger.warning(
                        "OpenAI rejected response_format=json_object. "
                        "Retrying once without JSON mode."
                    )

                    try:
                        response = self._create_chat_completion(
                            prompt=prompt,
                            use_json_mode=False,
                        )

                        content = response.choices[0].message.content

                        if content is None:
                            self.last_error = (
                                "OpenAI response content was None after fallback without JSON mode."
                            )
                            logger.error(self.last_error)
                            return None

                        logger.info(f"Raw LLM response after fallback: {content}")

                        result = self._parse_json_response(content)

                        if not isinstance(result, dict):
                            self.last_error = (
                                f"Fallback LLM response was JSON but not an object: {result}"
                            )
                            logger.error(self.last_error)
                            return None

                        logger.info("LLM call succeeded after fallback without JSON mode.")
                        return result

                    except Exception as fallback_error:
                        self.last_error = (
                            "OpenAI fallback without JSON mode also failed. "
                            f"Model={self.model}. Error: {str(fallback_error)}"
                        )
                        logger.error(self.last_error, exc_info=True)
                        return None

                self.last_error = (
                    "OpenAI rejected the request. This is often caused by an invalid model, "
                    "unsupported parameter, or malformed request. "
                    f"Model={self.model}. Error: {error_text}"
                )
                logger.error(self.last_error)
                return None

            except (APIConnectionError, APITimeoutError) as e:
                self.last_error = f"OpenAI connection/timeout error: {str(e)}"
                wait_time = 2 ** attempt

                logger.warning(
                    f"{self.last_error}. Retrying in {wait_time}s "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )

                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
                    continue

                logger.error("Max retries exceeded due to OpenAI connection/timeout errors.")
                return None

            except APIError as e:
                self.last_error = f"OpenAI API error: {str(e)}"
                wait_time = 2 ** attempt

                logger.warning(
                    f"{self.last_error}. Retrying in {wait_time}s "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )

                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
                    continue

                logger.error("Max retries exceeded due to OpenAI API errors.")
                return None

            except json.JSONDecodeError as e:
                self.last_error = f"Failed to parse LLM response as JSON: {str(e)}"
                logger.error(self.last_error)
                return None

            except Exception as e:
                self.last_error = (
                    f"Unexpected error calling OpenAI. Model={self.model}. Error: {str(e)}"
                )
                logger.error(self.last_error, exc_info=True)
                return None

        self.last_error = "LLM call failed after all retry attempts."
        logger.error(self.last_error)
        return None

    def _create_chat_completion(self, prompt: str, use_json_mode: bool):
        """
        Create a Chat Completions request.

        Args:
            prompt: User prompt.
            use_json_mode: Whether to ask OpenAI to enforce JSON output.

        Returns:
            OpenAI chat completion response.
        """
        request_kwargs = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a JSON-only API. "
                        "Return valid JSON only. "
                        "Do not include markdown, comments, explanations, or code fences."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if use_json_mode:
            request_kwargs["response_format"] = {"type": "json_object"}

        return self.client.chat.completions.create(**request_kwargs)

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        Parse JSON from the model response.

        This handles both strict JSON and accidental markdown-wrapped JSON.

        Args:
            content: Raw model response.

        Returns:
            Parsed JSON dictionary.

        Raises:
            json.JSONDecodeError if parsing fails.
        """
        cleaned = content.strip()

        # First try direct JSON parsing.
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Remove markdown code fences if the model ignored instructions.
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Last fallback: extract the first JSON object from the text.
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))

        # Raise a proper JSON error if no object can be extracted.
        return json.loads(cleaned)