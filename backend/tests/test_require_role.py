"""
Milestone 4 test: require_role() — built now for Milestone 5's analyst-only
routes, which don't exist yet.
"""

import uuid

import pytest
from fastapi import HTTPException

from app.dependencies import require_role
from app.models import User


def test_require_role_returns_user_when_role_matches(db_session):
    analyst = User(full_name="Analyst", email=f"{uuid.uuid4().hex}@test.local", hashed_password="x", role="analyst")
    db_session.add(analyst)
    db_session.commit()

    check = require_role("analyst")
    result = check(current_user=analyst)

    assert result is analyst


def test_require_role_rejects_wrong_role(db_session):
    customer = User(full_name="Customer", email=f"{uuid.uuid4().hex}@test.local", hashed_password="x", role="customer")
    db_session.add(customer)
    db_session.commit()

    check = require_role("analyst")
    with pytest.raises(HTTPException) as exc_info:
        check(current_user=customer)

    assert exc_info.value.status_code == 403
