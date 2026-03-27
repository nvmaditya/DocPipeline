from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

import docpipe.pipeline as pipeline_mod
from backend.app.main import create_app


class DummyEmbedder:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def encode(self, texts):
        vectors = []
        for text in texts:
            length = float(len(text))
            alpha = float(sum(1 for c in text.lower() if c.isalpha()))
            digits = float(sum(1 for c in text if c.isdigit()))
            vectors.append([length, alpha, digits, 1.0])
        arr = np.asarray(vectors, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return arr / norms


def _write_test_config(path: Path, store_dir: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "extraction:",
                "  scanned_threshold: 10",
                "  ocr_engine: none",
                "  ocr_language: eng",
                "chunking:",
                "  strategy: recursive",
                "  chunk_size: 256",
                "  chunk_overlap: 32",
                "embedding:",
                "  model: sentence-transformers/all-MiniLM-L6-v2",
                "  batch_size: 8",
                "  device: cpu",
                "  normalize: true",
                "faiss:",
                "  index_type: flat",
                "store:",
                f"  faiss_path: {(store_dir / 'faiss.index').as_posix()}",
                f"  sqlite_path: {(store_dir / 'metadata.db').as_posix()}",
                "query:",
                "  top_k: 5",
                "  score_threshold: 0.0",
            ]
        ),
        encoding="utf-8",
    )


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    cfg_path = tmp_path / "backend-config.yaml"
    _write_test_config(cfg_path, tmp_path / "seed-store")
    monkeypatch.setenv("BACKEND_DOCPIPE_CONFIG", str(cfg_path))
    monkeypatch.setenv("BACKEND_USER_STORE_ROOT", str(tmp_path / "users-store"))
    monkeypatch.setattr(pipeline_mod, "Embedder", DummyEmbedder)
    return TestClient(create_app())


@pytest.fixture()
def auth_headers(client: TestClient):
    def _make_headers(email: str = "student@example.com", password: str = "password123") -> dict[str, str]:
        client.post("/api/v1/auth/register", json={"email": email, "password": password})
        login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _make_headers
