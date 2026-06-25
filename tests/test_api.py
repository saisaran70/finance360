"""
API Validation test suite — API-001 through API-008
Run:  pytest tests/test_api.py -v
Results are auto-written to logs/api_test_log.md after the run.
"""

import json
from datetime import date

import pytest

from app import db
from app.models.expense import Expense, ExpenseCategory
from app.models.goal import Goal
from app.models.settings import UserSettings
from app.models.user import User


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_user(app):
    return User.query.filter_by(email="exp@test.com").first()


def _make_user(email, name="Other User"):
    user = User(full_name=name, email=email)
    user.set_password("pass123")
    db.session.add(user)
    db.session.flush()
    db.session.add(UserSettings(user_id=user.id, monthly_budget=50000))
    db.session.commit()
    return user


def _add_expense_db(user_id, amount, note="api-test"):
    cat = ExpenseCategory.query.filter_by(name="Food").first()
    e = Expense(
        user_id=user_id,
        category_id=cat.id,
        amount=amount,
        note=note,
        expense_date=date.today(),
    )
    db.session.add(e)
    db.session.commit()
    return e


def _add_goal_db(user_id, name="API Goal", target=10000, current=2500,
                 monthly=500, goal_type="savings"):
    g = Goal(
        user_id=user_id,
        name=name,
        goal_type=goal_type,
        target_amount=target,
        current_amount=current,
        monthly_contribution=monthly,
        status="active",
    )
    db.session.add(g)
    db.session.commit()
    return g


# ─── API-001: /expenses/data returns only current user's data ─────────────────

@pytest.mark.tc_id("API-001")
def test_api_001_expenses_data_user_isolation(auth_client, app):
    user_a = _get_user(app)
    user_b = _make_user("api001_b@test.com")

    # Create one expense for each user
    _add_expense_db(user_a.id, 1111, note="api001-user-a")
    _add_expense_db(user_b.id, 2222, note="api001-user-b")

    resp = auth_client.get("/expenses/data")
    assert resp.status_code == 200

    data = json.loads(resp.data)
    assert isinstance(data, list)

    notes = [e["note"] for e in data]
    assert "api001-user-a" in notes, "User A's expense should be returned"
    assert "api001-user-b" not in notes, \
        "User B's expense must NOT appear in User A's response"

    amounts = [e["amount"] for e in data]
    assert 2222.0 not in amounts, "User B's amount must not leak into User A's data"


# ─── API-002: /goals/data proper field serialization ─────────────────────────

@pytest.mark.tc_id("API-002")
def test_api_002_goals_serialization(auth_client, app):
    user = _get_user(app)
    _add_goal_db(
        user.id, name="API002 Goal", target=20000,
        current=5000, monthly=1000, goal_type="investment",
    )

    resp = auth_client.get("/goals/data")
    assert resp.status_code == 200
    assert "application/json" in resp.content_type

    data = json.loads(resp.data)
    assert isinstance(data, list)

    goal = next((g for g in data if g["name"] == "API002 Goal"), None)
    assert goal is not None

    # Verify every required field is present and has the correct type
    expected = {
        "id": int,
        "name": str,
        "goal_type": str,
        "target_amount": float,
        "current_amount": float,
        "monthly_contribution": float,
        "progress_percent": (int, float),
        "amount_remaining": (int, float),
        "months_to_goal": (int, type(None)),
        "status": str,
    }
    for field, expected_type in expected.items():
        assert field in goal, f"Missing field: '{field}'"
        assert isinstance(goal[field], expected_type), \
            f"Field '{field}' has wrong type: {type(goal[field])}"

    # Verify computed values are correct
    assert goal["target_amount"] == 20000.0
    assert goal["current_amount"] == 5000.0
    assert goal["monthly_contribution"] == 1000.0
    assert goal["progress_percent"] == 25.0,  "5000/20000 = 25%"
    assert goal["amount_remaining"] == 15000.0, "20000 - 5000 = 15000"
    assert goal["months_to_goal"] == 15, "ceil(15000/1000) = 15"
    assert goal["status"] == "active"
    assert goal["goal_type"] == "investment"


# ─── API-003: /analytics/spending-savings correct JSON schema ─────────────────

@pytest.mark.tc_id("API-003")
def test_api_003_spending_savings_schema(auth_client, app):
    resp = auth_client.get("/analytics/spending-savings?range=6m")
    assert resp.status_code == 200
    assert "application/json" in resp.content_type

    data = json.loads(resp.data)

    # Required top-level keys
    for key in ("labels", "spending", "savings"):
        assert key in data, f"Missing key '{key}' in response"
        assert isinstance(data[key], list), f"'{key}' must be a list"

    # All arrays same length
    n = len(data["labels"])
    assert len(data["spending"]) == n
    assert len(data["savings"]) == n

    # All values must be numeric
    for v in data["spending"]:
        assert isinstance(v, (int, float)), f"spending value '{v}' is not numeric"
    for v in data["savings"]:
        assert isinstance(v, (int, float)), f"savings value '{v}' is not numeric"

    # No extra unexpected keys
    assert set(data.keys()) == {"labels", "spending", "savings"}, \
        f"Unexpected keys in response: {set(data.keys())}"


