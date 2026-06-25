"""
Edge Cases test suite — EDGE-001 through EDGE-010
Run:  pytest tests/test_edge_cases.py -v
Results are auto-written to logs/edge_cases_test_log.md after the run.
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

def _get_user(app):
    return User.query.filter_by(email="exp@test.com").first()


def _add_expense(client, cat_id, amount, note="edge", expense_date=None):
    return client.post("/expenses/add", data={
        "amount": str(amount),
        "category_id": str(cat_id),
        "note": note,
        "expense_date": expense_date or date.today().strftime("%Y-%m-%d"),
    }, follow_redirects=True)


def _set_budget(app, budget=80000, saving=10000, investing=5000):
    s = UserSettings.query.first()
    s.monthly_budget = budget
    s.monthly_saving_goal = saving
    s.monthly_investing_goal = investing
    db.session.commit()


# ─── EDGE-001: Extremely large expense amount ─────────────────────────────────

@pytest.mark.tc_id("EDGE-001")
def test_edge_001_large_amount(auth_client, app, food_cat_id):
    resp = _add_expense(auth_client, food_cat_id, 99999999, note="edge001-large")
    assert resp.status_code == 200

    expense = Expense.query.filter_by(note="edge001-large").first()
    assert expense is not None, "Large amount expense should be saved"
    assert float(expense.amount) == 99999999.0, \
        f"Expected 99999999.0, got {float(expense.amount)}"


# ─── EDGE-002: Decimal amount precision ──────────────────────────────────────

@pytest.mark.tc_id("EDGE-002")
def test_edge_002_decimal_precision(auth_client, app, food_cat_id):
    resp = _add_expense(auth_client, food_cat_id, "1234.56", note="edge002-decimal")
    assert resp.status_code == 200

    expense = Expense.query.filter_by(note="edge002-decimal").first()
    assert expense is not None
    assert float(expense.amount) == 1234.56, \
        f"Decimal precision lost: expected 1234.56, got {float(expense.amount)}"

    # Verify via JSON API too
    data = json.loads(auth_client.get("/expenses/data").data)
    entry = next((e for e in data if e["note"] == "edge002-decimal"), None)
    assert entry is not None
    assert entry["amount"] == 1234.56


# ─── EDGE-003: No expenses this month — dashboard graceful ───────────────────

@pytest.mark.tc_id("EDGE-003")
def test_edge_003_no_expenses_this_month(auth_client, app, food_cat_id):
    _set_budget(app, budget=50000)

    # Add an expense in a past month only
    _add_expense(auth_client, food_cat_id, 1000,
                 note="edge003-old", expense_date="2025-01-15")

    resp = auth_client.get("/", follow_redirects=True)
    assert resp.status_code == 200, "Dashboard must load with no expenses this month"

    # total_spent this month should be 0
    from app.services.analytics_service import get_dashboard_summary
    summary = get_dashboard_summary(_get_user(app))
    assert summary["total_spent"] == 0.0, \
        "total_spent should be 0 when no expenses logged this month"
    assert summary["budget_used_pct"] == 0, \
        "budget_used_pct should be 0 when nothing is spent"


# ─── EDGE-004: All goals completed — analytics updates correctly ──────────────

@pytest.mark.tc_id("EDGE-004")
def test_edge_004_all_goals_completed(auth_client, app):
    from app.services.analytics_service import get_goal_analytics

    user = _get_user(app)

    # Create two goals and complete both
    for name, target in [("Edge Goal A", 1000), ("Edge Goal B", 2000)]:
        g = Goal(user_id=user.id, name=name,
                 target_amount=target, current_amount=target, status="completed")
        db.session.add(g)
    db.session.commit()

    result = get_goal_analytics(user)
    # No active goals → has_goals=False, all totals 0
    assert result["has_goals"] is False, \
        "has_goals should be False when all goals are completed"
    assert result["total_target"] == 0.0
    assert result["total_saved"] == 0.0
    assert result["pct_funded"] == 0

    # Analytics page must still load without crashing
    resp = auth_client.get("/analytics/")
    assert resp.status_code == 200


# ─── EDGE-005: Deleted Goals category recreated on contribution ───────────────

@pytest.mark.tc_id("EDGE-005")
def test_edge_005_deleted_goals_category_recreated(auth_client, app):
    # Confirm Goals category does NOT exist in fresh DB
    assert ExpenseCategory.query.filter_by(name="Goals").first() is None

    # Create a goal and trigger _log_goal_expense by setting initial amount
    auth_client.post("/goals/add", data={
        "name": "edge005-goal",
        "goal_type": "savings",
        "target_amount": "10000",
        "current_amount": "500",   # triggers _log_goal_expense → creates Goals cat
        "monthly_contribution": "0",
    })

    goals_cat = ExpenseCategory.query.filter_by(name="Goals").first()
    assert goals_cat is not None, "Goals category should be auto-created"

    # Manually delete the Goals category via raw SQL — bypasses ORM cascade
    # (simulates a real manual DB deletion without touching related expense rows)
    from sqlalchemy import text
    db.session.execute(text("DELETE FROM expense_categories WHERE name = 'Goals'"))
    db.session.commit()
    db.session.expire_all()  # clear ORM identity map so next query hits the DB
    assert ExpenseCategory.query.filter_by(name="Goals").first() is None

    # Make another contribution — Goals category must be recreated
    goal = Goal.query.filter_by(name="edge005-goal").first()
    auth_client.post(f"/goals/{goal.id}/contribute",
                     data={"amount": "200"}, follow_redirects=True)

    recreated = ExpenseCategory.query.filter_by(name="Goals").first()
    assert recreated is not None, \
        "Goals category should be recreated automatically on next contribution"
    assert recreated.color == "#A78BFA"
    assert recreated.icon == "target"


# ─── EDGE-006: Fixed costs exceed budget — dashboard still calculates ─────────

@pytest.mark.tc_id("EDGE-006")
def test_edge_006_fixed_costs_exceed_budget(auth_client, app):
    user = _get_user(app)
    _set_budget(app, budget=10000, saving=0, investing=0)

    # Add fixed costs totalling more than the budget
    food_cat = ExpenseCategory.query.filter_by(name="Food").first()
    db.session.add(RecurringExpense(
        user_id=user.id, category_id=food_cat.id,
        title="edge006-rent", amount=15000, billing_cycle="monthly",
    ))
    db.session.commit()

    # Dashboard must not crash
    resp = auth_client.get("/", follow_redirects=True)
    assert resp.status_code == 200, \
        "Dashboard must not crash when fixed costs exceed budget"

    # Verify summary still computes (fixed_cost_monthly > monthly_budget)
    from app.services.analytics_service import get_dashboard_summary
    summary = get_dashboard_summary(user)
    assert summary["fixed_cost_monthly"] == 15000, \
        "Fixed cost monthly should reflect the recurring expense"
    assert summary["monthly_budget"] == 10000


# ─── EDGE-007: Brand new user — analytics empty state ────────────────────────

@pytest.mark.tc_id("EDGE-007")
def test_edge_007_new_user_empty_analytics(auth_client, app):
    # Fresh DB — auth_client user has zero expenses, goals, fixed costs
    assert Expense.query.count() == 0
    assert Goal.query.count() == 0
    assert RecurringExpense.query.count() == 0

    resp = auth_client.get("/analytics/")
    assert resp.status_code == 200, "Analytics page must load for a brand new user"

    # All API endpoints must return valid empty responses
    endpoints = [
        ("/analytics/categories",        list),
        ("/analytics/trends",            list),
        ("/analytics/fixed-costs",       list),
        ("/analytics/ai-insights",       list),
    ]
    for endpoint, expected_type in endpoints:
        r = auth_client.get(endpoint)
        assert r.status_code == 200, f"{endpoint} should return 200"
        data = json.loads(r.data)
        assert isinstance(data, expected_type), \
            f"{endpoint} should return a {expected_type.__name__}, got {type(data)}"

    # Spending/savings trend must return zero arrays
    r = auth_client.get("/analytics/spending-savings?range=6m")
    data = json.loads(r.data)
    assert all(v == 0 for v in data["spending"])
    assert len(data["labels"]) == 6


# ─── EDGE-008: Custom date filter with from > to ──────────────────────────────

@pytest.mark.tc_id("EDGE-008")
def test_edge_008_invalid_custom_date_range(auth_client, app, food_cat_id):
    # Add an expense inside the "reversed" range to confirm it's excluded
    _add_expense(auth_client, food_cat_id, 500,
                 note="edge008-expense", expense_date="2026-03-15")

    # from=May > to=January → no matching expenses (graceful empty result)
    resp = auth_client.get(
        "/expenses/?period=custom&from=2026-05-31&to=2026-01-01"
    )
    assert resp.status_code == 200, "Page must not crash with reversed date range"

    # The expense added for March should NOT appear (it's outside both boundaries)
    assert b"edge008-expense" not in resp.data, \
        "No expenses should match an impossible date range"


# ─── EDGE-009: Leap year date expense ────────────────────────────────────────

@pytest.mark.tc_id("EDGE-009")
def test_edge_009_leap_year_date(auth_client, app, food_cat_id):
    # 2028 is a leap year — Feb 29 is valid
    resp = _add_expense(auth_client, food_cat_id, 250,
                        note="edge009-leap", expense_date="2028-02-29")
    assert resp.status_code == 200

    expense = Expense.query.filter_by(note="edge009-leap").first()
    assert expense is not None, "Leap year expense should be saved"
    assert expense.expense_date == date(2028, 2, 29), \
        f"Date should be 2028-02-29, got {expense.expense_date}"

    # Verify via JSON API
    data = json.loads(auth_client.get("/expenses/data?period=all").data)
    entry = next((e for e in data if e["note"] == "edge009-leap"), None)
    assert entry is not None
    assert entry["date"] == "2028-02-29"
    assert entry["date_display"] == "29 Feb 2028"


# ─── EDGE-010: Unicode and emoji in note field ────────────────────────────────

@pytest.mark.tc_id("EDGE-010")
def test_edge_010_unicode_emoji_note(auth_client, app, food_cat_id):
    notes = [
        ("edge010-emoji",   "🍕 Pizza dinner 🎉"),
        ("edge010-hindi",   "खाना - दोपहर का भोजन"),
        ("edge010-mixed",   "Café ₹450 — थैंक्यू!"),
    ]

    for marker, note in notes:
        auth_client.post("/expenses/add", data={
            "amount": "100",
            "category_id": str(food_cat_id),
            "note": note,
            "expense_date": date.today().strftime("%Y-%m-%d"),
        })

    # Verify all notes stored correctly in DB
    for marker, note in notes:
        expense = Expense.query.filter_by(note=note).first()
        assert expense is not None, f"Expense with note '{note}' should be saved"
        assert expense.note == note, \
            f"Note stored incorrectly: expected '{note}', got '{expense.note}'"

    # Verify via JSON API — unicode round-trips correctly
    data = json.loads(auth_client.get("/expenses/data").data)
    stored_notes = [e["note"] for e in data]
    for _, note in notes:
        assert note in stored_notes, f"Note '{note}' missing from API response"

    # Expenses page must render without error
    resp = auth_client.get("/expenses/")
    assert resp.status_code == 200, \
        "Expenses page must render unicode notes without crashing"
