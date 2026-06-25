---
title: Feature — Expense Tracking
updated: 2026-05-26
---

# Expense Tracking

[[home]] | [[routes]] | [[models/expense]] | [[features/analytics]] | [[features/dashboard]]

---

## What It Does

Core CRUD for expenses. Add, edit, delete expenses with category assignment.
Filterable by time period (3m / 6m / 1y / all).

---

## Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/expenses/` | List page |
| POST | `/expenses/add` | Create expense |
| POST | `/expenses/edit/<id>` | Update expense |
| POST | `/expenses/delete/<id>` | Delete expense |
| GET | `/expenses/data?period=` | JSON list |

---

## Template

`app/templates/expenses/index.html`

- **Filter tabs** — 3M / 6M / 1Y / All (clicking changes `period` param in AJAX URL)
- **Expense list** — rows with amount, description, category chip, date, edit/delete buttons
- **Add Modal** — `openModal('add-expense-modal')` — form with category dropdown
- **Edit Modal** — pre-filled via JS when Edit is clicked

---

## AJAX Endpoint

`GET /expenses/data?period=3m`

Response (list of `Expense.to_dict()`):
```json
[
  {
    "id": 1,
    "amount": 450.0,
    "description": "Lunch at restaurant",
    "category": "Food",
    "category_color": "#FF6B6B",
    "category_icon": "🍕",
    "date": "2026-05-20",
    "is_recurring": false
  }
]
```

Period filters:
- `3m` — last 3 months (default)
- `6m` — last 6 months
- `1y` — last 12 months
- `all` — all time

---

## Form Fields

| Field | Type | Validation |
|-------|------|-----------|
| amount | Float | Required, > 0 |
| description | String | Required, max 200 |
| category_id | FK | Optional |
| date | Date | Required, defaults to today |
| is_recurring | Boolean | Optional checkbox |

---

## Model

[[models/expense]] — `Expense` + `ExpenseCategory`

Categories are seeded at startup: Food, Transport, Shopping, Bills, Entertainment, Health, Education, Others.

---

## Related Notes

- [[models/expense]] — Expense model detail
- [[features/analytics]] — Category breakdown uses expense data
- [[features/dashboard]] — Recent expenses on dashboard
- [[features/recurring-bills]] — Recurring flag links here
