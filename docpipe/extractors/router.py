from __future__ import annotations

import mimetypes
from pathlib import Path

from .base import BaseExtractor
from .docx import DocxExtractor
from .html import HtmlExtractor
from .pdf import PdfExtractor
from .pptx import PptxExtractor
from .text import TextExtractor
from .xlsx import XlsxExtractor


class ExtractorRouter:
    def __init__(self, scanned_threshold: int = 50, ocr_engine: str = "none", ocr_language: str = "eng") -> None:
        self._pdf = PdfExtractor(
            scanned_threshold=scanned_threshold,
            ocr_engine=ocr_engine,
            ocr_language=ocr_language,
        )
        self._docx = DocxExtractor()
        self._pptx = PptxExtractor()
        self._xlsx = XlsxExtractor()
        self._html = HtmlExtractor()
        self._text = TextExtractor()

    def route(self, file_path: str) -> BaseExtractor:
        mime_type, _ = mimetypes.guess_type(file_path)
        ext = Path(file_path).suffix.lower()

        if mime_type == "application/pdf" or ext == ".pdf":
            return self._pdf
        if (
            mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            or ext == ".docx"
        ):
            return self._docx
        if (
            mime_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            or ext == ".pptx"
        ):
            return self._pptx
        if ext in {".xlsx", ".csv"}:
            return self._xlsx
        if mime_type == "text/html" or ext in {".html", ".htm"}:
            return self._html
        if mime_type and mime_type.startswith("text/"):
            return self._text
        if ext in {".txt", ".md"}:
            return self._text
        raise ValueError(f"Unsupported file type: {file_path}")
