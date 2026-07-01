"""API key authentication middleware."""
from fastapi import HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from src.core.settings import get_settings
from src.core.logger import logger

settings = get_settings()

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    """
    Verify API key from X-API-Key request header.
    """

    if not api_key:
        logger.warning("Request received without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )

    if api_key != settings.api_key_secret:
        logger.warning("Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    masked_key = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 9 else "***"
    return masked_key