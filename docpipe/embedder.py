from __future__ import annotations

import hashlib
import os
from typing import List

import numpy as np


class Embedder:
    def __init__(
        self,
        model_name: str,
        batch_size: int = 32,
        device: str = "cpu",
        normalize: bool = True,
        backend: str = "local",
        github_endpoint: str = "https://models.github.ai/inference",
        github_token_env: str = "GITHUB_TOKEN",
    ) -> None:
        self.backend = backend.lower()
        self.model_name = model_name
        self.batch_size = batch_size
        self.normalize = normalize
        self._github_endpoint = github_endpoint
        self._github_token_env = github_token_env
        self._openai_client = None
        self._fallback_mode = False
        self._fallback_dim = int(os.getenv("DOCPIPE_FALLBACK_EMBEDDING_DIM", "384"))

        if self.backend == "local":
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model_name, device=device)
        elif self.backend == "github":
            self.model = None
        else:
            raise ValueError(f"Unsupported embedding backend: {backend}")

    def _normalize_vectors(self, arr: np.ndarray) -> np.ndarray:
        if self.normalize and arr.size:
            norms = np.linalg.norm(arr, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            arr = arr / norms
        return arr

    def _fallback_embed(self, texts: List[str]) -> np.ndarray:
        """Deterministic, dependency-free embedding fallback used when remote embedding API is unavailable."""
        vectors = np.zeros((len(texts), self._fallback_dim), dtype=np.float32)
        for row, text in enumerate(texts):
            if not text:
                vectors[row, 0] = 1.0
                continue

            text_bytes = text.encode("utf-8", errors="ignore")
            for idx, byte in enumerate(text_bytes):
                bucket = (byte + 131 * idx) % self._fallback_dim
                sign = 1.0 if (idx % 2 == 0) else -1.0
                vectors[row, bucket] += sign * (1.0 + (byte % 17) / 17.0)

            digest = hashlib.sha256(text_bytes).digest()
            for idx, byte in enumerate(digest):
                bucket = (byte + 17 * idx) % self._fallback_dim
                vectors[row, bucket] += 0.25

        return self._normalize_vectors(vectors)

    def _get_openai_client(self):
        if self._openai_client is not None:
            return self._openai_client

        token = os.getenv(self._github_token_env)
        if not token:
            if "localhost" in self._github_endpoint or "127.0.0.1" in self._github_endpoint:
                token = "ollama"
            else:
                raise RuntimeError(
                    f"Missing {self._github_token_env}. Set this environment variable to use the embeddings API."
                )

        try:
            from openai import OpenAI
        except Exception as exc:
            raise RuntimeError("OpenAI SDK is required for GitHub embeddings. Install `openai`.") from exc

        self._openai_client = OpenAI(base_url=self._github_endpoint, api_key=token)
        return self._openai_client

    def encode(self, texts: List[str]):
        if self.backend == "local":
            vectors = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                normalize_embeddings=self.normalize,
            )
            return np.asarray(vectors, dtype=np.float32)

        if self._fallback_mode:
            return self._fallback_embed(texts)

        try:
            client = self._get_openai_client()
            vectors = []
            for idx in range(0, len(texts), self.batch_size):
                batch = texts[idx : idx + self.batch_size]
                response = client.embeddings.create(model=self.model_name, input=batch)
                vectors.extend(item.embedding for item in response.data)

            arr = np.asarray(vectors, dtype=np.float32)
            return self._normalize_vectors(arr)
        except Exception as exc:
            # Avoid hard-failing ingestion when remote embeddings are temporarily unavailable.
            self._fallback_mode = True
            print(f"[Embedder] Remote embedding unavailable, using fallback embeddings: {exc}")
            return self._fallback_embed(texts)
