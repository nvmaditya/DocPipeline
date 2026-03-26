from __future__ import annotations

from typing import Any, Dict, List

from .base import BaseChunker


class RecursiveChunker(BaseChunker):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, records: List[Dict[str, Any]], doc_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []
        chunk_index = 0

        for record in records:
            text = record.get("text", "")
            if not text.strip():
                continue

            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                part = text[start:end].strip()
                if part:
                    chunks.append(
                        {
                            "doc_id": doc_meta["doc_id"],
                            "file_path": doc_meta["file_path"],
                            "file_name": doc_meta["file_name"],
                            "file_type": doc_meta["file_type"],
                            "chunk_index": chunk_index,
                            "page_number": record.get("page_number"),
                            "char_start": start,
                            "char_end": end,
                            "chunk_text": part,
                            "heading_context": record.get("heading_context"),
                        }
                    )
                    chunk_index += 1

                if end == len(text):
                    break
                start = max(0, end - self.chunk_overlap)

        return chunks
