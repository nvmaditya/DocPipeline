from __future__ import annotations

from typing import Any, Dict, List

from bs4 import BeautifulSoup
import html2text

from .base import BaseExtractor


class HtmlExtractor(BaseExtractor):
    def __init__(self) -> None:
        self._h2t = html2text.HTML2Text()
        self._h2t.ignore_links = False

    def extract(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
            raw = handle.read()
        soup = BeautifulSoup(raw, "html.parser")
        text = self._h2t.handle(str(soup))
        return [{"text": text, "page_number": None, "heading_context": None}]
