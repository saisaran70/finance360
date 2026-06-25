"""
Goal Management test suite — GOAL-001 through GOAL-016
Run:  pytest tests/test_goals.py -v
Results are auto-written to logs/goals_test_log.md after the run.
"""

import json

import pytest

from app import db
from app.models.expense import Expense, ExpenseCategory
from app.models.goal import Goal


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _create_goal(client, name="Test Goal", goal_type="savings",
                 target_amount="10000", current_amount="0",
                 monthly_contribution="0", target_date=""):
    return client.post(
        "/goals/add",
        data={
            "name": name,
            "goal_type": goal_type,
            "target_amount": target_amount,
            "current_amount": current_amount,
            "monthly_contribution": monthly_contribution,
            "target_date": target_date,
        },
        follow_redirects=True,
    )


def _get_goal(name):
    return Goal.query.filter_by(name=name).first()


def _goals_data(client):
    return json.loads(client.get("/goals/data").data)


# ─── GOAL-001: Create valid goal ─────────────────────────────────────────────

@pytest.mark.tc_id("GOAL-001")
def test_goal_001_create_valid_goal(auth_client, app):
    resp = _create_goal(auth_client, name="GOAL001-fund", target_amount="200000",
                        goal_type="emergency", monthly_contribution="5000")
    assert resp.status_code == 200

    goal = _get_goal("GOAL001-fund")
    assert goal is not None, "Goal should be saved to DB"
    assert float(goal.target_amount) == 200000.0
    assert goal.goal_type == "emergency"
    assert float(goal.monthly_contribution) == 5000.0
    assert goal.status == "active"


# ─── GOAL-002: Zero target amount → validation error ─────────────────────────

@pytest.mark.tc_id("GOAL-002")
def test_goal_002_zero_target(auth_client, app):
    count_before = Goal.query.count()
    resp = _create_goal(auth_client, name="GOAL002-zero", target_amount="0")
    assert resp.status_code == 200
    assert b"Goal name and target amount are required" in resp.data
    assert Goal.query.count() == count_before, "No goal should be created"


# ─── GOAL-003: Initial amount > 0 → expense auto-logged ──────────────────────

@pytest.mark.tc_id("GOAL-003")
def test_goal_003_initial_amount_logs_expense(auth_client, app):
    _create_goal(auth_client, name="GOAL003-init", target_amount="50000",
                 current_amount="10000")

    goal = _get_goal("GOAL003-init")
    assert goal is not None
    assert float(goal.current_amount) == 10000.0

    # An Expense should have been auto-logged under Goals category
    expense = Expense.query.filter(
        Expense.note.contains("GOAL003-init")
    ).first()
    assert expense is not None, "Initial amount should auto-log a Goals expense"
    assert float(expense.amount) == 10000.0

    # Goals category must exist
    goals_cat = ExpenseCategory.query.filter_by(name="Goals").first()
    assert goals_cat is not None
    assert expense.category_id == goals_cat.id


# ─── GOAL-004: Auto-complete when contribution reaches target ─────────────────

@pytest.mark.tc_id("GOAL-004")
def test_goal_004_auto_completion(auth_client, app):
    _create_goal(auth_client, name="GOAL004-complete", target_amount="1000",
                 current_amount="0")
    goal = _get_goal("GOAL004-complete")

    # Contribute exactly the target amount
    resp = auth_client.post(
        f"/goals/{goal.id}/contribute",
        data={"amount": "1000"},
        follow_redirects=True,
    )
    assert resp.status_code == 200

    db.session.refresh(goal)
    assert goal.status == "completed", "Goal should be auto-completed when target reached"
    assert float(goal.current_amount) == 1000.0


# ─── GOAL-005: Add valid contribution ────────────────────────────────────────

@pytest.mark.tc_id("GOAL-005")
def test_goal_005_add_valid_contribution(auth_client, app):
    _create_goal(auth_client, name="GOAL005-contrib", target_amount="5000")
    goal = _get_goal("GOAL005-contrib")

    auth_client.post(
        f"/goals/{goal.id}/contribute",
        data={"amount": "750"},
        follow_redirects=True,
    )

    db.session.refresh(goal)
    assert float(goal.current_amount) == 750.0, "current_amount should increase by contribution"


