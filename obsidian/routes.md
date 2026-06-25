---
title: Budget Buddy AI — Routes
updated: 2026-05-26
---

# Routes

[[home]] | [[architecture]] | [[services]]

All routes require `@login_required` except auth routes.
CSRF: all POST forms include `csrf_token`. AJAX POSTs send `X-CSRFToken` header.

---

## Auth (`/auth`) — `routes/auth.py`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/auth/login` | Public | Login page |
| POST | `/auth/login` | Public | Authenticate, redirect to `/` |
| GET | `/auth/register` | Public | Register page |
| POST | `/auth/register` | Public | Create account + UserSettings row |
| GET | `/auth/logout` | Required | Clear session, redirect to login |

See [[features/auth]].

---

## Dashboard (`/`) — `routes/dashboard.py`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Required | Dashboard page — passes `summary`, `categories`, `today` |

Data is fetched client-side via AJAX from `/expenses/data` and `/ai/insights/data`.
See [[features/dashboard]] and [[services#analytics_service]].

---

## Expenses (`/expenses`) — `routes/expenses.py`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/expenses/` | Required | Expense list page |
| POST | `/expenses/add` | Required | Create new expense |
| POST | `/expenses/edit/<id>` | Required | Update expense |
| POST | `/expenses/delete/<id>` | Required | Delete expense |
| GET | `/expenses/data` | Required | JSON list — filter by `?period=3m\|6m\|1y\|all` |

`/expenses/data` response shape:
```json
[
  {
    "id": 1,
    "amount": 450.0,
    "description": "Lunch",
    "category": "Food",
    "date": "2026-05-20",
    "category_color": "#FF6B6B"
  }
]
```

See [[features/expenses]].

---

## Analytics (`/analytics`) — `routes/analytics.py`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/analytics/` | Required | Analytics page |
| GET | `/analytics/data/categories` | Required | JSON — category breakdown |
| GET | `/analytics/data/trends` | Required | JSON — 6-month monthly totals |
| GET | `/analytics/data/fixed-costs` | Required | JSON — recurring cost analysis |

These JSON endpoints feed the Chart.js charts.
See [[features/analytics]] and [[services#analytics_service]].

---

## Goals (`/goals`) — `routes/goals.py`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/goals/` | Required | Goals page |
| POST | `/goals/add` | Required | Create goal |
| POST | `/goals/edit/<id>` | Required | Update goal |
| POST | `/goals/delete/<id>` | Required | Delete goal |
| GET | `/goals/data` | Required | JSON list of goals |

See [[features/goals]].

---

## AI Insights (`/ai`) — `routes/ai.py`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/ai/insights` | Required | Insights page |
| POST | `/ai/generate` | Required | Call OpenRouter, store new insights |
| POST | `/ai/insights/<id>/read` | Required | Mark insight as read |
| GET | `/ai/insights/data` | Required | JSON list of insights |

CSRF on AJAX: `ai.py` uses `validate_csrf()` manually for JSON endpoints.
See [[features/ai-insights]] and [[services#ai_service]].

---

## Settings (`/settings`) — `routes/settings.py`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/settings/` | Required | Settings page |
| POST | `/settings/profile` | Required | Update username |
| POST | `/settings/budget` | Required | Update monthly budget + saving % |
| POST | `/settings/notifications` | Required | Toggle AI/budget/weekly alerts |

See [[features/settings]].

---

## Related Notes

- [[architecture]] — Blueprint registration in `create_app()`
- [[services]] — Business logic called by routes
- [[features/auth]] — Auth flow detail
- [[features/expenses]] — Expense CRUD detail
- [[features/ai-insights]] — AI endpoint detail
