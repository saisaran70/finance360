---
title: Feature — Dashboard
updated: 2026-05-26
---

# Dashboard

[[home]] | [[routes]] | [[services]] | [[features/expenses]] | [[features/goals]] | [[features/ai-insights]]

---

## What It Does

The main landing page after login. Shows a financial overview at a glance:
- Monthly spending vs budget
- Category breakdown donut chart
- Recent expenses
- Savings goals summary
- Latest AI insight

---

## Route

`GET /` → `routes/dashboard.py:index()`

Passes to template:
- `summary` — from `analytics_service.get_dashboard_summary(user)`
- `categories` — all `ExpenseCategory` rows (for Add Expense modal dropdown)
- `today` — current date ISO string

---

## Template

`app/templates/dashboard/index.html` — extends `base.html`

Page structure:
1. **4 Summary Cards** (static from `summary` dict)
   - Total Expenses This Month
   - Budget Remaining
   - Active Goals
   - Money Saved
2. **Category Donut Chart** — Chart.js, populated via AJAX
3. **Recent Expenses** — table, populated via AJAX
4. **AI Insight Card** — populated via AJAX
5. **Goals Summary** — populated via AJAX

---

## AJAX Data Flow

All chart/data sections load asynchronously after the HTML shell renders:

```javascript
// In dashboard/index.html script block
fetch('/expenses/data?period=3m')   // → expense list for donut + table
fetch('/ai/insights/data')          // → latest AI insight card
fetch('/goals/data')                // → goals progress bars
```

This keeps initial page load fast — template renders in ~50ms, data fills in via JS.

---

## Summary Dict Shape

```python
{
    "total_expenses": 32000.0,
    "monthly_budget": 50000.0,
    "budget_remaining": 18000.0,
    "budget_percent": 64.0,
    "active_goals": 3,
    "total_saved": 28500.0,
    "expense_count": 18,
    "top_category": "Food",
    "ai_insights_count": 2
}
```

---

## Service

`analytics_service.get_dashboard_summary(user)` in [[services]].
Queries: `Expense` (this month), `Goal` (active), `UserSettings`, `AIInsight` (unread count).

---

## Related Notes

- [[services#get_dashboard_summary]] — Summary calculation
- [[features/expenses]] — Expense list and AJAX data
- [[features/analytics]] — Full analytics page (more detail)
- [[features/ai-insights]] — AI insight generation
- [[models/expense]] — Expense model
- [[models/goal]] — Goal model
