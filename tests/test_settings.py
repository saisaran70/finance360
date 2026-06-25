"""
Settings module test suite — SET-001 through SET-010
Run:  pytest tests/test_settings.py -v
Results are auto-written to logs/settings_test_log.md after the run.
"""

import pytest

from app import db
from app.models.expense import ExpenseCategory
from app.models.recurring import RecurringExpense
from app.models.settings import UserSettings
from app.models.user import User
from app.services.analytics_service import get_fixed_cost_analysis


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _update_settings(client, **kwargs):
    """POST to /settings/update with sensible defaults for required fields."""
    defaults = {
        "full_name": "Expense Tester",
        "currency": "INR",
        "city": "",
        "monthly_budget": "80000",
        "monthly_saving_goal": "10000",
        "monthly_investing_goal": "5000",
    }
    defaults.update(kwargs)
    return client.post("/settings/update", data=defaults, follow_redirects=False)


def _add_fixed_cost(client, title, amount, billing_cycle, cat_id):
    return client.post(
        "/settings/fixed-costs/add",
        data={
            "title": title,
            "amount": str(amount),
            "category_id": str(cat_id),
            "billing_cycle": billing_cycle,
            "next_due_date": "",
        },
        follow_redirects=False,
    )


def _get_settings():
    return UserSettings.query.first()


def _get_user():
    return User.query.filter_by(email="exp@test.com").first()


def _food_cat_id_fresh(app):
    return ExpenseCategory.query.filter_by(name="Food").first().id


# ─── SET-001: Update profile name and currency ────────────────────────────────

@pytest.mark.tc_id("SET-001")
def test_set_001_update_profile(auth_client, app):
    resp = _update_settings(auth_client, full_name="Priya Sharma", currency="USD", city="Mumbai")
    # Route redirects to /settings/?tab=profile
    assert resp.status_code == 302

    user = _get_user()
    assert user.full_name == "Priya Sharma"
    assert user.currency == "USD"
    assert user.city == "Mumbai"


# ─── SET-002: Update monthly budget ──────────────────────────────────────────

@pytest.mark.tc_id("SET-002")
def test_set_002_update_monthly_budget(auth_client, app):
    resp = _update_settings(
        auth_client,
        monthly_budget="60000",
        monthly_saving_goal="8000",
        monthly_investing_goal="6000",
    )
    assert resp.status_code == 302

    s = _get_settings()
    assert float(s.monthly_budget) == 60000.0
    assert float(s.monthly_saving_goal) == 8000.0
    assert float(s.monthly_investing_goal) == 6000.0


# ─── SET-003: Toggle AI alerts ────────────────────────────────────────────────

@pytest.mark.tc_id("SET-003")
def test_set_003_toggle_ai_alerts(auth_client, app):
    # Enable
    _update_settings(auth_client, ai_alerts_enabled="on")
    assert _get_settings().ai_alerts_enabled is True

    # Disable (checkbox absent from form = off)
    _update_settings(auth_client)          # no ai_alerts_enabled key
    assert _get_settings().ai_alerts_enabled is False


# ─── SET-004: Toggle notifications ───────────────────────────────────────────

@pytest.mark.tc_id("SET-004")
def test_set_004_toggle_notifications(auth_client, app):
    # Enable
    _update_settings(auth_client, notifications_enabled="on")
    assert _get_settings().notifications_enabled is True

    # Disable
    _update_settings(auth_client)          # no notifications_enabled key
    assert _get_settings().notifications_enabled is False


# ─── SET-005: Add monthly recurring expense ───────────────────────────────────

@pytest.mark.tc_id("SET-005")
def test_set_005_add_monthly_fixed_cost(auth_client, app, food_cat_id):
    count_before = RecurringExpense.query.count()
    resp = _add_fixed_cost(auth_client, "House Rent", 15000, "monthly", food_cat_id)

    assert resp.status_code == 302
    assert RecurringExpense.query.count() == count_before + 1

    item = RecurringExpense.query.filter_by(title="House Rent").first()
    assert item is not None
    assert float(item.amount) == 15000.0
    assert item.billing_cycle == "monthly"
    assert item.user_id == _get_user().id


# ─── SET-006: Yearly billing — monthly_equiv = amount / 12 ───────────────────

