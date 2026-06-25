# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working Style

Always address the user as **boss**.

---

## Project Context

This repo is **Finance360** — an AI-powered organizational financial management platform (Flask + SQLAlchemy + Chart.js). It is being built by migrating from **BudgetBuddy AI v1**, which is the current baseline on `master`. The full product spec is in [FINANCE360.md](FINANCE360.md). Progress and decisions are tracked in the [obsidian/](obsidian/) vault.

Demo credentials: `test@budgetbuddy.com` / `test1234`

---

## Common Commands

```powershell
# Activate virtual environment (always required first)
.venv\Scripts\activate

# Run the app
python run.py                  # http://127.0.0.1:5000

# Or use the one-click launcher (runs setup_db.py + starts server + opens browser)
launch.bat

# Database setup (idempotent — safe to run multiple times)
python setup_db.py             # runs migrations, seeds categories, creates demo account

# Migrations
flask db migrate -m "description"
flask db upgrade

# Seed test data (drops and recreates test user)
python seed.py

# Run all tests
pytest tests/ -v

# Run a single test file
pytest tests/test_expenses.py -v
pytest tests/test_auth.py -v

# Run a single test by name
pytest tests/test_expenses.py -k "test_add_expense" -v

# Flask shell (has all models pre-imported)
flask shell
```

---

## Architecture

### App Factory Pattern

`app/__init__.py` exports `db`, `migrate`, `login_manager`, `csrf`, `oauth` as module-level singletons. `create_app(config_name)` wires them together. `run.py` calls `create_app()` and registers a shell context. **All imports of models and routes must happen inside `create_app()`** to avoid circular imports — the model import block at the top of `create_app` is the fix for SQLAlchemy relationship resolution.

### Blueprints

| Blueprint | Prefix | File |
|-----------|--------|------|
| `auth_bp` | `/auth` | `app/routes/auth.py` |
| `dashboard_bp` | `/` | `app/routes/dashboard.py` |
| `expenses_bp` | `/expenses` | `app/routes/expenses.py` |
| `analytics_bp` | `/analytics` | `app/routes/analytics.py` |
| `goals_bp` | `/goals` | `app/routes/goals.py` |
| `settings_bp` | `/settings` | `app/routes/settings.py` |
| `ai_bp` | `/ai` | `app/routes/ai.py` |

### Services Layer

Business logic lives in `app/services/`, never in routes.

- `analytics_service.py` — all dashboard/analytics queries (`get_dashboard_summary`, `get_category_breakdown`, `get_monthly_trends`, `get_spending_savings_trend`, `get_projected_spend`, `get_goal_analytics`, `get_fixed_cost_analysis`)
- `ai_service.py` — calls OpenRouter API; falls back to `_fallback_insights()` when the key is missing or the API fails

### Models

All models inherit from `db.Model`. Key relationships:
- `User` → `Expense`, `Goal`, `UserSettings` (one-to-one), `AIInsight`, `RecurringExpense`
- `Expense` → `ExpenseCategory` (many-to-one)
- OAuth users have `password_hash = 'OAUTH:google'` — always check `user.is_oauth_user` before calling `check_password()`

### Frontend Pattern

Templates use Jinja2 with a `base.html` layout. Charts are Chart.js, loaded via AJAX from JSON endpoints (e.g. `/expenses/data`, `/analytics/spending-savings`). CSRF tokens are required on all POST forms — `csrf = CSRFProtect()` is global.

### Config & Environment

`config.py` defines `DevelopmentConfig` / `ProductionConfig`, loaded via `config[config_name]`. All secrets come from `.env` via `python-dotenv`. Key env vars: `SECRET_KEY`, `DATABASE_URL`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`.

### Database

SQLite in development (`instance/budget_buddy.db`), PostgreSQL in production (swap `DATABASE_URL`). Migrations use Flask-Migrate (Alembic) with `render_as_batch=True` for SQLite ALTER TABLE compatibility.

### Testing

Tests use an **in-memory SQLite** database. CSRF is disabled by default (`WTF_CSRF_ENABLED: False`) except in the `csrf_app` fixture. The `auth_client` fixture provides a pre-logged-in test client. After every run, `conftest.py` auto-writes per-module markdown logs to `logs/`.

### Obsidian + Git Automation

The Stop hook (`.claude/settings.json`) runs on every session end:
1. `scripts/update_obsidian.py` — refreshes frontmatter `updated:` dates across all vault notes
2. `git add -A && git commit && git push` — auto-commits and pushes everything
