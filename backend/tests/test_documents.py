from fastapi.testclient import TestClient


def test_upload_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/api/v1/docs/upload",
        files={"file": ("notes.txt", b"alpha beta gamma")},
    )

    assert response.status_code == 401


def test_upload_list_get_delete_document(client: TestClient, auth_headers) -> None:
    headers = auth_headers("doc-user@example.com")

    upload = client.post(
        "/api/v1/docs/upload",
        files={"file": ("notes.txt", b"alpha beta gamma")},
        headers=headers,
    )
    assert upload.status_code == 200
    doc_id = upload.json()["doc_id"]

    listing = client.get("/api/v1/docs/list", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()["documents"]) == 1

    get_doc = client.get(f"/api/v1/docs/{doc_id}", headers=headers)
    assert get_doc.status_code == 200
    assert get_doc.json()["doc_id"] == doc_id

    delete = client.delete(f"/api/v1/docs/{doc_id}", headers=headers)
    assert delete.status_code == 200

    listing_after = client.get("/api/v1/docs/list", headers=headers)
    assert listing_after.status_code == 200
    assert listing_after.json()["documents"] == []


def test_document_isolation_between_users(client: TestClient, auth_headers) -> None:
    headers_a = auth_headers("user-a@example.com")
    headers_b = auth_headers("user-b@example.com")

    upload_a = client.post(
        "/api/v1/docs/upload",
        files={"file": ("a.txt", b"document from user a")},
        headers=headers_a,
    )
    assert upload_a.status_code == 200

    upload_b = client.post(
        "/api/v1/docs/upload",
        files={"file": ("b.txt", b"document from user b")},
        headers=headers_b,
    )
    assert upload_b.status_code == 200

    list_a = client.get("/api/v1/docs/list", headers=headers_a)
    list_b = client.get("/api/v1/docs/list", headers=headers_b)

    assert len(list_a.json()["documents"]) == 1
    assert len(list_b.json()["documents"]) == 1
    assert list_a.json()["documents"][0]["file_name"].endswith("a.txt")
    assert list_b.json()["documents"][0]["file_name"].endswith("b.txt")