@pytest.mark.tc_id("SET-006")
def test_set_006_yearly_billing_monthly_equiv(auth_client, app, food_cat_id):
    _add_fixed_cost(auth_client, "Annual Insurance", 12000, "yearly", food_cat_id)

    item = RecurringExpense.query.filter_by(title="Annual Insurance").first()
    assert item is not None
    assert item.billing_cycle == "yearly"

    user = _get_user()
    analysis = get_fixed_cost_analysis(user)
    entry = next((r for r in analysis if r["title"] == "Annual Insurance"), None)
    assert entry is not None
    assert entry["monthly_equiv"] == round(12000 / 12), \
        f"Expected {round(12000/12)}, got {entry['monthly_equiv']}"


# ─── SET-007: Weekly billing — monthly_equiv = amount × 4.33 ─────────────────

@pytest.mark.tc_id("SET-007")
def test_set_007_weekly_billing_monthly_equiv(auth_client, app, food_cat_id):
    _add_fixed_cost(auth_client, "Weekly Groceries", 2000, "weekly", food_cat_id)

    item = RecurringExpense.query.filter_by(title="Weekly Groceries").first()
    assert item is not None
    assert item.billing_cycle == "weekly"

    user = _get_user()
    analysis = get_fixed_cost_analysis(user)
    entry = next((r for r in analysis if r["title"] == "Weekly Groceries"), None)
    assert entry is not None
    assert entry["monthly_equiv"] == round(2000 * 4.33), \
        f"Expected {round(2000*4.33)}, got {entry['monthly_equiv']}"


# ─── SET-008: Delete recurring expense ───────────────────────────────────────

@pytest.mark.tc_id("SET-008")
def test_set_008_delete_fixed_cost(auth_client, app, food_cat_id):
    _add_fixed_cost(auth_client, "Netflix", 649, "monthly", food_cat_id)
    item = RecurringExpense.query.filter_by(title="Netflix").first()
    assert item is not None
    item_id = item.id

    resp = auth_client.post(
        f"/settings/fixed-costs/{item_id}/delete",
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert db.session.get(RecurringExpense, item_id) is None, \
        "Fixed cost should be deleted from DB"


# ─── SET-009: Tab persistence after form submission ───────────────────────────
# The route redirects to ?tab=fixed-costs after adding/deleting a fixed cost,
# and to ?tab=profile after updating profile settings.

@pytest.mark.tc_id("SET-009")
def test_set_009_tab_persistence(auth_client, app, food_cat_id):
    # After adding fixed cost → redirect should include ?tab=fixed-costs
    resp = _add_fixed_cost(auth_client, "Spotify", 119, "monthly", food_cat_id)
    assert resp.status_code == 302
    assert "tab=fixed-costs" in resp.headers["Location"], \
        "Adding fixed cost should redirect to fixed-costs tab"

    # After updating profile settings → redirect should include ?tab=profile
    resp2 = _update_settings(auth_client)
    assert resp2.status_code == 302
    assert "tab=profile" in resp2.headers["Location"], \
        "Updating profile should redirect to profile tab"

    # GET ?tab=fixed-costs should load the page (Fixed Costs content present)
    page = auth_client.get("/settings/?tab=fixed-costs", follow_redirects=True)
    assert page.status_code == 200
    assert b"tab-fixed-costs" in page.data
    assert b"Fixed Costs" in page.data


# ─── SET-010: Settings row auto-created for user with no settings ─────────────

@pytest.mark.tc_id("SET-010")
def test_set_010_settings_auto_create(app, client):
    # Create a user WITHOUT a settings row
    user = User(full_name="No Settings User", email="nosettings@test.com")
    user.set_password("testpass123")
    db.session.add(user)
    db.session.commit()
    user_id = user.id

    assert UserSettings.query.filter_by(user_id=user_id).first() is None, \
        "User should have no settings before first visit"

    # Log in as this user
    client.post("/auth/login", data={
        "email": "nosettings@test.com",
        "password": "testpass123",
    })

    # Visiting /settings/ should auto-create the settings row
    resp = client.get("/settings/", follow_redirects=True)
    assert resp.status_code == 200

    created = UserSettings.query.filter_by(user_id=user_id).first()
    assert created is not None, "Settings row should be auto-created on first /settings/ visit"
