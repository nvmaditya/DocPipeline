from __future__ import annotations

import mimetypes
from pathlib import Path

from .base import BaseExtractor
from .docx import DocxExtractor
from .pdf import PdfExtractor


class ExtractorRouter:
    def __init__(self, scanned_threshold: int = 50) -> None:
        self._pdf = PdfExtractor(scanned_threshold=scanned_threshold)
        self._docx = DocxExtractor()

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
        raise ValueError(f"Unsupported file type: {file_path}")
