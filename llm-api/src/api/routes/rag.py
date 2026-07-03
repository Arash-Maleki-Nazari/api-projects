"""RAG API routes."""

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.api.middleware.auth import verify_api_key
from src.services.rag_service import LocalRAGService


router = APIRouter()

_rag_service: Optional[LocalRAGService] = None


class RAGSearchRequest(BaseModel):
    """Request model for local RAG search."""

    query: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of results to return")


def get_rag_service() -> LocalRAGService:
    """Create the RAG service lazily when the endpoint is first used."""
    global _rag_service

    if _rag_service is None:
        _rag_service = LocalRAGService()

    return _rag_service


@router.post("/search")
def search_knowledge_base(
    request: RAGSearchRequest,
    api_key: str = Depends(verify_api_key),
    rag_service: LocalRAGService = Depends(get_rag_service),
):
    """Search the local vector database for relevant knowledge-base chunks."""

    indexed_count = rag_service.index_documents()
    results = rag_service.search(query=request.query, top_k=request.top_k)

    return {
        "status": "success",
        "data": {
            "query": request.query,
            "top_k": request.top_k,
            "indexed_new_chunks": indexed_count,
            "results": results,
        },
    }
