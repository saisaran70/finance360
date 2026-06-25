"""
Analytics module test suite — ANA-001 through ANA-012
Run:  pytest tests/test_analytics.py -v
Results are auto-written to logs/analytics_test_log.md after the run.
"""

import json
from datetime import date

import pytest

from app import db
from app.models.expense import Expense, ExpenseCategory
from app.models.goal import Goal
from app.models.recurring import RecurringExpense
from app.models.settings import UserSettings
from app.models.user import User


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _add_expense(client, cat_id, amount, expense_date=None):
    client.post("/expenses/add", data={
        "amount": str(amount),
        "category_id": str(cat_id),
        "note": f"ana-{amount}",
        "expense_date": expense_date or date.today().strftime("%Y-%m-%d"),
    })


def _set_budget(app, budget=80000, saving=10000, investing=5000):
    s = UserSettings.query.first()
    s.monthly_budget = budget
    s.monthly_saving_goal = saving
    s.monthly_investing_goal = investing
    db.session.commit()


def _get_user(app):
    return User.query.filter_by(email="exp@test.com").first()


def _spending_savings(client, range_key="6m"):
    resp = client.get(f"/analytics/spending-savings?range={range_key}")
    return json.loads(resp.data), resp


# ─── ANA-001: Analytics page loads ───────────────────────────────────────────

@pytest.mark.tc_id("ANA-001")
def test_ana_001_analytics_page_loads(auth_client, app):
    resp = auth_client.get("/analytics/")
    assert resp.status_code == 200
    # Core landmarks rendered server-side
    assert b"analytics" in resp.data.lower() or b"Analytics" in resp.data
    assert b"Spending" in resp.data or b"spending" in resp.data.lower()


# ─── ANA-002: Spending vs savings JSON schema ─────────────────────────────────

@pytest.mark.tc_id("ANA-002")
def test_ana_002_spending_savings_schema(auth_client, app):
    data, resp = _spending_savings(auth_client)

    assert resp.status_code == 200
    assert "application/json" in resp.content_type

    assert "labels" in data,   "Response must contain 'labels'"
    assert "spending" in data, "Response must contain 'spending'"
    assert "savings" in data,  "Response must contain 'savings'"

    assert isinstance(data["labels"],   list)
    assert isinstance(data["spending"], list)
    assert isinstance(data["savings"],  list)

    # All three arrays must be the same length
    assert len(data["labels"]) == len(data["spending"]) == len(data["savings"])


# ─── ANA-003: 7-day range — 7 daily labels ───────────────────────────────────

@pytest.mark.tc_id("ANA-003")
def test_ana_003_7day_range(auth_client, app):
    data, resp = _spending_savings(auth_client, "7d")
    assert resp.status_code == 200
    assert len(data["labels"]) == 7, "7d range must return exactly 7 data points"
    # Daily labels format: "DD Mon" e.g. "27 May"
    for label in data["labels"]:
        parts = label.split(" ")
        assert len(parts) == 2, f"Daily label '{label}' should be 'DD Mon'"
        assert parts[0].isdigit(), f"Day part '{parts[0]}' should be numeric"


# ─── ANA-004: 30-day range — 30 daily labels ─────────────────────────────────

@pytest.mark.tc_id("ANA-004")
def test_ana_004_30day_range(auth_client, app):
    data, resp = _spending_savings(auth_client, "30d")
    assert resp.status_code == 200
    assert len(data["labels"]) == 30, "30d range must return exactly 30 data points"
    # Daily format check
    for label in data["labels"]:
        parts = label.split(" ")
        assert len(parts) == 2 and parts[0].isdigit()


# ─── ANA-005: 6-month range — 6 monthly labels ───────────────────────────────

@pytest.mark.tc_id("ANA-005")
def test_ana_005_6month_range(auth_client, app):
    data, resp = _spending_savings(auth_client, "6m")
    assert resp.status_code == 200
    assert len(data["labels"]) == 6, "6m range must return exactly 6 data points"
    # Monthly labels format: "Mon YYYY" e.g. "Jan 2026"
    for label in data["labels"]:
        parts = label.split(" ")
        assert len(parts) == 2, f"Monthly label '{label}' should be 'Mon YYYY'"
        assert parts[1].isdigit() and len(parts[1]) == 4, "Year should be 4 digits"


# ─── ANA-006: 1-year range — 12 monthly labels ───────────────────────────────

@pytest.mark.tc_id("ANA-006")
def test_ana_006_1year_range(auth_client, app):
    data, resp = _spending_savings(auth_client, "1y")
    assert resp.status_code == 200
    assert len(data["labels"]) == 12, "1y range must return exactly 12 data points"
    for label in data["labels"]:
        parts = label.split(" ")
        assert len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 4


# ─── ANA-007: Negative savings when spending > budget ────────────────────────

@pytest.mark.tc_id("ANA-007")
def test_ana_007_negative_savings(auth_client, app, food_cat_id):
    # budget=10000, investing=0  →  effective savings base = 10000
    _set_budget(app, budget=10000, saving=0, investing=0)

    # Spend 15000 this month → savings = 10000 - 15000 = -5000
    today = date.today().strftime("%Y-%m-%d")
    _add_expense(auth_client, food_cat_id, 15000, today)

    data, _ = _spending_savings(auth_client, "6m")

    # Find the current month entry (last label = current month)
    current_month_savings = data["savings"][-1]
    assert current_month_savings < 0, (
        f"Savings should be negative when spending ({15000}) > budget ({10000}), "
        f"got {current_month_savings}"
    )
    assert current_month_savings == -5000, \
        f"Expected savings = -5000, got {current_month_savings}"


