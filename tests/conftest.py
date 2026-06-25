"""
Pytest configuration, fixtures, and automatic test-log writer.
After every run, results for EXP-* tests are written to logs/expenses_test_log.md
which doubles as the Obsidian note for the test run.
"""

import os
from datetime import datetime

import pytest
from sqlalchemy.pool import StaticPool

from app import create_app, db
from app.models.expense import Expense, ExpenseCategory
from app.models.settings import UserSettings
from app.models.user import User

# ─── Test case descriptions (used in the log) ────────────────────────────────

TC_DESCRIPTIONS = {
    # Expenses
    "EXP-001": "Add valid expense",
    "EXP-002": "Add expense with zero amount",
    "EXP-003": "Add expense with negative amount",
    "EXP-004": "Add expense without category",
    "EXP-005": "Add expense without note",
    "EXP-006": "Edit existing expense",
    "EXP-007": "Delete expense",
    "EXP-008": "Expense appears in dashboard",
    "EXP-009": "Expense filter — 3 months",
    "EXP-010": "Expense filter — 6 months",
    "EXP-011": "Expense filter — 1 year",
    "EXP-012": "Custom date range filter",
    "EXP-013": "Future date expense",
    "EXP-014": "Expense JSON API",
    "EXP-015": "Edit non-existing expense (404)",
    "EXP-016": "Missing CSRF token returns 400",
    # Authentication
    "AUTH-001": "Register with valid details — account created",
    "AUTH-002": "Register with existing email — error shown",
    "AUTH-003": "Register with short password (< 6 chars) — validation error",
    "AUTH-004": "Password mismatch on register — validation error",
    "AUTH-005": "Login with valid credentials — success",
    "AUTH-006": "Login with invalid password — error shown",
    "AUTH-007": "Logout — session cleared and redirected",
    "AUTH-008": "Remember me login — persistent cookie set",
    "AUTH-009": "Access dashboard without login — redirect to login",
    "AUTH-010": "Missing CSRF token on login form — 400 error",
    # Edge Cases
    "EDGE-001": "Extremely large expense amount (₹99,999,999)",
    "EDGE-002": "Decimal amount precision (₹1234.56)",
    "EDGE-003": "No expenses this month — dashboard handles gracefully",
    "EDGE-004": "All goals completed — analytics updates correctly",
    "EDGE-005": "Deleted Goals category — recreated on next contribution",
    "EDGE-006": "Fixed costs exceed budget — dashboard still calculates",
    "EDGE-007": "Brand new user with no data — analytics empty state",
    "EDGE-008": "Custom date filter with from > to — graceful handling",
    "EDGE-009": "Leap year date expense (Feb 29) saved correctly",
    "EDGE-010": "Unicode/emoji note stored and displayed correctly",
    # API Validation
    "API-001": "/expenses/data returns current user's data only",
    "API-002": "/goals/data proper field serialization",
    "API-003": "/analytics/spending-savings correct JSON schema",
    "API-004": "Invalid range query — graceful fallback to 6m",
    "API-005": "Unauthenticated API access redirects to login",
    "API-006": "Empty dataset returns valid empty JSON arrays",
    "API-007": "Date formatting matches spec (YYYY-MM-DD / DD Mon YYYY)",
    "API-008": "User currency reflected in analytics summary",
    # Security & Validation
    "SEC-001": "Unauthenticated access redirects to login",
    "SEC-002": "Cross-user expense edit returns 404",
    "SEC-003": "Cross-user goal delete returns 404",
    "SEC-004": "Missing CSRF token returns 400",
    "SEC-005": "SQL injection in login email blocked",
    "SEC-006": "XSS in note field is escaped on render",
    "SEC-007": "Invalid category ID — validation failure",
    "SEC-008": "Expired session redirects to login",
    "SEC-009": "Invalid route returns 404",
    # Settings
    "SET-001": "Update profile settings (name, currency)",
    "SET-002": "Update monthly budget",
    "SET-003": "Toggle AI alerts on/off",
    "SET-004": "Toggle notifications on/off",
    "SET-005": "Add monthly recurring expense",
    "SET-006": "Add yearly recurring expense — monthly equiv = amount / 12",
    "SET-007": "Add weekly recurring expense — monthly equiv = amount × 4.33",
    "SET-008": "Delete recurring expense",
    "SET-009": "Tab persistence — redirect to correct tab after submit",
    "SET-010": "Settings row auto-created for user with no settings",
    # Analytics
    "ANA-001": "Analytics page loads correctly",
    "ANA-002": "Spending vs savings JSON — correct schema",
    "ANA-003": "7-day range — 7 daily labels",
    "ANA-004": "30-day range — 30 daily labels",
    "ANA-005": "6-month range — 6 monthly labels",
    "ANA-006": "1-year range — 12 monthly labels",
    "ANA-007": "Negative savings when spending > budget",
    "ANA-008": "Category percentages sum to 100",
    "ANA-009": "Fixed cost monthly equivalents (yearly/weekly/monthly)",
    "ANA-010": "AI insights endpoint returns JSON array",
    "ANA-011": "Empty state — no expenses, no crash",
    "ANA-012": "Goal analytics totals calculated correctly",
    # Dashboard
    "DASH-001": "Dashboard loads correctly",
    "DASH-002": "Zero budget — no crash, percentage = 0",
    "DASH-003": "Money score updates with expenses and goals",
    "DASH-004": "Recent expenses — only latest 5 shown",
    "DASH-005": "Budget allocation percentages correct",
    "DASH-006": "Remaining budget = budget minus total spent",
    "DASH-007": "Negative remaining budget displayed correctly",
    # Goals
    "GOAL-001": "Create valid goal",
    "GOAL-002": "Create goal with zero target amount",
    "GOAL-003": "Create goal with initial amount — expense auto-logged",
    "GOAL-004": "Goal auto-completes when target reached",
    "GOAL-005": "Add valid contribution",
    "GOAL-006": "Add zero contribution",
    "GOAL-007": "Add negative contribution",
    "GOAL-008": "Edit goal details",
    "GOAL-009": "Edit with add_contribution — expense auto-logged",
    "GOAL-010": "Delete goal",
    "GOAL-011": "Goal progress percentage calculation",
    "GOAL-012": "Goal ETA (months_to_goal) calculation",
    "GOAL-013": "Zero monthly contribution — ETA is None",
    "GOAL-014": "Goals expense category auto-created on first contribution",
    "GOAL-015": "Goal row appears in analytics category breakdown",
    "GOAL-016": "Goals JSON API",
}

