---
title: Feature — Analytics
updated: 2026-05-26
---

# Analytics

[[home]] | [[routes]] | [[services]] | [[features/dashboard]] | [[features/expenses]]

---

## What It Does

Deep-dive spending analysis on a dedicated page:
- Category breakdown (donut chart + ranked list with %)
- 6-month spending trend (line chart)
- Fixed/recurring cost analysis

---

## Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/analytics/` | Analytics page |
| GET | `/analytics/data/categories` | Category breakdown JSON |
| GET | `/analytics/data/trends` | Monthly trend JSON |
| GET | `/analytics/data/fixed-costs` | Recurring cost summary JSON |

---

## Template

`app/templates/analytics/index.html`

Sections:
1. **Category Donut** — Chart.js, `/analytics/data/categories`
2. **Category Progress Bars** — each category as a % bar
3. **Trend Line Chart** — 6 months, `/analytics/data/trends`
4. **Fixed Cost Cards** — recurring bills totals, `/analytics/data/fixed-costs`

---

## Data Formats

### `/analytics/data/categories`
```json
[
  {
    "category": "Food",
    "total": 12000.0,
    "percentage": 37.5,
    "color": "#FF6B6B",
    "icon": "🍕"
  }
]
```

### `/analytics/data/trends`
```json
[
  {"month": "Dec 2025", "total": 12400.0},
  {"month": "Jan 2026", "total": 15800.0},
  {"month": "Feb 2026", "total": 11200.0},
  {"month": "Mar 2026", "total": 18900.0},
  {"month": "Apr 2026", "total": 14500.0},
  {"month": "May 2026", "total": 32000.0}
]
```

---

## Service Functions

All analytics data comes from `analytics_service.py` — see [[services]]:
- `get_category_breakdown(user)` → categories JSON
- `get_monthly_trends(user, months=6)` → trends JSON
- `get_fixed_cost_analysis(user)` → fixed costs JSON

---

## Related Notes

- [[services]] — All analytics service functions
- [[features/expenses]] — Source data for analytics
- [[features/dashboard]] — Simplified analytics summary
- [[decisions#DEC-009]] — Why Chart.js
