---
title: Feature — Savings Goals
updated: 2026-05-26
---

# Savings Goals

[[home]] | [[routes]] | [[models/goal]] | [[features/dashboard]]

---

## What It Does

Users create savings goals with a target amount, optional target date, and track contributions over time.

---

## Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/goals/` | Goals page |
| POST | `/goals/add` | Create goal |
| POST | `/goals/edit/<id>` | Update goal (incl. adding money) |
| POST | `/goals/delete/<id>` | Delete goal |
| GET | `/goals/data` | JSON list of goals |

---

## Template

`app/templates/goals/index.html`

- **Goal Cards** — each with name, progress bar, current/target amounts, days remaining
- **Add Goal Modal** — name, target amount, target date (optional), description
- **Edit Goal Modal** — also allows updating `current_amount` (i.e. logging a contribution)

---

## Goal Card Data

From `Goal.to_dict()`:
```json
{
  "id": 1,
  "name": "Emergency Fund",
  "target_amount": 100000.0,
  "current_amount": 45000.0,
  "progress_percent": 45.0,
  "amount_remaining": 55000.0,
  "target_date": "2026-12-31",
  "days_remaining": 219,
  "description": "6 months of living expenses"
}
```

---

## Seed Data Goals

From `seed.py` (test account):
1. **Emergency Fund** — ₹1,00,000 target, ₹45,000 saved (45%)
2. **Vacation to Goa** — ₹30,000 target, ₹12,000 saved (40%)
3. **Laptop Upgrade** — ₹80,000 target, ₹20,000 saved (25%)

---

## Model

[[models/goal]] — `progress_percent` and `amount_remaining` as Python properties (not DB columns).

---

## Related Notes

- [[models/goal]] — Goal model detail
- [[features/dashboard]] — Goals summary widget on dashboard
- [[services]] — Dashboard summary uses goal data
