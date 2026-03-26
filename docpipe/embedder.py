from __future__ import annotations

from typing import List

from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name: str, batch_size: int = 32, device: str = "cpu", normalize: bool = True) -> None:
        self.model = SentenceTransformer(model_name, device=device)
        self.batch_size = batch_size
        self.normalize = normalize

    def encode(self, texts: List[str]):
        return self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=False,
            normalize_embeddings=self.normalize,
        )