# ─── Log writer hooks ─────────────────────────────────────────────────────────

_results: list[dict] = []


def pytest_configure(config):
    config.addinivalue_line("markers", "tc_id(id): test case ID for log")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when != "call":
        return
    marker = item.get_closest_marker("tc_id")
    tc_id = marker.args[0] if marker else item.name
    if rep.passed:
        status = "PASS"
        error = ""
    elif rep.failed:
        status = "FAIL"
        lines = str(rep.longrepr).strip().splitlines()
        error = lines[-1][:120].replace("|", "\\|") if lines else ""
    else:
        status = "SKIP"
        error = ""
    _results.append(
        {
            "tc_id": tc_id,
            "description": TC_DESCRIPTIONS.get(tc_id, item.name),
            "status": status,
            "error": error,
        }
    )


def _write_log(prefix: str, title: str, run_cmd: str, log_filename: str) -> None:
    module_results = [r for r in _results if r["tc_id"].startswith(prefix)]
    if not module_results:
        return

    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_filename)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    passed  = sum(1 for r in module_results if r["status"] == "PASS")
    failed  = sum(1 for r in module_results if r["status"] == "FAIL")
    skipped = sum(1 for r in module_results if r["status"] == "SKIP")

    lines = [
        f"# {title} — Test Run Log\n",
        f"**Last run:** {now}  ",
        f"**Result:** {passed} passed · {failed} failed · {skipped} skipped · {len(module_results)} total\n",
        "---\n",
        "| TC ID | Scenario | Status | Notes |",
        "| --- | --- | --- | --- |",
    ]
    for r in module_results:
        if r["status"] == "PASS":
            badge = "PASS"
        elif r["status"] == "FAIL":
            badge = "FAIL"
        else:
            badge = "SKIP"
        lines.append(f"| {r['tc_id']} | {r['description']} | {badge} | {r['error']} |")

    lines += [
        "\n---",
        f"\n_Auto-generated by pytest · {now}_",
        f"_Run:_ `{run_cmd}`",
    ]

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n[LOG] {log_filename}  ({passed} passed, {failed} failed)")


