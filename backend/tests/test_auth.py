from fastapi.testclient import TestClient


def test_register_login_me_flow(client: TestClient) -> None:
    payload = {"email": "auth-user@example.com", "password": "password123"}
    register = client.post("/api/v1/auth/register", json=payload)
    assert register.status_code == 200

    login = client.post("/api/v1/auth/login", json=payload)
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == payload["email"]


def test_register_duplicate_email_returns_400(client: TestClient) -> None:
    payload = {"email": "dup@example.com", "password": "password123"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 200
    duplicate = client.post("/api/v1/auth/register", json=payload)
    assert duplicate.status_code == 400


def test_login_invalid_password_returns_401(client: TestClient) -> None:
    payload = {"email": "bad-login@example.com", "password": "password123"}
    client.post("/api/v1/auth/register", json=payload)

    bad = client.post("/api/v1/auth/login", json={"email": payload["email"], "password": "wrong"})
    assert bad.status_code == 401


def test_me_requires_token(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
