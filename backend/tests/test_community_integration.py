"""Integration tests for community database API flow."""

from __future__ import annotations

from pathlib import Path
import subprocess

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


def _write_config(path: Path, store_dir: Path) -> None:
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


def _setup_community_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    book_content: str = "Photosynthesis is the process used by plants to convert light energy into chemical energy.",
    book_name: str = "TestBiology.txt",
):
    """Configure test environment with a temp Books dir containing a single test file."""
    cfg_path = tmp_path / "community-config.yaml"
    _write_config(cfg_path, tmp_path / "seed-store")

    books_dir = tmp_path / "books"
    books_dir.mkdir(parents=True, exist_ok=True)
    (books_dir / book_name).write_text(book_content, encoding="utf-8")

    monkeypatch.setenv("BACKEND_DOCPIPE_CONFIG", str(cfg_path))
    monkeypatch.setenv("BACKEND_USER_STORE_ROOT", str(tmp_path / "users-store"))
    monkeypatch.setenv("BACKEND_COMMUNITY_STORE_ROOT", str(tmp_path / "community-store"))
    monkeypatch.setenv("BACKEND_BOOKS_ROOT", str(books_dir))
    monkeypatch.setattr(pipeline_mod, "Embedder", DummyEmbedder)


def _auth_headers(client: TestClient) -> dict[str, str]:
    payload = {"email": "community-test@example.com", "password": "password123"}
    client.post("/api/v1/auth/register", json=payload)
    login = client.post("/api/v1/auth/login", json=payload)
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_community_databases_endpoint_returns_empty_when_no_books(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When Books dir is empty, /api/v1/community/databases returns empty list."""
    cfg_path = tmp_path / "config.yaml"
    _write_config(cfg_path, tmp_path / "seed-store")
    books_dir = tmp_path / "books"
    books_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("BACKEND_DOCPIPE_CONFIG", str(cfg_path))
    monkeypatch.setenv("BACKEND_USER_STORE_ROOT", str(tmp_path / "users-store"))
    monkeypatch.setenv("BACKEND_COMMUNITY_STORE_ROOT", str(tmp_path / "community-store"))
    monkeypatch.setenv("BACKEND_BOOKS_ROOT", str(books_dir))
    monkeypatch.setattr(pipeline_mod, "Embedder", DummyEmbedder)

    with TestClient(create_app()) as client:
        headers = _auth_headers(client)
        response = client.get("/api/v1/community/databases", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["databases"] == []


def test_community_databases_endpoint_lists_bootstrapped_book(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A book file in Books dir is indexed and appears in the listing."""
    _setup_community_env(monkeypatch, tmp_path)

    with TestClient(create_app()) as client:
        headers = _auth_headers(client)
        response = client.get("/api/v1/community/databases", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["databases"]) == 1

    db_entry = data["databases"][0]
    assert db_entry["title"] == "TestBiology"
    assert db_entry["database_id"] == "testbiology"
    assert db_entry["documents"] >= 1
    assert db_entry["chunks"] >= 1


def test_community_semantic_search_scoped_to_database(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Semantic search with database_id is scoped to the community database."""
    _setup_community_env(monkeypatch, tmp_path)

    with TestClient(create_app()) as client:
        headers = _auth_headers(client)

        # Bootstrap community databases first via listing
        list_resp = client.get("/api/v1/community/databases", headers=headers)
        assert list_resp.status_code == 200
        db_id = list_resp.json()["databases"][0]["database_id"]

        # Search within the community database
        search_resp = client.post(
            "/api/v1/search/semantic",
            params={"database_id": db_id},
            json={"query": "photosynthesis", "top_k": 3},
            headers=headers,
        )
        assert search_resp.status_code == 200
        results = search_resp.json()["results"]
        assert len(results) > 0


def test_community_ask_stream_scoped_to_database(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Ask stream with database_id returns SSE response grounded in community database."""
    _setup_community_env(monkeypatch, tmp_path)

    with TestClient(create_app()) as client:
        headers = _auth_headers(client)

        # Bootstrap community databases first
        list_resp = client.get("/api/v1/community/databases", headers=headers)
        assert list_resp.status_code == 200
        db_id = list_resp.json()["databases"][0]["database_id"]

        # Ask within the community database
        ask_resp = client.get(
            "/api/v1/search/ask/stream",
            params={"query": "what is photosynthesis", "database_id": db_id},
            headers=headers,
        )
        assert ask_resp.status_code == 200
        assert ask_resp.headers["content-type"].startswith("text/event-stream")
        assert "data:" in ask_resp.text


def test_community_databases_requires_auth() -> None:
    """Community databases endpoint requires authentication."""
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/community/databases")
    assert response.status_code == 401


def test_create_module_uses_fallback_when_web_extractor_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Create module should still succeed and index fallback content when web_extractor fails."""
    _setup_community_env(monkeypatch, tmp_path)

    def _fail_subprocess(*args, **kwargs):
        raise subprocess.CalledProcessError(1, args[0], output="", stderr="simulated extractor failure")

    monkeypatch.setattr(subprocess, "run", _fail_subprocess)

    with TestClient(create_app()) as client:
        headers = _auth_headers(client)
        response = client.post(
            "/api/v1/community/modules",
            headers=headers,
            json={"topic": "Fallback Topic"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["database_id"] == "fallback_topic"

    source_file = Path(data["source_file"])
    assert source_file.exists()
    source_text = source_file.read_text(encoding="utf-8")
    assert "local fallback content" in source_text
    assert "simulated extractor failure" in source_text
