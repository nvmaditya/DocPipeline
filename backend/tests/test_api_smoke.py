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


def _configure_adapter_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg_path = tmp_path / "backend-config.yaml"
    _write_test_config(cfg_path, tmp_path / "seed-store")
    monkeypatch.setenv("BACKEND_DOCPIPE_CONFIG", str(cfg_path))
    monkeypatch.setenv("BACKEND_USER_STORE_ROOT", str(tmp_path / "users-store"))
    monkeypatch.setattr(pipeline_mod, "Embedder", DummyEmbedder)


def _auth_headers(client: TestClient) -> dict[str, str]:
    register_payload = {"email": "student@example.com", "password": "password123"}
    client.post("/api/v1/auth/register", json=register_payload)
    login = client.post("/api/v1/auth/login", json=register_payload)
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_endpoint() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_auth_login_and_me() -> None:
    client = TestClient(create_app())
    payload = {"email": "user@example.com", "password": "password123"}

    register = client.post("/api/v1/auth/register", json=payload)
    assert register.status_code == 200

    login = client.post("/api/v1/auth/login", json=payload)
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == payload["email"]


def test_document_and_search_flow(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _configure_adapter_runtime(monkeypatch, tmp_path)
    client = TestClient(create_app())
    headers = _auth_headers(client)

    upload = client.post(
        "/api/v1/docs/upload",
        files={"file": ("notes.txt", b"sample notes for search")},
        headers=headers,
    )
    assert upload.status_code == 200

    listing = client.get("/api/v1/docs/list", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()["documents"]) == 1

    semantic = client.post(
        "/api/v1/search/semantic",
        json={"query": "notes", "top_k": 3},
        headers=headers,
    )
    assert semantic.status_code == 200
    body = semantic.json()
    assert body["results"]
    assert "notes" in body["results"][0]["chunk_text"].lower()


def test_document_delete_hides_from_list(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _configure_adapter_runtime(monkeypatch, tmp_path)
    client = TestClient(create_app())
    headers = _auth_headers(client)

    upload = client.post(
        "/api/v1/docs/upload",
        files={"file": ("to-delete.txt", b"content to delete")},
        headers=headers,
    )
    assert upload.status_code == 200
    doc_id = upload.json()["doc_id"]

    delete = client.delete(f"/api/v1/docs/{doc_id}", headers=headers)
    assert delete.status_code == 200

    listing = client.get("/api/v1/docs/list", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["documents"] == []


def test_ask_stream_sse_response(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _configure_adapter_runtime(monkeypatch, tmp_path)
    client = TestClient(create_app())
    headers = _auth_headers(client)

    upload = client.post(
        "/api/v1/docs/upload",
        files={"file": ("rag.txt", b"Grounded response from uploaded content")},
        headers=headers,
    )
    assert upload.status_code == 200

    response = client.get("/api/v1/search/ask/stream", params={"query": "hello"}, headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "data:" in response.text
