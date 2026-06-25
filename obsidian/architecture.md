---
title: Budget Buddy AI — Architecture
updated: 2026-05-26
---

# Architecture

[[home]] | [[stack]] | [[database]] | [[routes]] | [[services]]

---

## Layer Overview

```
Browser (HTML + Vanilla JS + Chart.js)
        │
        │  HTTP  (AJAX fetch + form POST)
        ▼
┌─────────────────────────────────────────────┐
│              Flask Application               │
│                                             │
│  ┌──────────┐  ┌───────────────────────┐   │
│  │  Routes  │  │   Jinja2 Templates    │   │
│  │(Blueprints)│  │  base.html + pages  │   │
│  └────┬─────┘  └───────────────────────┘   │
│       │                                     │
│  ┌────▼─────────────────────┐               │
│  │      Service Layer        │               │
│  │  analytics_service.py     │               │
│  │  ai_service.py            │               │
│  └────┬─────────────────────┘               │
│       │                                     │
│  ┌────▼─────────────────────┐               │
│  │    SQLAlchemy ORM         │               │
│  │  (models/*.py)            │               │
│  └────┬─────────────────────┘               │
│       │                                     │
│  ┌────▼─────────┐                          │
│  │  SQLite DB   │  (→ PostgreSQL prod)      │
│  │  budget_buddy│                           │
│  │  .db         │                           │
│  └──────────────┘                          │
└─────────────────────────────────────────────┘
        │
        │  HTTPS  (OpenRouter API)
        ▼
   OpenRouter → openai/gpt-oss-20b:free
```

---

## Entry Points

| File | Role |
|------|------|
| `run.py` | Dev server entry point (`python run.py`) |
| `app/__init__.py` | Application factory `create_app()` |
| `config.py` | Environment-based configuration |
| `.env` | Secrets (API key, SECRET_KEY, DATABASE_URL) |

---

## Application Factory Pattern

`create_app()` in [app/__init__.py](../app/__init__.py):
1. Creates Flask app object
2. Loads config from `config.py`
3. Initialises extensions: `db`, `migrate`, `login_manager`, `csrf`
4. **Imports all models** (required for SQLAlchemy relationship resolution) — see [[decisions#DEC-011]]
5. Registers all 7 blueprints

---

## Blueprint Structure

| Blueprint | Prefix | File | Feature |
|-----------|--------|------|---------|
| `auth_bp` | `/auth` | `routes/auth.py` | [[features/auth]] |
| `dashboard_bp` | `/` | `routes/dashboard.py` | [[features/dashboard]] |
| `expenses_bp` | `/expenses` | `routes/expenses.py` | [[features/expenses]] |
| `analytics_bp` | `/analytics` | `routes/analytics.py` | [[features/analytics]] |
| `goals_bp` | `/goals` | `routes/goals.py` | [[features/goals]] |
| `ai_bp` | `/ai` | `routes/ai.py` | [[features/ai-insights]] |
| `settings_bp` | `/settings` | `routes/settings.py` | [[features/settings]] |

---

## Data Flow: Dashboard Page Load

```
Browser → GET /
  → dashboard.py:index()
  → analytics_service.get_dashboard_summary(user)
      → queries Expense, Goal, UserSettings
  → render_template('dashboard/index.html', summary, categories, today)
  → HTML returned with empty chart containers

Browser JS (main.js) → fetch('/expenses/data?period=3m')
  → expenses.py:expense_data()
  → returns JSON list of expenses
  → Chart.js renders donut chart

Browser JS → fetch('/ai/insights/data')
  → ai.py:insights_data()
  → returns JSON list of AIInsight rows
  → renders insight card in DOM
```

---

## Security Layers

| Concern | Implementation |
|---------|---------------|
| Auth | [[features/auth]] — Flask-Login `@login_required` |
| Passwords | Werkzeug PBKDF2 SHA-256 — see [[models/user]] |
| CSRF | Flask-WTF `CSRFProtect` — see [[decisions#DEC-007]] |
| Sessions | Signed cookie via `SECRET_KEY` |
| SQL injection | SQLAlchemy ORM (no raw SQL) |

---

## External Integrations

| Service | Purpose | Config |
|---------|---------|--------|
| OpenRouter API | AI budget insights | `OPENROUTER_API_KEY` in `.env` |
| APScheduler | Recurring bill cron (planned) | installed, not yet wired |

See [[features/ai-insights]] and [[decisions#DEC-004]].

---

## Related Notes

- [[stack]] — Why each technology was chosen
- [[database]] — Schema and relationships
- [[routes]] — Full endpoint listing
- [[services]] — Service layer details
- [[decisions]] — Every architectural decision
