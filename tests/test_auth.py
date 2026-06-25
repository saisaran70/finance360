"""
Authentication test suite — AUTH-001 through AUTH-010
Run:  pytest tests/test_auth.py -v
Results are auto-written to logs/auth_test_log.md after the run.
"""

import pytest

from app import db
from app.models.settings import UserSettings
from app.models.user import User


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _register(client, full_name="Test User", email="new@test.com",
              password="validpass", confirm=None, follow=True):
    return client.post("/auth/register", data={
        "full_name": full_name,
        "email": email,
        "password": password,
        "confirm_password": confirm if confirm is not None else password,
    }, follow_redirects=follow)


def _login(client, email, password, remember=False, follow=False):
    return client.post("/auth/login", data={
        "email": email,
        "password": password,
        "remember": "on" if remember else "",
    }, follow_redirects=follow)


def _make_user(email="existing@test.com", password="pass123"):
    user = User(full_name="Existing User", email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    db.session.add(UserSettings(user_id=user.id, monthly_budget=0))
    db.session.commit()
    return user


# ─── AUTH-001: Register with valid details ────────────────────────────────────

@pytest.mark.tc_id("AUTH-001")
def test_auth_001_register_valid(client, app):
    resp = _register(client, full_name="Priya Sharma",
                     email="priya@test.com", password="secure123")
    assert resp.status_code == 200  # followed redirect to /settings

    # User must exist in DB
    user = User.query.filter_by(email="priya@test.com").first()
    assert user is not None, "User should be created after registration"
    assert user.full_name == "Priya Sharma"

    # UserSettings row must be auto-created
    assert user.settings is not None, "UserSettings should be created on register"
    assert float(user.settings.monthly_budget) == 0.0

    # Password must be hashed, not stored in plaintext
    assert user.password_hash != "secure123"
    assert user.check_password("secure123") is True

    # Welcome flash + redirected to settings page
    assert b"Welcome" in resp.data or b"budget" in resp.data.lower()


# ─── AUTH-002: Register with existing email ───────────────────────────────────

@pytest.mark.tc_id("AUTH-002")
def test_auth_002_register_existing_email(client, app):
    _make_user(email="taken@test.com")
    count_before = User.query.count()

    resp = _register(client, email="taken@test.com", password="newpass123")
    assert resp.status_code == 200
    assert b"Email already registered" in resp.data
    assert User.query.count() == count_before, "No new user should be created"


# ─── AUTH-003: Register with short password ───────────────────────────────────

@pytest.mark.tc_id("AUTH-003")
def test_auth_003_short_password(client, app):
    count_before = User.query.count()

    resp = _register(client, email="short@test.com", password="abc")
    assert resp.status_code == 200
    assert b"at least 6 characters" in resp.data
    assert User.query.count() == count_before, "No user should be created"


# ─── AUTH-004: Password mismatch ──────────────────────────────────────────────

@pytest.mark.tc_id("AUTH-004")
def test_auth_004_password_mismatch(client, app):
    count_before = User.query.count()

    resp = _register(client, email="mismatch@test.com",
                     password="password123", confirm="different456")
    assert resp.status_code == 200
    assert b"Passwords do not match" in resp.data
    assert User.query.count() == count_before, "No user should be created"


# ─── AUTH-005: Login with valid credentials ───────────────────────────────────

@pytest.mark.tc_id("AUTH-005")
def test_auth_005_login_valid(client, app):
    _make_user(email="login@test.com", password="correctpass")

    resp = _login(client, "login@test.com", "correctpass", follow=False)
    # Should redirect to dashboard
    assert resp.status_code == 302
    assert "/" in resp.headers["Location"]
    assert "login" not in resp.headers["Location"].lower()

    # Follow redirect — dashboard must load
    resp2 = client.get("/", follow_redirects=True)
    assert resp2.status_code == 200


# ─── AUTH-006: Login with invalid password ────────────────────────────────────

@pytest.mark.tc_id("AUTH-006")
def test_auth_006_login_invalid_password(client, app):
    _make_user(email="wrongpass@test.com", password="correctpass")

    resp = _login(client, "wrongpass@test.com", "wrongpass", follow=True)
    assert resp.status_code == 200
    assert b"Invalid email or password" in resp.data

    # Must stay on login page — protected pages should still redirect
    resp2 = client.get("/expenses/", follow_redirects=False)
    assert resp2.status_code == 302, "User should NOT be logged in after failed login"


# ─── AUTH-007: Logout clears session ─────────────────────────────────────────

@pytest.mark.tc_id("AUTH-007")
def test_auth_007_logout(client, app):
    _make_user(email="logout@test.com", password="pass123")
    _login(client, "logout@test.com", "pass123")

    # Verify logged in
    assert client.get("/expenses/").status_code == 200

    # Logout
    resp = client.get("/auth/logout", follow_redirects=False)
    assert resp.status_code == 302
    assert "login" in resp.headers["Location"].lower()

    # Protected pages must now redirect
    resp2 = client.get("/expenses/", follow_redirects=False)
    assert resp2.status_code == 302, "User should not have access after logout"
    assert "login" in resp2.headers["Location"].lower()


# ─── AUTH-008: Remember me sets persistent cookie ─────────────────────────────

@pytest.mark.tc_id("AUTH-008")
def test_auth_008_remember_me(client, app):
    _make_user(email="remember@test.com", password="pass123")

    # Login without remember me — no remember_token cookie expected
    resp_no_remember = _login(client, "remember@test.com", "pass123",
                               remember=False, follow=False)
    assert resp_no_remember.status_code == 302
    no_remember_cookies = resp_no_remember.headers.get("Set-Cookie", "")

    client.get("/auth/logout")  # clear session

    # Login WITH remember me
    resp_remember = _login(client, "remember@test.com", "pass123",
                            remember=True, follow=False)
    assert resp_remember.status_code == 302

    # Flask-Login sets a 'remember_token' cookie for persistent sessions
    remember_cookies = resp_remember.headers.get("Set-Cookie", "")
    assert "remember_token" in remember_cookies, \
        "Login with remember=on should set a remember_token cookie"
    assert "remember_token" not in no_remember_cookies, \
        "Login without remember=on should NOT set a remember_token cookie"


# ─── AUTH-009: Access dashboard without login ─────────────────────────────────

@pytest.mark.tc_id("AUTH-009")
def test_auth_009_dashboard_requires_login(client, app):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    location = resp.headers["Location"].lower()
    assert "login" in location, \
        f"Unauthenticated GET / should redirect to login, got: {location}"

    # Redirect should carry the original URL as `next`
    assert "next" in location or "%2F" in location, \
        "Redirect should include the original URL as next parameter"


# ─── AUTH-010: Missing CSRF token on login ────────────────────────────────────

@pytest.mark.tc_id("AUTH-010")
def test_auth_010_login_missing_csrf(csrf_app):
    """Login POST without a CSRF token must be rejected with 400."""
    _make_user_in_csrf_app(csrf_app)
    client = csrf_app.test_client()

    resp = client.post("/auth/login", data={
        "email": "csrf_login@test.com",
        "password": "pass123",
        # csrf_token intentionally omitted
    })
    assert resp.status_code == 400, \
        "Login POST without CSRF token should return 400"


def _make_user_in_csrf_app(csrf_app):
    """Create a user inside the CSRF app's context."""
    with csrf_app.app_context():
        if not User.query.filter_by(email="csrf_login@test.com").first():
            user = User(full_name="CSRF Login User", email="csrf_login@test.com")
            user.set_password("pass123")
            db.session.add(user)
            db.session.flush()
            db.session.add(UserSettings(user_id=user.id, monthly_budget=0))
            db.session.commit()
