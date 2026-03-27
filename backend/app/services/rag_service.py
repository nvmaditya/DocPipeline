"""RAG stream helper service for SSE payload formatting."""

from __future__ import annotations

import json
from collections.abc import Iterator


class RagService:
    def build_stream(self, query: str, source_names: list[str]) -> Iterator[str]:
        yield f"data: {json.dumps({'type': 'meta', 'query': query, 'sources': source_names})}\n\n"

        tokens = [
            "Analyzing retrieved context.",
            "Building grounded response.",
            "Streaming complete answer.",
        ]
        for token in tokens:
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'answer': ' '.join(tokens)})}\n\n"
