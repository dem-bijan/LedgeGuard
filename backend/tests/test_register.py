"""
Milestone 4 test: user registration, including the duplicate-email
defense-in-depth (proactive check + DB-level backstop under real
concurrency) discussed during this milestone.
"""

import threading

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import engine
from app.main import app
from app.users import EmailAlreadyExistsException, register

client = TestClient(app)


def test_register_succeeds(db_session):
    response = client.post(
        "/register",
        json={"full_name": "Alice", "email": "alice-register@example.com", "password": "supersecret123"},
    )
    assert response.status_code == 201
    assert response.json()["id"]


def test_register_rejects_duplicate_email(db_session):
    payload = {"full_name": "Alice", "email": "dup-register@example.com", "password": "supersecret123"}
    r1 = client.post("/register", json=payload)
    r2 = client.post("/register", json=payload)

    assert r1.status_code == 201
    assert r2.status_code == 409


def test_register_rejects_short_password(db_session):
    response = client.post(
        "/register",
        json={"full_name": "Alice", "email": "weak-password@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_register_handles_concurrent_duplicate_registration(db_session):
    """Proactive check alone has a race window; this proves the DB-level
    backstop actually closes it under real concurrency, not just when
    requests happen to arrive one after another."""
    results = {}
    barrier = threading.Barrier(2)

    def attempt(name):
        session = Session(engine)
        try:
            barrier.wait()
            register(session, name, "race-register@example.com", "supersecret123", "customer")
            results[name] = "success"
        except EmailAlreadyExistsException:
            results[name] = "rejected"
        finally:
            session.close()

    t1 = threading.Thread(target=attempt, args=("t1",))
    t2 = threading.Thread(target=attempt, args=("t2",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    outcomes = [results["t1"], results["t2"]]
    assert outcomes.count("success") == 1
    assert outcomes.count("rejected") == 1
