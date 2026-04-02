"""Community database routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..dependencies import get_community_service, get_current_user_id
from ..services.community_service import CommunityService


router = APIRouter(prefix="/api/v1/community", tags=["community"])


@router.get("/databases")
def list_community_databases(
    _: str = Depends(get_current_user_id),
    community_service: CommunityService = Depends(get_community_service),
) -> dict:
    records = community_service.list_databases()
    return {
        "databases": [
            {
                "database_id": row.database_id,
                "title": row.title,
                "source_file": row.source_file,
                "documents": row.documents,
                "chunks": row.chunks,
            }
            for row in records
        ]
    }


class CreateModuleRequest(BaseModel):
    topic: str

@router.post("/modules")
def create_community_module(
    req: CreateModuleRequest,
    _: str = Depends(get_current_user_id),
    community_service: CommunityService = Depends(get_community_service),
) -> dict:
    try:
        record = community_service.create_module(req.topic)
        return {
            "database_id": record.database_id,
            "title": record.title,
            "source_file": record.source_file,
            "documents": record.documents,
            "chunks": record.chunks,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/databases/{database_id}/topics")
def get_community_topics(
    database_id: str,
    _: str = Depends(get_current_user_id),
    community_service: CommunityService = Depends(get_community_service),
) -> dict:
    """Return extracted topics for a community database."""
    # Find the source_file for this database_id
    records = community_service.list_databases()
    matched = [r for r in records if r.database_id == database_id]
    if not matched:
        raise HTTPException(status_code=404, detail="Database not found")

    source_file = matched[0].source_file
    topics = community_service._pipeline_adapter.get_community_topics(
        database_id=database_id,
        source_file=source_file,
    )
    return {
        "database_id": database_id,
        "title": matched[0].title,
        "topics": topics,
    }
