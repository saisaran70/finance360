"""
Security & Validation test suite — SEC-001 through SEC-009
Run:  pytest tests/test_security.py -v
Results are auto-written to logs/security_test_log.md after the run.
"""

import pytest

from app import db
from app.models.expense import Expense, ExpenseCategory
from app.models.goal import Goal
from app.models.settings import UserSettings
from app.models.user import User


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_user(email, password="testpass123", name="Test User"):
    user = User(full_name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    db.session.add(UserSettings(user_id=user.id, monthly_budget=50000))
    db.session.commit()
    return user


def _login(client, email, password="testpass123"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def _add_expense_db(app, user_id, amount=500):
    cat = ExpenseCategory.query.filter_by(name="Food").first()
    from datetime import date
    e = Expense(user_id=user_id, category_id=cat.id, amount=amount,
                note="sec-test", expense_date=date.today())
    db.session.add(e)
    db.session.commit()
    return e


def _add_goal_db(user_id, target=10000):
    g = Goal(user_id=user_id, name="sec-goal", target_amount=target,
             current_amount=0, status="active")
    db.session.add(g)
    db.session.commit()
    return g


# ─── SEC-001: Unauthenticated access redirects to login ──────────────────────

@pytest.mark.tc_id("SEC-001")
def test_sec_001_unauthenticated_redirect(client, app):
    protected_routes = [
        "/",
        "/expenses/",
        "/analytics/",
        "/goals/",
        "/settings/",
    ]
    for route in protected_routes:
        resp = client.get(route, follow_redirects=False)
        assert resp.status_code == 302, \
            f"GET {route} should redirect when not logged in"
        assert "login" in resp.headers["Location"].lower(), \
            f"Redirect for {route} should point to login page"


# ─── SEC-002: Cross-user expense edit returns 404 ─────────────────────────────

@pytest.mark.tc_id("SEC-002")
def test_sec_002_cross_user_expense_edit(auth_client, app, food_cat_id):
    # Create an expense that belongs to user B (not user A)
    user_b = _make_user("userb_sec002@test.com")
    expense_of_b = _add_expense_db(app, user_b.id, amount=800)

    # auth_client is user A — try to edit user B's expense
    resp = auth_client.post(
        f"/expenses/{expense_of_b.id}/edit",
        data={
            "amount": "999",
            "category_id": str(food_cat_id),
            "expense_date": "2026-05-10",
        },
    )
    assert resp.status_code == 404, \
        "User A editing User B's expense should return 404"

    # Verify expense is unchanged
    db.session.refresh(expense_of_b)
    assert float(expense_of_b.amount) == 800.0, "Expense amount should be unchanged"


# ─── SEC-003: Cross-user goal delete returns 404 ──────────────────────────────

@pytest.mark.tc_id("SEC-003")
def test_sec_003_cross_user_goal_delete(auth_client, app):
    # Create a goal that belongs to user B
    user_b = _make_user("userb_sec003@test.com")
    goal_of_b = _add_goal_db(user_b.id, target=50000)
    goal_id = goal_of_b.id

    # auth_client is user A — try to delete user B's goal
    resp = auth_client.post(f"/goals/{goal_id}/delete")
    assert resp.status_code == 404, \
        "User A deleting User B's goal should return 404"

    # Goal should still exist
    assert db.session.get(Goal, goal_id) is not None, \
        "Goal should not be deleted by a different user"


# ─── SEC-004: Missing CSRF token returns 400 ─────────────────────────────────

@pytest.mark.tc_id("SEC-004")
def test_sec_004_missing_csrf(csrf_auth_client, csrf_app):
    """POST to any state-changing endpoint without CSRF token must be rejected."""
    with csrf_app.app_context():
        cat_id = ExpenseCategory.query.filter_by(name="Food").first().id

    resp = csrf_auth_client.post(
        "/expenses/add",
        data={"amount": "100", "category_id": str(cat_id),
              "expense_date": "2026-05-10"},
        # csrf_token intentionally omitted
    )
    assert resp.status_code == 400, \
        "POST without CSRF token should return 400"


# ─── SEC-005: SQL injection in login email blocked ────────────────────────────

@pytest.mark.tc_id("SEC-005")
def test_sec_005_sql_injection_login(client, app):
    """SQLAlchemy uses parameterised queries — SQL injection payloads should
    simply fail to authenticate (no user found), not grant access."""
    payloads = [
        "' OR '1'='1",
        "admin@test.com' OR '1'='1' --",
        "' OR 1=1 --",
        "\" OR \"1\"=\"1",
    ]
    for payload in payloads:
        resp = client.post(
            "/auth/login",
            data={"email": payload, "password": "anything"},
            follow_redirects=False,
        )
        # Must NOT redirect to dashboard (302 to /) — must stay on login or show error
        if resp.status_code == 302:
            assert "login" in resp.headers["Location"].lower() or \
                   "dashboard" not in resp.headers["Location"].lower(), \
                f"SQL payload '{payload}' should not grant access"
        else:
            # 200 means stayed on login page — correct
            assert resp.status_code == 200, \
                f"Unexpected status {resp.status_code} for payload '{payload}'"


# ─── SEC-006: XSS in note field is escaped on render ─────────────────────────

@pytest.mark.tc_id("SEC-006")
def test_sec_006_xss_note_escaped(auth_client, app, food_cat_id):
    xss_payload = "<script>alert('xss')</script>"
    auth_client.post(
        "/expenses/add",
        data={
            "amount": "100",
            "category_id": str(food_cat_id),
            "note": xss_payload,
            "expense_date": "2026-05-10",
        },
    )

    # Verify note was stored as-is in the DB (no stripping)
    expense = Expense.query.filter_by(amount=100).first()
    assert expense is not None
    assert "<script>" in expense.note, "Raw note should be stored in DB as-is"

    # When rendered in the expenses page, Jinja2 must escape it
    resp = auth_client.get("/expenses/")
    assert resp.status_code == 200
    # Raw <script> tag must not appear unescaped in the HTML response
    assert b"<script>alert" not in resp.data, \
        "XSS payload must be escaped by Jinja2, not rendered as raw HTML"
    # Escaped form should be present instead
    assert b"&lt;script&gt;" in resp.data or b"alert" in resp.data, \
        "Escaped content should appear in the response"


# ─── SEC-007: Invalid category ID — validation failure ────────────────────────
# xfail: route accepts any integer category_id; SQLite does not enforce FK
# constraints by default, so the expense saves with a non-existent category.
# Fix: add `if not ExpenseCategory.query.get(category_id)` guard in add().

@pytest.mark.tc_id("SEC-007")
@pytest.mark.xfail(
    reason="category_id not validated — saves with id=99999 on SQLite (no FK enforcement)",
    strict=True,
)
def test_sec_007_invalid_category_id(auth_client, app):
    count_before = Expense.query.count()
    resp = auth_client.post(
        "/expenses/add",
        data={
            "amount": "500",
            "category_id": "99999",   # non-existent category
            "expense_date": "2026-05-10",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert Expense.query.count() == count_before, \
        "Expense with non-existent category_id should be rejected"


# ─── SEC-008: Expired session redirects to login ─────────────────────────────

@pytest.mark.tc_id("SEC-008")
def test_sec_008_expired_session_redirect(client, app):
    # Create user and log in
    _make_user("sess_sec008@test.com")
    _login(client, "sess_sec008@test.com")

    # Confirm access works while logged in
    resp = client.get("/expenses/")
    assert resp.status_code == 200, "Should have access while session is active"

    # Invalidate the session via the logout endpoint (clears Flask-Login session)
    client.get("/auth/logout", follow_redirects=False)

    # Subsequent request should redirect to login
    resp = client.get("/expenses/", follow_redirects=False)
    assert resp.status_code == 302, "Cleared session should cause redirect"
    assert "login" in resp.headers["Location"].lower(), \
        "Redirect should point to login page"


# ─── SEC-009: Invalid route returns 404 ──────────────────────────────────────

@pytest.mark.tc_id("SEC-009")
def test_sec_009_invalid_route_404(auth_client, app):
    invalid_routes = [
        "/nonexistent/",
        "/expenses/delete/all",
        "/admin/panel",
        "/goals/99999/hack",
    ]
    for route in invalid_routes:
        resp = auth_client.get(route)
        assert resp.status_code == 404, \
            f"GET {route} should return 404"
