from __future__ import annotations

from docpipe.chunkers import RecursiveChunker


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
