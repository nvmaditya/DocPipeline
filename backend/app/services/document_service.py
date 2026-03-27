"""Document service backed by the docpipe pipeline adapter."""

from __future__ import annotations

from dataclasses import dataclass

from ..adapters.pipeline_adapter import PipelineAdapter


@dataclass
class DocumentRecord:
    doc_id: str
    user_id: str
    file_name: str
    file_size_bytes: int
    ingested_at: str
    file_type: str
    file_path: str


class DocumentService:
    def __init__(self, pipeline_adapter: PipelineAdapter) -> None:
        self._pipeline_adapter = pipeline_adapter

    def add_document(self, user_id: str, file_name: str, payload: bytes) -> DocumentRecord:
        doc = self._pipeline_adapter.add_document(user_id=user_id, file_name=file_name, payload=payload)
        return DocumentRecord(
            doc_id=doc.doc_id,
            user_id=doc.user_id,
            file_name=doc.file_name,
            file_size_bytes=doc.file_size_bytes,
            ingested_at=doc.ingested_at,
            file_type=doc.file_type,
            file_path=doc.file_path,
        )

    def list_documents(self, user_id: str) -> list[DocumentRecord]:
        docs = self._pipeline_adapter.list_documents(user_id)
        return [
            DocumentRecord(
                doc_id=doc.doc_id,
                user_id=doc.user_id,
                file_name=doc.file_name,
                file_size_bytes=doc.file_size_bytes,
                ingested_at=doc.ingested_at,
                file_type=doc.file_type,
                file_path=doc.file_path,
            )
            for doc in docs
        ]

    def get_document(self, user_id: str, doc_id: str) -> DocumentRecord | None:
        doc = self._pipeline_adapter.get_document(user_id, doc_id)
        if doc is None:
            return None
        return DocumentRecord(
            doc_id=doc.doc_id,
            user_id=doc.user_id,
            file_name=doc.file_name,
            file_size_bytes=doc.file_size_bytes,
            ingested_at=doc.ingested_at,
            file_type=doc.file_type,
            file_path=doc.file_path,
        )

    def delete_document(self, user_id: str, doc_id: str) -> bool:
        return self._pipeline_adapter.delete_document(user_id, doc_id)