# ─── GOAL-006: Zero contribution → validation error ──────────────────────────

@pytest.mark.tc_id("GOAL-006")
def test_goal_006_zero_contribution(auth_client, app):
    _create_goal(auth_client, name="GOAL006-zero", target_amount="5000")
    goal = _get_goal("GOAL006-zero")

    resp = auth_client.post(
        f"/goals/{goal.id}/contribute",
        data={"amount": "0"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Enter a valid amount" in resp.data

    db.session.refresh(goal)
    assert float(goal.current_amount) == 0.0, "Amount should not change on zero contribution"


# ─── GOAL-007: Negative contribution → validation error ──────────────────────

@pytest.mark.tc_id("GOAL-007")
def test_goal_007_negative_contribution(auth_client, app):
    _create_goal(auth_client, name="GOAL007-neg", target_amount="5000")
    goal = _get_goal("GOAL007-neg")

    resp = auth_client.post(
        f"/goals/{goal.id}/contribute",
        data={"amount": "-500"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Enter a valid amount" in resp.data

    db.session.refresh(goal)
    assert float(goal.current_amount) == 0.0, "Amount should not change on negative contribution"


# ─── GOAL-008: Edit goal details ─────────────────────────────────────────────

@pytest.mark.tc_id("GOAL-008")
def test_goal_008_edit_goal_details(auth_client, app):
    _create_goal(auth_client, name="GOAL008-before", target_amount="10000")
    goal = _get_goal("GOAL008-before")

    resp = auth_client.post(
        f"/goals/{goal.id}/edit",
        data={
            "name": "GOAL008-after",
            "goal_type": "vacation",
            "target_amount": "15000",
            "current_amount": str(float(goal.current_amount)),
            "monthly_contribution": "2000",
            "status": "active",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    db.session.refresh(goal)
    assert goal.name == "GOAL008-after"
    assert float(goal.target_amount) == 15000.0
    assert goal.goal_type == "vacation"
    assert float(goal.monthly_contribution) == 2000.0


# ─── GOAL-009: Edit with add_contribution → expense auto-logged ──────────────

@pytest.mark.tc_id("GOAL-009")
def test_goal_009_edit_add_contribution_logs_expense(auth_client, app):
    _create_goal(auth_client, name="GOAL009-editcontrib", target_amount="20000")
    goal = _get_goal("GOAL009-editcontrib")
    initial_amount = float(goal.current_amount)
    expense_count_before = Expense.query.count()

    auth_client.post(
        f"/goals/{goal.id}/edit",
        data={
            "name": goal.name,
            "goal_type": goal.goal_type,
            "target_amount": str(float(goal.target_amount)),
            "current_amount": str(float(goal.current_amount)),
            "monthly_contribution": "1000",
            "status": "active",
            "add_contribution": "3000",
        },
        follow_redirects=True,
    )

    db.session.refresh(goal)
    assert float(goal.current_amount) == initial_amount + 3000.0, \
        "current_amount should increase by add_contribution"
    assert Expense.query.count() == expense_count_before + 1, \
        "One new Goals expense should be logged"

    expense = Expense.query.filter(
        Expense.note.contains("GOAL009-editcontrib")
    ).first()
    assert expense is not None
    assert float(expense.amount) == 3000.0


# ─── GOAL-010: Delete goal ────────────────────────────────────────────────────

@pytest.mark.tc_id("GOAL-010")
def test_goal_010_delete_goal(auth_client, app):
    _create_goal(auth_client, name="GOAL010-delete", target_amount="5000")
    goal = _get_goal("GOAL010-delete")
    goal_id = goal.id

    resp = auth_client.post(
        f"/goals/{goal_id}/delete",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert db.session.get(Goal, goal_id) is None, "Goal should be deleted from DB"


# ─── GOAL-011: Progress percentage calculation ────────────────────────────────

@pytest.mark.tc_id("GOAL-011")
def test_goal_011_progress_percentage(auth_client, app):
    _create_goal(auth_client, name="GOAL011-pct", target_amount="1000")
    goal = _get_goal("GOAL011-pct")

    auth_client.post(
        f"/goals/{goal.id}/contribute",
        data={"amount": "250"},
        follow_redirects=True,
    )

    db.session.refresh(goal)
    assert goal.progress_percent == 25.0, "progress_percent should be 25% after 250/1000"

    # Also verify via JSON API
    data = _goals_data(auth_client)
    match = next((g for g in data if g["name"] == "GOAL011-pct"), None)
    assert match is not None
    assert match["progress_percent"] == 25.0


# ─── GOAL-012: ETA (months_to_goal) calculation ───────────────────────────────

@pytest.mark.tc_id("GOAL-012")
def test_goal_012_eta_calculation(auth_client, app):
    _create_goal(
        auth_client,
        name="GOAL012-eta",
        target_amount="12000",
        monthly_contribution="1000",
    )
    goal = _get_goal("GOAL012-eta")
    assert goal.months_to_goal == 12, "months_to_goal should be 12 for 12000 / 1000"

    # Verify serialised in API
    data = _goals_data(auth_client)
    match = next((g for g in data if g["name"] == "GOAL012-eta"), None)
    assert match["months_to_goal"] == 12


# ─── GOAL-013: Zero monthly contribution → ETA is None ───────────────────────

@pytest.mark.tc_id("GOAL-013")
def test_goal_013_zero_contribution_no_eta(auth_client, app):
    _create_goal(
        auth_client,
        name="GOAL013-noeta",
        target_amount="12000",
        monthly_contribution="0",
    )
    goal = _get_goal("GOAL013-noeta")
    assert goal.months_to_goal is None, "months_to_goal should be None when contribution is 0"

    data = _goals_data(auth_client)
    match = next((g for g in data if g["name"] == "GOAL013-noeta"), None)
    assert match["months_to_goal"] is None


# ─── GOAL-014: Goals expense category auto-created ───────────────────────────

@pytest.mark.tc_id("GOAL-014")
def test_goal_014_goals_category_auto_created(auth_client, app):
    # Fresh DB — Goals category should not exist yet (not in seed_defaults)
    assert ExpenseCategory.query.filter_by(name="Goals").first() is None, \
        "Goals category should not exist before first contribution"

    _create_goal(auth_client, name="GOAL014-cat", target_amount="5000",
                 current_amount="1000")  # triggers _log_goal_expense

    goals_cat = ExpenseCategory.query.filter_by(name="Goals").first()
    assert goals_cat is not None, "Goals category should be created on first contribution"
    assert goals_cat.color == "#A78BFA"
    assert goals_cat.icon == "target"


# ─── GOAL-015: Goal row appears in analytics breakdown ───────────────────────

@pytest.mark.tc_id("GOAL-015")
def test_goal_015_goal_in_analytics_breakdown(auth_client, app):
    # Create a goal with no contributions this month
    _create_goal(auth_client, name="GOAL015-analytics", target_amount="30000")

    resp = auth_client.get("/analytics/")
    assert resp.status_code == 200
    # The analytics page should render a Goals category row
    assert b"Goals" in resp.data, "Analytics breakdown should include Goals row"


# ─── GOAL-016: Goals JSON API ─────────────────────────────────────────────────

@pytest.mark.tc_id("GOAL-016")
def test_goal_016_json_api(auth_client, app):
    _create_goal(auth_client, name="GOAL016-api", target_amount="8000",
                 monthly_contribution="500", goal_type="investment")

    resp = auth_client.get("/goals/data")
    assert resp.status_code == 200
    assert "application/json" in resp.content_type

    data = json.loads(resp.data)
    assert isinstance(data, list), "Response should be a JSON array"

    match = next((g for g in data if g["name"] == "GOAL016-api"), None)
    assert match is not None, "Created goal should appear in API response"

    # Verify all required fields are present
    required_fields = [
        "id", "name", "goal_type", "target_amount", "current_amount",
        "monthly_contribution", "progress_percent", "amount_remaining",
        "months_to_goal", "status",
    ]
    for field in required_fields:
        assert field in match, f"Missing field '{field}' in goal dict"

    assert match["goal_type"] == "investment"
    assert match["target_amount"] == 8000.0
    assert match["monthly_contribution"] == 500.0
    assert match["status"] == "active"
