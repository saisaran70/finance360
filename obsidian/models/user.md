---
title: Model — User
updated: 2026-06-03
---

# User Model

[[home]] | [[database]] | [[features/auth]] | [[models/settings]]

---

## File

[app/models/user.py](../../app/models/user.py)

---

## Class: `User`

Inherits `db.Model` + `UserMixin` (Flask-Login).

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `full_name` | String(100) NOT NULL | Display name |
| `email` | String(150) UNIQUE NOT NULL | Login identifier |
| `password_hash` | Text NOT NULL | PBKDF2 SHA-256 via Werkzeug, or `OAUTH:google` sentinel |
| `google_id` | String(100) UNIQUE NULL | Google OAuth sub ID — added 2026-06-03 |
| `currency` | String(10) | Default `INR` |
| `city` | String(100) | Optional |
| `theme_preference` | String(20) | Default `dark` |
| `created_at` | DateTime | UTC |
| `updated_at` | DateTime | UTC, auto-updated |

### Relationships

```python
expenses = db.relationship('Expense', backref='user', lazy='dynamic', cascade='all, delete-orphan')
goals = db.relationship('Goal', backref='user', lazy='dynamic', cascade='all, delete-orphan')
ai_insights = db.relationship('AIInsight', backref='user', lazy='dynamic', cascade='all, delete-orphan')
recurring_expenses = db.relationship('RecurringExpense', backref='user', lazy='dynamic', cascade='all, delete-orphan')
settings = db.relationship('UserSettings', backref='user', uselist=False, cascade='all, delete-orphan')
```

All relationships use `cascade='all, delete-orphan'` — deleting a user deletes all their data.

### Methods

```python
def set_password(self, password: str) -> None:
    self.password_hash = generate_password_hash(password)

def check_password(self, password: str) -> bool:
    # Guards against OAuth-only users (password_hash = 'OAUTH:google')
    if not self.password_hash or self.password_hash.startswith('OAUTH:'):
        return False
    return check_password_hash(self.password_hash, password)

@property
def is_oauth_user(self) -> bool:
    return bool(self.password_hash and self.password_hash.startswith('OAUTH:'))
```

### Flask-Login Callback

```python
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
```

---

## Google OAuth Users

Google-authenticated users have `google_id` set and `password_hash = 'OAUTH:google'`.
- `check_password()` always returns `False` for these users
- `is_oauth_user` property returns `True`
- Login page shows a friendly redirect message if they try to use email/password

See [[decisions#DEC-015]] and [[features/auth#Google OAuth]].

---

## Critical: Model Import Order

All models must be imported inside `create_app()` before blueprints:
```python
from app.models import user, expense, goal, settings, ai_insight, recurring
```
See [[decisions#DEC-011]].

---

## Related Notes

- [[models/settings]] — UserSettings one-to-one with User
- [[models/expense]] — User.expenses relationship
- [[models/goal]] — User.goals relationship
- [[models/ai-insight]] — User.ai_insights relationship
- [[models/recurring]] — User.recurring_expenses relationship
- [[features/auth]] — User creation and auth logic
- [[decisions#DEC-006]] — Why session auth + Werkzeug
- [[decisions#DEC-015]] — Google OAuth decision
