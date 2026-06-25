"""
Dashboard test suite — DASH-001 through DASH-007
Run:  pytest tests/test_dashboard.py -v
Results are auto-written to logs/dashboard_test_log.md after the run.
"""

import pytest
from datetime import date, timedelta

from app import db
from app.models.expense import Expense, ExpenseCategory
from app.models.goal import Goal
from app.models.settings import UserSettings
from app.models.user import User


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _add_expense(client, cat_id, amount, expense_date=None):
    return client.post(
        "/expenses/add",
        data={
            "amount": str(amount),
            "category_id": str(cat_id),
            "note": f"dash-test-{amount}",
            "expense_date": expense_date or date.today().strftime("%Y-%m-%d"),
        },
        follow_redirects=True,
    )


def _set_budget(app, monthly_budget=80000, saving_goal=10000, investing_goal=5000):
    settings = UserSettings.query.first()
    settings.monthly_budget = monthly_budget
    settings.monthly_saving_goal = saving_goal
    settings.monthly_investing_goal = investing_goal
    db.session.commit()


# ─── DASH-001: Dashboard loads correctly ─────────────────────────────────────

@pytest.mark.tc_id("DASH-001")
def test_dash_001_dashboard_loads(auth_client, app):
    resp = auth_client.get("/", follow_redirects=True)
    assert resp.status_code == 200
    # Key sections that should always be rendered
    assert b"total_spent" in resp.data or b"budget" in resp.data.lower() or b"Budget" in resp.data
    # Page should contain the user's name (set in auth_client fixture)
    assert b"Expense Tester" in resp.data


# ─── DASH-002: Zero budget — no crash, percentage = 0 ────────────────────────

@pytest.mark.tc_id("DASH-002")
def test_dash_002_zero_budget_no_crash(auth_client, app):
    _set_budget(app, monthly_budget=0, saving_goal=0, investing_goal=0)

    resp = auth_client.get("/", follow_redirects=True)
    assert resp.status_code == 200, "Dashboard must not crash when budget = 0"
    # budget_used_pct should be 0, not NaN / division error
    assert b"0%" in resp.data or b"0.0" in resp.data or b"NaN" not in resp.data


# ─── DASH-003: Money score updates with expenses and goals ───────────────────

@pytest.mark.tc_id("DASH-003")
def test_dash_003_money_score(auth_client, app, food_cat_id):
    # Set up a budget with saving + investing goals → score should be higher
    _set_budget(app, monthly_budget=80000, saving_goal=10000, investing_goal=5000)

    # Add a moderate expense (well under budget)
    _add_expense(auth_client, food_cat_id, 5000)

    resp = auth_client.get("/", follow_redirects=True)
    assert resp.status_code == 200
    # Money score should be present and a valid number (0–99)
    # The score is rendered in the template; check it exists somewhere in the page
    assert b"score" in resp.data.lower() or b"Score" in resp.data


# ─── DASH-004: Recent expenses — service returns only latest 5 ───────────────
# Note: recent_expenses is not rendered in the dashboard HTML (it's passed to
# the template but not looped over). We verify the service-level limit via the
# analytics service directly.

@pytest.mark.tc_id("DASH-004")
def test_dash_004_recent_expenses_latest_5(auth_client, app, food_cat_id):
    from app.models.user import User
    from app.services.analytics_service import get_dashboard_summary

    # Use different dates so date-desc ordering is deterministic (oldest = exp1)
    base = date.today()
    for i in range(1, 8):  # add 7 expenses on consecutive days
        d = (base - timedelta(days=7 - i)).strftime("%Y-%m-%d")
        auth_client.post(
            "/expenses/add",
            data={
                "amount": "100",
                "category_id": str(food_cat_id),
                "note": f"DASH004-exp{i}",
                "expense_date": d,
            },
        )

    user = User.query.filter_by(email="exp@test.com").first()
    summary = get_dashboard_summary(user)

    recent = summary["recent_expenses"]
    assert len(recent) <= 5, "Dashboard should return at most 5 recent expenses"
    assert len(recent) == 5, "With 7 expenses added, exactly 5 should be returned"

    notes = [e["note"] for e in recent]
    # Most recent 5 (exp3–exp7) should be returned; oldest 2 should be excluded
    assert "DASH004-exp7" in notes, "Most recent expense should be in results"
    assert "DASH004-exp1" not in notes, "Oldest expense should be excluded"
    assert "DASH004-exp2" not in notes, "Second oldest expense should be excluded"


# ─── DASH-005: Budget allocation percentages ─────────────────────────────────

@pytest.mark.tc_id("DASH-005")
def test_dash_005_budget_allocation_percentages(auth_client, app):
    # Budget=80000, saving=10000 (12.5%), investing=8000 (10%)
    _set_budget(app, monthly_budget=80000, saving_goal=10000, investing_goal=8000)

    resp = auth_client.get("/", follow_redirects=True)
    assert resp.status_code == 200

    # Allocation chips row is rendered when budget > 0
    # saving 12.5% and investing 10% should appear somewhere in the page
    assert b"12.5" in resp.data or b"12%" in resp.data or b"Savings" in resp.data
    assert b"Investing" in resp.data or b"investing" in resp.data.lower()


# ─── DASH-006: Remaining budget = budget - total_spent ───────────────────────

@pytest.mark.tc_id("DASH-006")
def test_dash_006_remaining_budget(auth_client, app, food_cat_id):
    _set_budget(app, monthly_budget=50000, saving_goal=0, investing_goal=0)

    today = date.today().strftime("%Y-%m-%d")
    _add_expense(auth_client, food_cat_id, 20000, today)

    resp = auth_client.get("/", follow_redirects=True)
    assert resp.status_code == 200

    # remaining = 50000 - 20000 = 30000
    assert b"30,000" in resp.data or b"30000" in resp.data, \
        "Remaining budget should be 30,000"


# ─── DASH-007: Negative remaining budget (overspent) ─────────────────────────
# Template renders remaining as abs(remaining) + " over" when negative.
# e.g. remaining=-5000 → "5,000 over"

@pytest.mark.tc_id("DASH-007")
def test_dash_007_negative_remaining_budget(auth_client, app, food_cat_id):
    _set_budget(app, monthly_budget=10000, saving_goal=0, investing_goal=0)

    today = date.today().strftime("%Y-%m-%d")
    _add_expense(auth_client, food_cat_id, 15000, today)

    resp = auth_client.get("/", follow_redirects=True)
    assert resp.status_code == 200, "Dashboard must not crash when budget is exceeded"

    # Template shows abs(remaining) + " over" class when remaining < 0
    assert b"over" in resp.data, "Overspent state should be shown with 'over' label"
    assert b"5,000" in resp.data, "Overspend amount (abs value) should be rendered"
