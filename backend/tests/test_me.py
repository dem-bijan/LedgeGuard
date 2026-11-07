"""Milestone 4 test: GET /me -- lets the frontend ask "who's logged in?"
since it can't read the httpOnly cookie itself."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_me_returns_the_logged_in_user(db_session):
    client.post(
        "/register",
        json={"full_name": "Me Test", "email": "me-endpoint-test@example.com", "password": "supersecret123"},
    )
    client.post("/login", json={"email": "me-endpoint-test@example.com", "password": "supersecret123"})

    response = client.get("/me")

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "me-endpoint-test@example.com"
    assert "hashed_password" not in body


def test_me_requires_auth():
    anonymous_client = TestClient(app)
    response = anonymous_client.get("/me")
    assert response.status_code == 401