# ─── API-004: Invalid range query — graceful fallback to 6m ──────────────────

@pytest.mark.tc_id("API-004")
def test_api_004_invalid_range_fallback(auth_client, app):
    invalid_ranges = ["badvalue", "10m", "0", "", "yearly", "ALL"]

    for rng in invalid_ranges:
        resp = auth_client.get(f"/analytics/spending-savings?range={rng}")
        assert resp.status_code == 200, \
            f"Invalid range '{rng}' should not cause an error"
        data = json.loads(resp.data)
        assert len(data["labels"]) == 6, \
            f"Invalid range '{rng}' should fall back to 6m (6 labels), got {len(data['labels'])}"


# ─── API-005: Unauthenticated API access redirects to login ──────────────────

@pytest.mark.tc_id("API-005")
def test_api_005_unauthenticated_api_access(client, app):
    api_endpoints = [
        "/expenses/data",
        "/goals/data",
        "/analytics/spending-savings",
        "/analytics/categories",
        "/analytics/ai-insights",
    ]
    for endpoint in api_endpoints:
        resp = client.get(endpoint, follow_redirects=False)
        assert resp.status_code == 302, \
            f"Unauthenticated GET {endpoint} should redirect (got {resp.status_code})"
        assert "login" in resp.headers["Location"].lower(), \
            f"Redirect for {endpoint} should point to login"


# ─── API-006: Empty dataset returns valid empty JSON arrays ──────────────────

@pytest.mark.tc_id("API-006")
def test_api_006_empty_dataset_response(auth_client, app):
    # Fresh DB — no expenses, no goals
    assert Expense.query.count() == 0
    assert Goal.query.count() == 0

    # /expenses/data → []
    resp = auth_client.get("/expenses/data")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data == [], f"Empty expenses should return [], got {data}"

    # /goals/data → []
    resp = auth_client.get("/goals/data")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data == [], f"Empty goals should return [], got {data}"

    # /analytics/spending-savings → arrays of zeros, not null/error
    resp = auth_client.get("/analytics/spending-savings?range=6m")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data["spending"], list)
    assert all(v == 0 for v in data["spending"]), \
        "spending values should all be 0 for a user with no expenses"

    # /analytics/ai-insights → []
    resp = auth_client.get("/analytics/ai-insights")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list), "AI insights should return a list even when empty"


# ─── API-007: Date formatting matches spec ────────────────────────────────────

@pytest.mark.tc_id("API-007")
def test_api_007_date_formatting(auth_client, app):
    user = _get_user(app)
    # Add expense on a fixed known date
    cat = ExpenseCategory.query.filter_by(name="Food").first()
    e = Expense(
        user_id=user.id,
        category_id=cat.id,
        amount=500,
        note="api007-date",
        expense_date=date(2026, 3, 15),
    )
    db.session.add(e)
    db.session.commit()

    resp = auth_client.get("/expenses/data")
    data = json.loads(resp.data)

    entry = next((e for e in data if e["note"] == "api007-date"), None)
    assert entry is not None

    # Machine-readable format: YYYY-MM-DD
    assert entry["date"] == "2026-03-15", \
        f"'date' should be YYYY-MM-DD, got '{entry['date']}'"

    # Human-readable format: DD Mon YYYY
    assert entry["date_display"] == "15 Mar 2026", \
        f"'date_display' should be DD Mon YYYY, got '{entry['date_display']}'"

    # Goals API: target_date uses YYYY-MM-DD
    g = Goal(
        user_id=user.id,
        name="api007-goal",
        target_amount=10000,
        current_amount=0,
        status="active",
        target_date=date(2026, 12, 31),
    )
    db.session.add(g)
    db.session.commit()

    resp = auth_client.get("/goals/data")
    goals = json.loads(resp.data)
    goal_entry = next((g for g in goals if g["name"] == "api007-goal"), None)
    assert goal_entry is not None
    assert goal_entry["target_date"] == "2026-12-31", \
        f"Goal target_date should be YYYY-MM-DD, got '{goal_entry['target_date']}'"


# ─── API-008: User currency reflected in analytics summary ───────────────────

@pytest.mark.tc_id("API-008")
def test_api_008_currency_consistency(auth_client, app):
    from app.services.analytics_service import get_dashboard_summary

    user = _get_user(app)

    # Default currency is INR
    assert user.currency == "INR"
    summary = get_dashboard_summary(user)
    assert summary["currency"] == "INR", \
        f"Default currency should be INR, got '{summary['currency']}'"

    # Change currency to USD via settings
    auth_client.post("/settings/update", data={
        "full_name": user.full_name,
        "currency": "USD",
        "city": "",
        "monthly_budget": "80000",
        "monthly_saving_goal": "10000",
        "monthly_investing_goal": "5000",
    })

    db.session.refresh(user)
    assert user.currency == "USD"

    # Analytics summary must reflect the new currency
    summary = get_dashboard_summary(user)
    assert summary["currency"] == "USD", \
        f"Currency should update to USD, got '{summary['currency']}'"

    # Dashboard page should render USD
    resp = auth_client.get("/", follow_redirects=True)
    assert b"USD" in resp.data, "Dashboard HTML should contain the updated currency"
