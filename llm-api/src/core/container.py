"""Dependency injection container."""
from typing import Optional
from src.core.settings import get_settings
from src.core.llm_client import LLMClient
from src.core.business_rules_engine import BusinessRulesEngine
from src.core.logger import setup_logger

# Lazy initialization
_settings: Optional[object] = None
_llm_client: Optional[LLMClient] = None
_business_rules_engine: Optional[BusinessRulesEngine] = None


def get_container_settings():
    """Get settings instance."""
    global _settings
    if _settings is None:
        _settings = get_settings()
    return _settings


def get_llm_client() -> LLMClient:
    """Get LLM client instance (singleton)."""
    global _llm_client
    if _llm_client is None:
        settings = get_container_settings()
        _llm_client = LLMClient(api_key=settings.openai_api_key)
    return _llm_client


def get_business_rules_engine() -> BusinessRulesEngine:
    """Get business rules engine instance (singleton)."""
    global _business_rules_engine
    if _business_rules_engine is None:
        _business_rules_engine = BusinessRulesEngine()
    return _business_rules_engine


def get_logger(name: str):
    """Get configured logger."""
    settings = get_container_settings()
    use_json = settings.log_format.lower() == "json"
    return setup_logger(name, log_level=settings.log_level, use_json=use_json)
