from fastapi.testclient import TestClient


def test_semantic_search_returns_ranked_results(client: TestClient, auth_headers) -> None:
    headers = auth_headers("search-user@example.com")
    client.post(
        "/api/v1/docs/upload",
        files={"file": ("search.txt", b"The project needs semantic search and retrieval")},
        headers=headers,
    )

    semantic = client.post(
        "/api/v1/search/semantic",
        json={"query": "semantic retrieval", "top_k": 5},
        headers=headers,
    )
    assert semantic.status_code == 200
    body = semantic.json()
    assert body["results"]
    assert body["results"][0]["score"] >= 0.0


def test_semantic_search_user_isolation(client: TestClient, auth_headers) -> None:
    headers_a = auth_headers("search-a@example.com")
    headers_b = auth_headers("search-b@example.com")

    client.post(
        "/api/v1/docs/upload",
        files={"file": ("a.txt", b"content for user a only")},
        headers=headers_a,
    )
    client.post(
        "/api/v1/docs/upload",
        files={"file": ("b.txt", b"content for user b only")},
        headers=headers_b,
    )

    res_a = client.post(
        "/api/v1/search/semantic",
        json={"query": "user a", "top_k": 10},
        headers=headers_a,
    )
    res_b = client.post(
        "/api/v1/search/semantic",
        json={"query": "user b", "top_k": 10},
        headers=headers_b,
    )

    assert res_a.status_code == 200
    assert res_b.status_code == 200
    files_a = {row["file_name"] for row in res_a.json()["results"]}
    files_b = {row["file_name"] for row in res_b.json()["results"]}
    assert files_a and files_b
    assert files_a.isdisjoint(files_b)


def test_ask_stream_returns_sse_events(client: TestClient, auth_headers) -> None:
    headers = auth_headers("ask-user@example.com")
    client.post(
        "/api/v1/docs/upload",
        files={"file": ("rag.txt", b"streaming answer should include events")},
        headers=headers,
    )

    response = client.get(
        "/api/v1/search/ask/stream",
        params={"query": "stream"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "\"type\": \"meta\"" in response.text
    assert "\"type\": \"done\"" in response.text
