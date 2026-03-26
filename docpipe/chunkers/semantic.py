from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

from .base import BaseChunker


class SemanticChunker(BaseChunker):
    def __init__(
        self,
        embedding_fn: Callable[[List[str]], np.ndarray],
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        similarity_threshold: float = 0.5,
    ) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        self.embedding_fn = embedding_fn
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.similarity_threshold = similarity_threshold

    def _sentence_spans(self, text: str) -> List[Tuple[int, int, str]]:
        spans: List[Tuple[int, int, str]] = []
        for match in re.finditer(r"[^.!?\n]+[.!?]?", text):
            sentence = match.group(0).strip()
            if sentence:
                spans.append((match.start(), match.end(), sentence))
        if not spans and text.strip():
            return [(0, len(text), text.strip())]
        return spans

    def _split_semantic_groups(self, spans: List[Tuple[int, int, str]]) -> List[List[Tuple[int, int, str]]]:
        if len(spans) <= 1:
            return [spans] if spans else []

        sentences = [s[2] for s in spans]
        vectors = np.asarray(self.embedding_fn(sentences), dtype=np.float32)
        groups: List[List[Tuple[int, int, str]]] = [[spans[0]]]

        for idx in range(1, len(spans)):
            prev_vec = vectors[idx - 1]
            cur_vec = vectors[idx]
            score = float(np.dot(prev_vec, cur_vec))
            if score < self.similarity_threshold:
                groups.append([spans[idx]])
            else:
                groups[-1].append(spans[idx])
        return groups

    def _split_long_text(self, text: str, start_offset: int) -> List[Tuple[int, int, str]]:
        pieces: List[Tuple[int, int, str]] = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            part = text[start:end].strip()
            if part:
                pieces.append((start_offset + start, start_offset + end, part))
            if end == len(text):
                break
            start = max(0, end - self.chunk_overlap)
        return pieces

    def chunk(self, records: List[Dict[str, Any]], doc_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []
        chunk_index = 0

        for record in records:
            text = record.get("text", "")
            if not text.strip():
                continue

            spans = self._sentence_spans(text)
            groups = self._split_semantic_groups(spans)

            for group in groups:
                if not group:
                    continue
                group_start = group[0][0]
                group_end = group[-1][1]
                group_text = text[group_start:group_end].strip()
                if not group_text:
                    continue

                for char_start, char_end, piece in self._split_long_text(group_text, group_start):
                    chunks.append(
                        {
                            "doc_id": doc_meta["doc_id"],
                            "file_path": doc_meta["file_path"],
                            "file_name": doc_meta["file_name"],
                            "file_type": doc_meta["file_type"],
                            "chunk_index": chunk_index,
                            "page_number": record.get("page_number"),
                            "char_start": char_start,
                            "char_end": char_end,
                            "chunk_text": piece,
                            "heading_context": record.get("heading_context"),
                        }
                    )
                    chunk_index += 1

        return chunks
