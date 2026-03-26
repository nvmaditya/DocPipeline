from __future__ import annotations

from typing import Any, Dict, List

import fitz

from .base import BaseExtractor


class PdfExtractor(BaseExtractor):
    def __init__(self, scanned_threshold: int = 50) -> None:
        self.scanned_threshold = scanned_threshold

    def extract(self, file_path: str) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        doc = fitz.open(file_path)
        try:
            for page_index, page in enumerate(doc):
                text = page.get_text("text") or ""
                is_scanned = len(text.strip()) < self.scanned_threshold
                if is_scanned:
                    continue
                records.append(
                    {
                        "text": text,
                        "page_number": page_index + 1,
                        "heading_context": None,
                    }
                )
        finally:
            doc.close()
        return records
