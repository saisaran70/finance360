---
title: Feature — Authentication
updated: 2026-06-03
---

# Authentication

[[home]] | [[routes]] | [[models/user]] | [[decisions#DEC-006]] | [[decisions#DEC-007]] | [[decisions#DEC-015]]

---

## What It Does

Handles user registration, login, logout, and Google OAuth sign-in. All other pages require authentication.

---

## User Flows

### Email / Password
```
/auth/register → fill form → POST → create User + UserSettings → redirect to /settings
/auth/login    → fill form → POST → set session → redirect to /
/auth/logout   → GET → clear session → redirect to /auth/login
```

### Google OAuth
```
/auth/google          → redirect to Google consent screen
Google callback       → /auth/google/callback
                        → find by google_id → login
                        → or find by email → link account + login
                        → or create new user + UserSettings → login → redirect to /
```

---

## Route File

[app/routes/auth.py](../../app/routes/auth.py)

### Register (`POST /auth/register`)

1. Validate: full_name, email, password, confirm_password
2. Check email not already taken
3. Hash password with Werkzeug: `generate_password_hash(password)`
4. Create `User` row
5. Create `UserSettings` row (one-to-one)
6. Flash success, redirect to `/settings`

### Login (`POST /auth/login`)

1. Find user by email
2. Check `user.is_oauth_user` → if True, show "use Google button" message
3. `check_password_hash(user.password_hash, password)`
4. `login_user(user)` — sets Flask-Login session
5. Redirect to `next` param or `/`

### Google Login (`GET /auth/google`)

1. Authlib generates Google OAuth URL with state nonce
2. Redirects browser to `accounts.google.com/o/oauth2/v2/auth`

### Google Callback (`GET /auth/google/callback`)

1. Authlib exchanges `code` for token, fetches `userinfo`
2. Look up user by `google_id`
3. If not found → look up by `email` → link account (set `google_id`)
4. If not found at all → create new `User` (password_hash=`'OAUTH:google'`) + `UserSettings`
5. `login_user(user, remember=True)`
6. Redirect to `/`

### Logout (`GET /auth/logout`)

1. `logout_user()` — clears session
2. Redirect to `/auth/login`

---

## Security

| Concern | Implementation |
|---------|---------------|
| Password storage | Werkzeug `pbkdf2:sha256` — never plaintext |
| OAuth users | `password_hash = 'OAUTH:google'` sentinel — `check_password` always returns False |
| CSRF (forms) | Flask-WTF token in every form |
| CSRF (OAuth) | Authlib state nonce in session |
| Session | Signed cookie, invalidated on logout |
| Brute force | No rate limiting yet (Phase 12 todo) |

See [[decisions#DEC-006]], [[decisions#DEC-007]], [[decisions#DEC-015]].

---

## Templates

- `app/templates/auth/login.html` — Sign In form + "Continue with Google" button
- `app/templates/auth/register.html` — Register form + "Continue with Google" button

Both include `{{ csrf_token() }}` in the email/password form.
Google button is a plain `<a href="/auth/google">` — no CSRF needed (GET request).

---

## Dependencies

| Library | Purpose |
|---------|---------|
| `flask-login` | Session management, `@login_required` |
| `werkzeug` | Password hashing |
| `flask-wtf` | CSRF protection |
| `authlib` | Google OAuth 2.0 flow |

Credentials stored in `.env`: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`.

---

## Model

[[models/user]] — `User` with `password_hash`, `google_id`, `set_password()`, `check_password()`, `is_oauth_user`

---

## Related Notes

- [[models/user]] — User model detail
- [[models/settings]] — UserSettings created on register/Google signup
- [[decisions#DEC-006]] — Auth strategy choice
- [[decisions#DEC-007]] — CSRF protection choice
- [[decisions#DEC-015]] — Google OAuth decision
