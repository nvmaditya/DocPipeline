from __future__ import annotations

from pathlib import Path

import fitz
from docx import Document

from docpipe.pipeline import Pipeline


def _make_pdf(path: Path, text: str) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(str(path))
    doc.close()


def _make_docx(path: Path, heading: str, text: str) -> None:
    doc = Document()
    doc.add_heading(heading, level=1)
    doc.add_paragraph(text)
    doc.save(str(path))


def test_pipeline_ingest_and_query(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    _make_pdf(docs_dir / "sample.pdf", "Revenue increased in Q3.")
    _make_docx(docs_dir / "sample.docx", "Summary", "Revenue increased and costs dropped.")

    store_dir = tmp_path / "store"
    faiss_path = (store_dir / "faiss.index").as_posix()
    sqlite_path = (store_dir / "metadata.db").as_posix()
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(
        "\n".join(
            [
                "extraction:",
                "  scanned_threshold: 10",
                "chunking:",
                "  chunk_size: 256",
                "  chunk_overlap: 32",
                "embedding:",
                "  model: sentence-transformers/all-MiniLM-L6-v2",
                "  batch_size: 8",
                "  device: cpu",
                "  normalize: true",
                "faiss:",
                "  index_type: flat",
                "store:",
                f"  faiss_path: {faiss_path}",
                f"  sqlite_path: {sqlite_path}",
                "query:",
                "  top_k: 5",
                "  score_threshold: 0.0",
            ]
        ),
        encoding="utf-8",
    )

    pipe = Pipeline(config=str(cfg_path))
    try:
        ingested = pipe.ingest(str(docs_dir))
        assert ingested == 2

        results = pipe.search("revenue", top_k=5)
        assert results
        assert any("Revenue" in r["chunk_text"] or "revenue" in r["chunk_text"] for r in results)

        stats = pipe.stats()
        assert stats["documents"] == 2
        assert stats["chunks"] >= 2
    finally:
        pipe.close()
