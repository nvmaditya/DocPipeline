"""End-to-end integration journeys spanning multiple backend modules."""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_e2e_document_lifecycle(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    auth_headers,
    client: TestClient,
) -> None:
    """Register -> Upload file -> Process -> Search -> Delete."""
    headers = auth_headers()
    
    # 1. Upload a document
    file_content = b"Ollama phi3 is a powerful local model for testing document pipelines."
    files = {"file": ("test_doc.txt", file_content, "text/plain")}
    upload_resp = client.post("/api/v1/documents/upload", headers=headers, files=files)
    assert upload_resp.status_code == 200
    doc_id = upload_resp.json()["id"]

    # Allow background processing to finish
    time.sleep(1)

    # 2. Verify document list
    list_resp = client.get("/api/v1/documents", headers=headers)
    assert list_resp.status_code == 200
    docs = list_resp.json()["documents"]
    assert any(d["id"] == doc_id for d in docs)

    # 3. Search
    search_resp = client.post(
        "/api/v1/search/semantic",
        headers=headers,
        json={"query": "Ollama phi3", "top_k": 3}
    )
    assert search_resp.status_code == 200

    # 4. Ask
    ask_resp = client.get(
        "/api/v1/search/ask/stream",
        headers=headers,
        params={"query": "What model is used for testing?"}
    )
    assert ask_resp.status_code == 200
    assert "data:" in ask_resp.text

    # 5. Delete
    del_resp = client.delete(f"/api/v1/documents/{doc_id}", headers=headers)
    assert del_resp.status_code == 200


@pytest.mark.integration
def test_e2e_community_module_orchestration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    auth_headers,
    client: TestClient,
) -> None:
    """Test web_extractor trigger via community modules creation."""
    headers = auth_headers()
    
    # Create module (will spawn subprocess to run web_extractor with phi3)
    resp = client.post(
        "/api/v1/community/modules",
        headers=headers,
        json={"topic": "Pytest integration testing"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "database_id" in data
    
    # Query the newly created database
    ask_resp = client.get(
        "/api/v1/search/ask/stream",
        headers=headers,
        params={
            "query": "What is integration testing?",
            "database_id": data["database_id"]
        }
    )
    assert ask_resp.status_code == 200
    assert "data:" in ask_resp.text
