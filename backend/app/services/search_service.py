"""Search service primitives for semantic search and SSE ask stream."""

from __future__ import annotations

from collections.abc import Iterator

from ..adapters.pipeline_adapter import PipelineAdapter
from .rag_service import RagService


class SearchService:
    def __init__(self, pipeline_adapter: PipelineAdapter, rag_service: RagService | None = None) -> None:
        self._pipeline_adapter = pipeline_adapter
        self._rag_service = rag_service or RagService()

    def semantic_search(self, user_id: str, query: str, top_k: int) -> list[dict]:
        return self._pipeline_adapter.semantic_search(user_id=user_id, query=query, top_k=top_k)

    def ask_stream(self, user_id: str, query: str, top_k: int) -> Iterator[str]:
        results = self.semantic_search(user_id=user_id, query=query, top_k=top_k)
        source_names = [r["file_name"] for r in results]
        yield from self._rag_service.build_stream(query=query, source_names=source_names)
