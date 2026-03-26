from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, records: List[Dict[str, Any]], doc_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return chunk records with chunk text and normalized metadata."""
