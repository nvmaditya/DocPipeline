from __future__ import annotations

from typing import Any, Dict, List

import fitz

from .base import BaseExtractor


class PdfExtractor(BaseExtractor):
    def __init__(self, scanned_threshold: int = 50, ocr_engine: str = "none", ocr_language: str = "eng") -> None:
        self.scanned_threshold = scanned_threshold
        self.ocr_engine = ocr_engine.lower()
        self.ocr_language = ocr_language

    def extract(self, file_path: str) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        doc = fitz.open(file_path)
        try:
            for page_index, page in enumerate(doc):
                text = page.get_text("text") or ""
                heading_context = self._detect_heading_context(page)
                is_scanned = len(text.strip()) < self.scanned_threshold
                if is_scanned:
                    ocr_text = self._extract_ocr_text(page)
                    if not ocr_text.strip():
                        continue
                    text = ocr_text
                records.append(
                    {
                        "text": text,
                        "page_number": page_index + 1,
                        "heading_context": heading_context,
                    }
                )
        finally:
            doc.close()
        return records

    def _detect_heading_context(self, page: fitz.Page) -> str | None:
        try:
            content = page.get_text("dict")
        except Exception:
            return None

        candidate = None
        best_size = 0.0
        for block in content.get("blocks", []):
            for line in block.get("lines", []):
                line_text_parts: List[str] = []
                line_size = 0.0
                for span in line.get("spans", []):
                    text = (span.get("text") or "").strip()
                    if text:
                        line_text_parts.append(text)
                        line_size = max(line_size, float(span.get("size") or 0.0))
                line_text = " ".join(line_text_parts).strip()
                if not line_text:
                    continue
                if len(line_text) > 120:
                    continue
                if line_size > best_size:
                    candidate = line_text
                    best_size = line_size
        return candidate

    def _extract_ocr_text(self, page: fitz.Page) -> str:
        if self.ocr_engine in {"none", "off", "disabled"}:
            return ""

        if self.ocr_engine == "surya":
            try:
                from surya.ocr import run_ocr  # type: ignore
            except Exception:
                return ""
            try:
                pix = page.get_pixmap(dpi=200)
                png_bytes = pix.tobytes("png")
                result = run_ocr([png_bytes], [self.ocr_language])
                lines: List[str] = []
                for page_result in result:
                    for line in getattr(page_result, "text_lines", []) or []:
                        value = getattr(line, "text", "")
                        if value:
                            lines.append(value)
                return "\n".join(lines)
            except Exception:
                return ""

        if self.ocr_engine == "tesseract":
            try:
                from PIL import Image
                import io
                import pytesseract
            except Exception:
                return ""
            try:
                pix = page.get_pixmap(dpi=300)
                image = Image.open(io.BytesIO(pix.tobytes("png")))
                return pytesseract.image_to_string(image, lang=self.ocr_language)
            except Exception:
                return ""

        return ""
