"""Search routes including semantic and SSE ask stream."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..dependencies import get_current_user_id, get_search_service
from ..services.search_service import SearchService


router = APIRouter(prefix="/api/v1/search", tags=["search"])


class SemanticSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)


@router.post("/semantic")
def semantic_search(
    payload: SemanticSearchRequest,
    database_id: str | None = Query(default=None),
    user_id: str = Depends(get_current_user_id),
    search_service: SearchService = Depends(get_search_service),
) -> dict:
    results = search_service.semantic_search(
        user_id=user_id,
        query=payload.query,
        top_k=payload.top_k,
        database_id=database_id,
    )
    return {"query": payload.query, "results": results}


@router.get("/ask/stream")
def ask_stream(
    query: str = Query(..., min_length=1),
    top_k: int = Query(default=5, ge=1, le=50),
    database_id: str | None = Query(default=None),
    user_id: str = Depends(get_current_user_id),
    search_service: SearchService = Depends(get_search_service),
) -> StreamingResponse:
    iterator = search_service.ask_stream(
        user_id=user_id,
        query=query,
        top_k=top_k,
        database_id=database_id,
    )
    return StreamingResponse(iterator, media_type="text/event-stream")
