from __future__ import annotations

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

        if self.backend == "local":
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model_name, device=device)
        elif self.backend == "github":
            self.model = None
        else:
            raise ValueError(f"Unsupported embedding backend: {backend}")

    def _get_openai_client(self):
        if self._openai_client is not None:
            return self._openai_client

        token = os.getenv(self._github_token_env)
        if not token:
            raise RuntimeError(
                f"Missing {self._github_token_env}. Set it to call GitHub Models embeddings API."
            )

        try:
            from openai import OpenAI
        except Exception as exc:
            raise RuntimeError("OpenAI SDK is required for GitHub embeddings. Install `openai`.") from exc

        self._openai_client = OpenAI(base_url=self._github_endpoint, api_key=token)
        return self._openai_client

    def encode(self, texts: List[str]):
        if self.backend == "local":
            return self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                normalize_embeddings=self.normalize,
            )

        client = self._get_openai_client()
        vectors = []
        for idx in range(0, len(texts), self.batch_size):
            batch = texts[idx : idx + self.batch_size]
            response = client.embeddings.create(model=self.model_name, input=batch)
            vectors.extend(item.embedding for item in response.data)

        arr = np.asarray(vectors, dtype=np.float32)
        if self.normalize and arr.size:
            norms = np.linalg.norm(arr, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            arr = arr / norms
        return arr
