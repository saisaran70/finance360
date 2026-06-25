"""
Expense module test suite — EXP-001 through EXP-016
Run:  pytest tests/test_expenses.py -v
Results are auto-written to logs/expenses_test_log.md after the run.
"""

import json
from datetime import date, timedelta

import pytest

from app import db
from app.models.expense import Expense, ExpenseCategory


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _add_expense(client, cat_id, amount="500", note="test", expense_date="2026-05-10"):
    return client.post(
        "/expenses/add",
        data={
            "amount": amount,
            "category_id": str(cat_id),
            "note": note,
            "expense_date": expense_date,
        },
        follow_redirects=True,
    )


def _expense_count(app):
    return Expense.query.count()


# ─── EXP-001: Add valid expense ───────────────────────────────────────────────

@pytest.mark.tc_id("EXP-001")
def test_exp_001_add_valid_expense(auth_client, app, food_cat_id):
    resp = _add_expense(auth_client, food_cat_id, amount="750.50", note="EXP001-coffee")
    assert resp.status_code == 200
    expense = Expense.query.filter_by(note="EXP001-coffee").first()
    assert expense is not None, "Expense should be saved to DB"
    assert float(expense.amount) == 750.50
    assert expense.expense_date == date(2026, 5, 10)


# ─── EXP-002: Zero amount → validation error ──────────────────────────────────

@pytest.mark.tc_id("EXP-002")
def test_exp_002_zero_amount(auth_client, app, food_cat_id):
    count_before = _expense_count(app)
    resp = _add_expense(auth_client, food_cat_id, amount="0", note="EXP002")
    assert resp.status_code == 200
    assert b"Amount must be greater than zero" in resp.data
    assert _expense_count(app) == count_before, "No expense should be created"


# ─── EXP-003: Negative amount → validation error ─────────────────────────────

@pytest.mark.tc_id("EXP-003")
def test_exp_003_negative_amount(auth_client, app, food_cat_id):
    count_before = _expense_count(app)
    resp = _add_expense(auth_client, food_cat_id, amount="-200", note="EXP003")
    assert resp.status_code == 200
    assert b"Amount must be greater than zero" in resp.data
    assert _expense_count(app) == count_before, "No expense should be created"


# ─── EXP-004: No category → validation error ─────────────────────────────────
# xfail: route uses `int(form.get('category_id', 0))` — SQLite doesn't enforce
# FK constraints by default so the expense saves with category_id=0.
# Fix: add explicit validation for category_id > 0 in the add() route.

