"""
Milestone 4 test: login issues a real JWT, and wrong password / unknown
email both fail with the exact same message (don't leak which one it was).
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _register(email, password="supersecret123"):
    client.post("/register", json={"full_name": "Login Test", "email": email, "password": password})


def test_login_succeeds_and_returns_a_token(db_session):
    _register("login-success@example.com")

    response = client.post("/login", json={"email": "login-success@example.com", "password": "supersecret123"})

    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token.count(".") == 2  # header.payload.signature


def test_login_rejects_wrong_password(db_session):
    _register("login-wrong-password@example.com")

    response = client.post(
        "/login", json={"email": "login-wrong-password@example.com", "password": "not-the-password"}
    )

    assert response.status_code == 400


def test_login_rejects_unknown_email_with_same_message_as_wrong_password(db_session):
    _register("login-known@example.com")

    wrong_password = client.post(
        "/login", json={"email": "login-known@example.com", "password": "not-the-password"}
    )
    unknown_email = client.post(
        "/login", json={"email": "nobody-at-all@example.com", "password": "supersecret123"}
    )

    assert wrong_password.status_code == unknown_email.status_code == 400
    assert wrong_password.json() == unknown_email.json()
