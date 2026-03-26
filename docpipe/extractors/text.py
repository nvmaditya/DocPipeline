from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .base import BaseExtractor


class TextExtractor(BaseExtractor):
    def extract(self, file_path: str) -> List[Dict[str, Any]]:
        text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        return [{"text": text, "page_number": None, "heading_context": None}]
