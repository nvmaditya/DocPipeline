from __future__ import annotations

from pathlib import Path

import fitz
from docx import Document

from docpipe.extractors import DocxExtractor, PdfExtractor


def test_pdf_extractor_reads_text_page(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello PDF extractor")
    doc.save(str(pdf_path))
    doc.close()

    extractor = PdfExtractor(scanned_threshold=5)
    records = extractor.extract(str(pdf_path))

    assert records
    assert "Hello PDF extractor" in records[0]["text"]
    assert records[0]["page_number"] == 1


def test_docx_extractor_reads_heading_paragraph_and_table(tmp_path: Path) -> None:
    docx_path = tmp_path / "sample.docx"
    doc = Document()
    doc.add_heading("Section 1", level=1)
    doc.add_paragraph("This is a paragraph.")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "A"
    table.cell(0, 1).text = "B"
    doc.save(str(docx_path))

    extractor = DocxExtractor()
    records = extractor.extract(str(docx_path))

    texts = [r["text"] for r in records]
    assert any("Section 1" in t for t in texts)
    assert any("This is a paragraph." in t for t in texts)
    assert any("A | B" in t for t in texts)
