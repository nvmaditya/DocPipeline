"""Study content and quiz generation routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from ..dependencies import get_current_user_id
from ..services.study_service import StudyService


router = APIRouter(prefix="/api/v1/study", tags=["study"])


class GenerateStudyRequest(BaseModel):
    database_id: str = Field(min_length=1)
    topic_name: str = Field(min_length=1)


@router.post("/generate")
def generate_study_material(
    payload: GenerateStudyRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    study_service: StudyService = request.app.state.study_service
    try:
        result = study_service.generate_study_material(
            user_id=user_id,
            database_id=payload.database_id,
            topic_name=payload.topic_name,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
