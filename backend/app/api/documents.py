"""Document routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..dependencies import get_current_user_id, get_document_service
from ..services.document_service import DocumentService


router = APIRouter(prefix="/api/v1/docs", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    payload = await file.read()
    record = document_service.add_document(user_id=user_id, file_name=file.filename or "unnamed", payload=payload)
    return {
        "doc_id": record.doc_id,
        "file_name": record.file_name,
        "file_size_bytes": record.file_size_bytes,
        "ingested_at": record.ingested_at,
    }


@router.get("/list")
def list_documents(
    user_id: str = Depends(get_current_user_id),
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    rows = document_service.list_documents(user_id)
    return {"documents": [row.__dict__ for row in rows]}


@router.get("/{doc_id}")
def get_document(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    row = document_service.get_document(user_id, doc_id)
    if row is None:
        raise HTTPException(status_code=404, detail="document not found")
    return row.__dict__


@router.delete("/{doc_id}")
def delete_document(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    deleted = document_service.delete_document(user_id, doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="document not found")
    return {"message": "document deleted"}
