from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np


class FaissStore:
    def __init__(self, index_path: str) -> None:
        self.index_path = index_path
        self.index = None

    def _ensure_index(self, dim: int) -> None:
        if self.index is None:
            if Path(self.index_path).exists():
                self.index = faiss.read_index(self.index_path)
            else:
                self.index = faiss.IndexFlatIP(dim)

    def add_vectors(self, vectors) -> None:
        np_vectors = np.asarray(vectors, dtype=np.float32)
        if np_vectors.ndim != 2:
            raise ValueError("Vectors must be 2D")
        self._ensure_index(np_vectors.shape[1])
        self.index.add(np_vectors)

    def search(self, query_vector, top_k: int) -> List[Tuple[int, float]]:
        np_query = np.asarray(query_vector, dtype=np.float32)
        if np_query.ndim == 1:
            np_query = np_query.reshape(1, -1)
        if self.index is None:
            return []
        scores, ids = self.index.search(np_query, top_k)
        results: List[Tuple[int, float]] = []
        for score, idx in zip(scores[0], ids[0]):
            if idx == -1:
                continue
            results.append((int(idx), float(score)))
        return results

    def count(self) -> int:
        if self.index is None:
            if Path(self.index_path).exists():
                self.index = faiss.read_index(self.index_path)
            else:
                return 0
        return int(self.index.ntotal)

    def save(self) -> None:
        if self.index is None:
            return
        Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, self.index_path)