@pytest.mark.tc_id("EXP-004")
@pytest.mark.xfail(reason="category_id not validated — expense saves with id=0 on SQLite", strict=True)
def test_exp_004_add_without_category(auth_client, app):
    count_before = _expense_count(app)
    resp = auth_client.post(
        "/expenses/add",
        data={"amount": "500", "expense_date": "2026-05-10"},  # no category_id
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert _expense_count(app) == count_before, (
        "Expense saved without a valid category — category_id validation is missing"
    )


# ─── EXP-005: Note is optional ────────────────────────────────────────────────

@pytest.mark.tc_id("EXP-005")
def test_exp_005_add_without_note(auth_client, app, food_cat_id):
    resp = auth_client.post(
        "/expenses/add",
        data={"amount": "300", "category_id": str(food_cat_id), "expense_date": "2026-05-10"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    saved = Expense.query.filter_by(amount=300).first()
    assert saved is not None, "Expense without note should still be saved"
    assert saved.note in (None, "")


# ─── EXP-006: Edit existing expense ──────────────────────────────────────────

@pytest.mark.tc_id("EXP-006")
def test_exp_006_edit_expense(auth_client, app, food_cat_id):
    _add_expense(auth_client, food_cat_id, amount="400", note="EXP006-before")
    expense = Expense.query.filter_by(note="EXP006-before").first()
    assert expense is not None

    resp = auth_client.post(
        f"/expenses/{expense.id}/edit",
        data={
            "amount": "600",
            "category_id": str(food_cat_id),
            "note": "EXP006-after",
            "expense_date": "2026-05-12",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    db.session.refresh(expense)
    assert float(expense.amount) == 600.0
    assert expense.note == "EXP006-after"
    assert expense.expense_date == date(2026, 5, 12)


# ─── EXP-007: Delete expense ─────────────────────────────────────────────────

@pytest.mark.tc_id("EXP-007")
def test_exp_007_delete_expense(auth_client, app, food_cat_id):
    _add_expense(auth_client, food_cat_id, amount="250", note="EXP007-delete")
    expense = Expense.query.filter_by(note="EXP007-delete").first()
    assert expense is not None

    resp = auth_client.post(
        f"/expenses/{expense.id}/delete",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert db.session.get(Expense, expense.id) is None, "Expense should be deleted"


# ─── EXP-008: Expense totals update on dashboard ─────────────────────────────

@pytest.mark.tc_id("EXP-008")
def test_exp_008_expense_appears_in_dashboard(auth_client, app, food_cat_id):
    today = date.today().strftime("%Y-%m-%d")
    _add_expense(auth_client, food_cat_id, amount="1500", note="EXP008-dash", expense_date=today)

    resp = auth_client.get("/", follow_redirects=True)
    assert resp.status_code == 200
    # Dashboard renders total_spent; 1500 should appear somewhere in the page
    assert b"1,500" in resp.data or b"1500" in resp.data


# ─── EXP-009: 3-month filter ─────────────────────────────────────────────────

@pytest.mark.tc_id("EXP-009")
def test_exp_009_filter_3m(auth_client, app, food_cat_id):
    _add_expense(auth_client, food_cat_id, amount="100", note="EXP009-recent", expense_date="2026-05-01")
    # Expense well outside 3m window (4 years ago) should not appear
    _add_expense(auth_client, food_cat_id, amount="200", note="EXP009-old", expense_date="2022-01-01")

    resp = auth_client.get("/expenses/?period=3m")
    assert resp.status_code == 200
    assert b"EXP009-recent" in resp.data
    assert b"EXP009-old" not in resp.data


# ─── EXP-010: 6-month filter ─────────────────────────────────────────────────

@pytest.mark.tc_id("EXP-010")
def test_exp_010_filter_6m(auth_client, app, food_cat_id):
    _add_expense(auth_client, food_cat_id, amount="100", note="EXP010-recent", expense_date="2026-04-01")
    _add_expense(auth_client, food_cat_id, amount="200", note="EXP010-old", expense_date="2022-01-01")

    resp = auth_client.get("/expenses/?period=6m")
    assert resp.status_code == 200
    assert b"EXP010-recent" in resp.data
    assert b"EXP010-old" not in resp.data


# ─── EXP-011: 1-year filter ──────────────────────────────────────────────────

@pytest.mark.tc_id("EXP-011")
def test_exp_011_filter_1y(auth_client, app, food_cat_id):
    _add_expense(auth_client, food_cat_id, amount="100", note="EXP011-recent", expense_date="2026-01-01")
    _add_expense(auth_client, food_cat_id, amount="200", note="EXP011-old", expense_date="2020-01-01")

    resp = auth_client.get("/expenses/?period=1y")
    assert resp.status_code == 200
    assert b"EXP011-recent" in resp.data
    assert b"EXP011-old" not in resp.data


# ─── EXP-012: Custom date range filter ───────────────────────────────────────

@pytest.mark.tc_id("EXP-012")
def test_exp_012_custom_date_filter(auth_client, app, food_cat_id):
    _add_expense(auth_client, food_cat_id, amount="111", note="EXP012-jan", expense_date="2026-01-15")
    _add_expense(auth_client, food_cat_id, amount="222", note="EXP012-apr", expense_date="2026-04-20")

    resp = auth_client.get("/expenses/?period=custom&from=2026-01-01&to=2026-01-31")
    assert resp.status_code == 200
    assert b"EXP012-jan" in resp.data
    assert b"EXP012-apr" not in resp.data


# ─── EXP-013: Future date expense ────────────────────────────────────────────

@pytest.mark.tc_id("EXP-013")
def test_exp_013_future_date_expense(auth_client, app, food_cat_id):
    future = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
    _add_expense(auth_client, food_cat_id, amount="999", note="EXP013-future", expense_date=future)

    saved = Expense.query.filter_by(note="EXP013-future").first()
    assert saved is not None, "Future-dated expense should be saved"
    assert saved.expense_date > date.today()


# ─── EXP-014: JSON API returns valid list ─────────────────────────────────────

@pytest.mark.tc_id("EXP-014")
def test_exp_014_json_api(auth_client, app, food_cat_id):
    _add_expense(auth_client, food_cat_id, amount="350", note="EXP014-api")

    resp = auth_client.get("/expenses/data")
    assert resp.status_code == 200
    assert "application/json" in resp.content_type

    data = json.loads(resp.data)
    assert isinstance(data, list), "Response should be a JSON array"
    notes = [e["note"] for e in data]
    assert "EXP014-api" in notes

    # Verify required fields in each record
    for item in data:
        for field in ("id", "amount", "category", "date"):
            assert field in item, f"Missing field '{field}' in expense dict"


# ─── EXP-015: Edit non-existing expense → 404 ────────────────────────────────

@pytest.mark.tc_id("EXP-015")
def test_exp_015_edit_invalid_id(auth_client, app, food_cat_id):
    resp = auth_client.post(
        "/expenses/999999/edit",
        data={
            "amount": "100",
            "category_id": str(food_cat_id),
            "expense_date": "2026-05-10",
        },
    )
    assert resp.status_code == 404, "Non-existing expense edit should return 404"


# ─── EXP-016: Missing CSRF token → 400 ────────────────────────────────────────

@pytest.mark.tc_id("EXP-016")
def test_exp_016_missing_csrf(csrf_auth_client, csrf_app):
    with csrf_app.app_context():
        cat_id = ExpenseCategory.query.filter_by(name="Food").first().id

    resp = csrf_auth_client.post(
        "/expenses/add",
        data={
            "amount": "100",
            "category_id": str(cat_id),
            "expense_date": "2026-05-10",
        },
        # No csrf_token field → Flask-WTF CSRFProtect should reject with 400
    )
    assert resp.status_code == 400, "POST without CSRF token should return 400"
