"""RAG stream helper service for SSE payload formatting."""

from __future__ import annotations

import json
from collections.abc import Iterator


class RagService:
    def build_stream(self, query: str, answer: str, source_names: list[str]) -> Iterator[str]:
        yield f"data: {json.dumps({'type': 'meta', 'query': query, 'sources': source_names})}\n\n"

        chunk_size = 15
        for i in range(0, len(answer), chunk_size):
            chunk = answer[i : i + chunk_size]
            yield f"data: {json.dumps({'type': 'chunk', 'text': chunk})}\n\n"

        yield f"data: {json.dumps({'type': 'answer', 'text': answer})}\n\n"
