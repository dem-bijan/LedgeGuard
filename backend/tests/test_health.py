"""
Milestone 1 test: all services can boot and reach each other.

This is an integration test, not a unit test — it requires the real Postgres
container (`docker compose up -d`) to be running. We're deliberately testing
against the real DB here because the thing we actually care about at this
stage is "can the app reach the database through the real network path,"
which a mock would just assume away.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_reports_ok_when_db_reachable():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["db"] is True
