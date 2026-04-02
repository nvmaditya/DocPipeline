"""Search service primitives for semantic search and SSE ask stream."""

from __future__ import annotations

from collections.abc import Iterator

from ..adapters.pipeline_adapter import PipelineAdapter
from .rag_service import RagService


class SearchService:
    def __init__(self, pipeline_adapter: PipelineAdapter, rag_service: RagService | None = None) -> None:
        self._pipeline_adapter = pipeline_adapter
        self._rag_service = rag_service or RagService()

    def semantic_search(
        self,
        user_id: str,
        query: str,
        top_k: int,
        database_id: str | None = None,
    ) -> list[dict]:
        selected_database = database_id.strip() if database_id else None
        selected_database = selected_database or None
        return self._pipeline_adapter.semantic_search(
            user_id=user_id,
            query=query,
            top_k=top_k,
            database_id=selected_database,
        )

    def ask_stream(
        self,
        user_id: str,
        query: str,
        top_k: int,
        database_id: str | None = None,
    ) -> Iterator[str]:
        try:
            result = self._pipeline_adapter.ask(
                user_id=user_id,
                query=query,
                top_k=top_k,
                database_id=database_id,
            )
            source_names = [r["file_name"] for r in result.get("sources", [])]
            answer = result.get("response", "")
        except Exception as exc:
            results = self.semantic_search(user_id=user_id, query=query, top_k=top_k, database_id=database_id)
            source_names = [r["file_name"] for r in results]
            answer = f"I found some relevant documents, but I could not generate an AI response due to an error: {exc}"

        yield from self._rag_service.build_stream(
            query=query,
            answer=answer,
            source_names=source_names,
        )