# ─── ANA-008: Category percentages sum to ~100 ───────────────────────────────

@pytest.mark.tc_id("ANA-008")
def test_ana_008_category_percentages_sum_100(auth_client, app):
    from app.services.analytics_service import get_category_breakdown

    today = date.today().strftime("%Y-%m-%d")
    categories = ExpenseCategory.query.limit(4).all()
    # Add equal amounts across 4 categories (25% each → 100% total)
    for cat in categories:
        _add_expense(auth_client, cat.id, 2500, today)

    user = _get_user(app)
    breakdown = get_category_breakdown(user)

    # Filter to rows that have actual spending
    spending_rows = [r for r in breakdown if r["amount"] > 0]
    assert len(spending_rows) > 0, "Should have at least one category with spending"

    total_pct = sum(r["percentage"] for r in spending_rows)
    assert abs(total_pct - 100.0) <= 0.5, (
        f"Category percentages should sum to ~100, got {total_pct}"
    )

    # Each individual percentage must be between 0 and 100
    for r in spending_rows:
        assert 0 <= r["percentage"] <= 100, \
            f"Percentage {r['percentage']} out of range for category {r['category']}"


# ─── ANA-009: Fixed cost monthly equivalents ─────────────────────────────────

@pytest.mark.tc_id("ANA-009")
def test_ana_009_fixed_cost_monthly_equivalents(auth_client, app):
    from app.services.analytics_service import get_fixed_cost_analysis

    user = _get_user(app)
    food_cat = ExpenseCategory.query.filter_by(name="Food").first()

    # Add 3 fixed costs with different billing cycles
    monthly_item = RecurringExpense(
        user_id=user.id, category_id=food_cat.id,
        title="Rent", amount=12000, billing_cycle="monthly",
    )
    yearly_item = RecurringExpense(
        user_id=user.id, category_id=food_cat.id,
        title="Domain", amount=1200, billing_cycle="yearly",   # → 100/month
    )
    weekly_item = RecurringExpense(
        user_id=user.id, category_id=food_cat.id,
        title="Groceries", amount=1000, billing_cycle="weekly",  # → 4330/month
    )
    db.session.add_all([monthly_item, yearly_item, weekly_item])
    db.session.commit()

    result = get_fixed_cost_analysis(user)
    by_title = {r["title"]: r for r in result}

    assert "Rent" in by_title
    assert by_title["Rent"]["monthly_equiv"] == 12000, \
        "Monthly billing: equiv should equal amount"

    assert "Domain" in by_title
    assert by_title["Domain"]["monthly_equiv"] == round(1200 / 12), \
        "Yearly billing: equiv should be amount / 12"

    assert "Groceries" in by_title
    assert by_title["Groceries"]["monthly_equiv"] == round(1000 * 4.33), \
        "Weekly billing: equiv should be amount * 4.33"

    # Verify billing_cycle and amount are returned correctly
    assert by_title["Rent"]["billing_cycle"] == "monthly"
    assert by_title["Domain"]["billing_cycle"] == "yearly"
    assert by_title["Groceries"]["billing_cycle"] == "weekly"


# ─── ANA-010: AI insights endpoint returns JSON array ────────────────────────

@pytest.mark.tc_id("ANA-010")
def test_ana_010_ai_insights_endpoint(auth_client, app):
    resp = auth_client.get("/analytics/ai-insights")
    assert resp.status_code == 200
    assert "application/json" in resp.content_type

    data = json.loads(resp.data)
    assert isinstance(data, list), "AI insights endpoint should return a JSON array"
    # For a new user with no AI insights, the list should be empty (not an error)
    # If insights exist, each should have required fields
    for insight in data:
        for field in ("title", "message", "type"):
            assert field in insight, f"Missing field '{field}' in AI insight"


# ─── ANA-011: No expenses — empty state handled ───────────────────────────────

@pytest.mark.tc_id("ANA-011")
def test_ana_011_no_expenses_empty_state(auth_client, app):
    # Fresh DB — user has no expenses at all
    assert Expense.query.count() == 0, "Should start with no expenses"

    resp = auth_client.get("/analytics/")
    assert resp.status_code == 200, "Analytics page must load without expenses"

    # Spending vs savings should return zeros, not crash
    data, spend_resp = _spending_savings(auth_client, "6m")
    assert spend_resp.status_code == 200
    assert all(v == 0 for v in data["spending"]), "All spending values should be 0"


# ─── ANA-012: Goal analytics totals ──────────────────────────────────────────

@pytest.mark.tc_id("ANA-012")
def test_ana_012_goal_analytics_totals(auth_client, app):
    from app.services.analytics_service import get_goal_analytics

    user = _get_user(app)

    # Create two active goals
    goal_a = Goal(user_id=user.id, name="Emergency Fund",
                  target_amount=100000, current_amount=30000, status="active")
    goal_b = Goal(user_id=user.id, name="Vacation",
                  target_amount=50000, current_amount=20000, status="active")
    # Completed goal — should NOT be counted
    goal_c = Goal(user_id=user.id, name="Old Goal",
                  target_amount=5000, current_amount=5000, status="completed")
    db.session.add_all([goal_a, goal_b, goal_c])
    db.session.commit()

    result = get_goal_analytics(user)

    assert result["has_goals"] is True
    assert result["total_target"] == 150000.0,  "target = 100000 + 50000"
    assert result["total_saved"]  == 50000.0,   "saved = 30000 + 20000"
    assert result["remaining"]    == 100000.0,  "remaining = 150000 - 50000"
    assert result["pct_funded"]   == 33,        "pct = round(50000/150000*100) = 33"