def pytest_sessionfinish(session, exitstatus):
    _write_log("EXP",  "Expense Module",         "pytest tests/test_expenses.py -v",  "expenses_test_log.md")
    _write_log("GOAL", "Goal Management Module",  "pytest tests/test_goals.py -v",     "goals_test_log.md")
    _write_log("DASH", "Dashboard Module",        "pytest tests/test_dashboard.py -v",  "dashboard_test_log.md")
    _write_log("ANA",  "Analytics Module",        "pytest tests/test_analytics.py -v",  "analytics_test_log.md")
    _write_log("SET",  "Settings Module",         "pytest tests/test_settings.py -v",    "settings_test_log.md")
    _write_log("SEC",  "Security & Validation",   "pytest tests/test_security.py -v",    "security_test_log.md")
    _write_log("API",  "API Validation",          "pytest tests/test_api.py -v",          "api_test_log.md")
    _write_log("EDGE", "Edge Cases",              "pytest tests/test_edge_cases.py -v",   "edge_cases_test_log.md")
    _write_log("AUTH", "Authentication",          "pytest tests/test_auth.py -v",         "auth_test_log.md")


# ─── Shared test config ───────────────────────────────────────────────────────

_BASE_CONFIG = {
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SQLALCHEMY_ENGINE_OPTIONS": {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    },
    "SECRET_KEY": "test-secret-key-budget-buddy",
    "WTF_CSRF_ENABLED": False,
    "SERVER_NAME": None,
}


# ─── Standard fixtures (CSRF disabled — used by all EXP tests except 016) ────

@pytest.fixture
def app():
    """Fresh in-memory Flask app per test."""
    application = create_app("default")
    application.config.update(_BASE_CONFIG)
    with application.app_context():
        db.create_all()
        ExpenseCategory.seed_defaults()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client, app):
    """Logged-in test client with a fresh user."""
    user = User(full_name="Expense Tester", email="exp@test.com")
    user.set_password("testpass123")
    db.session.add(user)
    db.session.flush()
    db.session.add(
        UserSettings(
            user_id=user.id,
            monthly_budget=80000,
            monthly_saving_goal=10000,
            monthly_investing_goal=5000,
        )
    )
    db.session.commit()
    client.post(
        "/auth/login",
        data={"email": "exp@test.com", "password": "testpass123"},
    )
    return client


@pytest.fixture
def food_cat_id(app):
    """Integer ID of the seeded Food category."""
    return ExpenseCategory.query.filter_by(name="Food").first().id


# ─── CSRF-enabled fixtures (used only for EXP-016) ────────────────────────────

@pytest.fixture
def csrf_app():
    """Separate app instance with CSRF protection ON."""
    cfg = {**_BASE_CONFIG, "WTF_CSRF_ENABLED": True, "SECRET_KEY": "csrf-test-key"}
    application = create_app("default")
    application.config.update(cfg)
    with application.app_context():
        db.create_all()
        ExpenseCategory.seed_defaults()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def csrf_auth_client(csrf_app):
    """Authenticated client for the CSRF app — login injected via session."""
    with csrf_app.app_context():
        user = User(full_name="CSRF User", email="csrf@test.com")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.flush()
        db.session.add(UserSettings(user_id=user.id, monthly_budget=50000))
        db.session.commit()
        user_id = user.id

    client = csrf_app.test_client()
    # Inject Flask-Login session directly to avoid CSRF on the login POST itself
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
    return client
