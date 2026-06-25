---
title: Budget Buddy AI — Services
updated: 2026-05-26
---

# Services

[[home]] | [[architecture]] | [[routes]] | [[features/ai-insights]] | [[features/analytics]]

The service layer isolates all business logic from route handlers.
Both files live in `app/services/`.

---

## analytics_service.py

### `get_dashboard_summary(user)`

Returns a dict consumed by `dashboard/index.html`:

```python
{
  "total_expenses": float,      # sum of all user expenses this month
  "monthly_budget": float,      # from UserSettings
  "budget_remaining": float,
  "budget_percent": float,       # 0–100+
  "active_goals": int,
  "total_saved": float,          # sum of current_amount across goals
  "expense_count": int,
  "top_category": str,
  "ai_insights_count": int
}
```

### `get_category_breakdown(user)`

Returns list of category spending for current month:

```python
[
  {
    "category": "Food",
    "total": 3200.0,
    "percentage": 38.5,
    "color": "#FF6B6B",
    "icon": "🍕"
  },
  ...
]
```

Used by: `/analytics/data/categories` → Chart.js donut chart.

### `get_monthly_trends(user, months=6)`

Returns 6-month rolling spending totals:

```python
[
  {"month": "Dec 2025", "total": 12400.0},
  {"month": "Jan 2026", "total": 15800.0},
  ...
]
```

Used by: `/analytics/data/trends` → Chart.js line chart.

### `get_fixed_cost_analysis(user)`

Returns recurring expense summary:

```python
{
  "total_fixed": float,
  "items": [
    {"name": "Netflix", "amount": 649.0, "cycle": "monthly", "next_due": "2026-06-01"}
  ]
}
```

Used by: `/analytics/data/fixed-costs`.

### `get_chart_data(user)`

Aggregates all chart data in a single call. Used by dashboard AJAX.

---

## ai_service.py

### `generate_insights(user)`

Main function called by `POST /ai/generate`.

Flow:
1. Gets last 30 days of expenses
2. Gets UserSettings (budget, saving goal)
3. Gets active goals
4. Builds OpenRouter prompt (JSON format request)
5. Calls `_call_openrouter(prompt)` → parses JSON response
6. On failure: calls `_fallback_insights(user)` — see [[decisions#DEC-012]]
7. Saves new `AIInsight` rows to DB (clears old unread ones first)

### `_call_openrouter(prompt)`

HTTP call to OpenRouter:

```python
requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://budget-buddy-ai.local",
        "X-Title": "Budget Buddy AI",
    },
    json={
        "model": model,        # from config — OPENROUTER_MODEL
        "messages": [...],
        "max_tokens": 600,
        "temperature": 0.4,
    },
    timeout=20,
)
```

- Model configurable via `OPENROUTER_MODEL` in `.env` — see [[decisions#DEC-005]]
- Strips markdown code fences from response before JSON parse
- Error handling: HTTPError, JSONDecodeError, RequestException all caught separately

### `_fallback_insights(user)`

Produces 3 rule-based insights without the API:
1. **Budget warning** — if spending > 80% of monthly budget
2. **Top category alert** — if one category is > 40% of spending
3. **Month projection** — if on track to exceed budget by end of month

Returns same structure as OpenRouter path so the route handler is unaware of which path ran.

---

## Prompt Format

```
You are a personal finance AI assistant. Analyze this user's financial data and provide insights.

User's financial data:
- Monthly budget: ₹50000
- Total spent this month: ₹32000
- Top category: Food (₹12000, 37.5%)
- Active goals: Emergency Fund (45% complete)
- Recent expenses: [last 30 days list]

Respond with ONLY valid JSON in this format:
{
  "insights": [
    {
      "type": "warning|success|tip|alert",
      "title": "Short title",
      "message": "2-3 sentence explanation",
      "priority": 1
    }
  ]
}
```

---

## Related Notes

- [[features/ai-insights]] — AI insights UI and user flow
- [[features/analytics]] — Analytics charts using service data
- [[features/dashboard]] — Dashboard summary using service data
- [[decisions#DEC-004]] — Why OpenRouter
- [[decisions#DEC-012]] — Why fallback insights
