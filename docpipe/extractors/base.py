from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, file_path: str) -> List[Dict[str, Any]]:
        """Return page/section-level extraction records with text and metadata."""
