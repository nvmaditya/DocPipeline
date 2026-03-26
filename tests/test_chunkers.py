from __future__ import annotations

import numpy as np

from docpipe.chunkers import RecursiveChunker
from docpipe.chunkers.semantic import SemanticChunker


def test_recursive_chunker_overlap_and_metadata() -> None:
    text = "A" * 1200
    records = [{"text": text, "page_number": 1, "heading_context": "H1"}]
    meta = {
        "doc_id": "doc-1",
        "file_path": "x.pdf",
        "file_name": "x.pdf",
        "file_type": "pdf",
    }

    chunker = RecursiveChunker(chunk_size=512, chunk_overlap=64)
    chunks = chunker.chunk(records, meta)

    assert len(chunks) >= 2
    assert chunks[0]["doc_id"] == "doc-1"
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["heading_context"] == "H1"
    assert chunks[1]["char_start"] < chunks[0]["char_end"]


def test_semantic_chunker_splits_on_similarity_drop() -> None:
    text = "Alpha topic sentence. Alpha details continue. Beta topic starts. Beta details continue."
    records = [{"text": text, "page_number": 1, "heading_context": "H1"}]
    meta = {
        "doc_id": "doc-2",
        "file_path": "y.pdf",
        "file_name": "y.pdf",
        "file_type": "pdf",
    }

    def embedding_fn(sentences):
        vectors = []
        for s in sentences:
            if "Alpha" in s:
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return np.asarray(vectors, dtype=np.float32)

    chunker = SemanticChunker(
        embedding_fn=embedding_fn,
        chunk_size=1024,
        chunk_overlap=64,
        similarity_threshold=0.5,
    )
    chunks = chunker.chunk(records, meta)

    assert len(chunks) >= 2
    assert any("Alpha" in c["chunk_text"] for c in chunks)
    assert any("Beta" in c["chunk_text"] for c in chunks)
