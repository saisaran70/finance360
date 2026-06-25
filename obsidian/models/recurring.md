---
title: Model — RecurringExpense
updated: 2026-05-26
---

# RecurringExpense Model

[[home]] | [[database]] | [[features/recurring-bills]] | [[models/user]] | [[models/expense]]

---

## File

[app/models/recurring.py](../../app/models/recurring.py)

---

## Class: `RecurringExpense`

Defines a bill that repeats on a schedule. When `auto_add=True` and `next_due_date` is reached, a new `Expense` row is automatically created.

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `user_id` | FK → user.id NOT NULL | |
| `name` | String(100) NOT NULL | e.g. "Netflix", "Rent" |
| `amount` | Float NOT NULL | |
| `category_id` | FK → expense_category.id | Nullable |
| `billing_cycle` | String(20) | `monthly` / `weekly` / `yearly` |
| `next_due_date` | Date NOT NULL | Auto-advanced after each auto-add |
| `is_active` | Boolean | Default True — can pause without deleting |
| `auto_add` | Boolean | Default False — manual by default |
| `created_at` | DateTime | |

---

## Status

The table exists in the database (created in second migration run).
The feature UI and APScheduler task are **not yet built** — see [[features/recurring-bills]].

---

## Important: Migration History

This model was missing from the initial migration because it wasn't imported when `flask db migrate` first ran. Required a second migration:
```powershell
flask db migrate -m "add recurring expenses"
flask db upgrade
```
See [[decisions#DEC-011]] for the model import fix.

---

## Billing Cycle Advance Logic (Planned)

```python
from dateutil.relativedelta import relativedelta

def advance_date(current_date, billing_cycle):
    if billing_cycle == 'monthly':
        return current_date + relativedelta(months=1)
    elif billing_cycle == 'weekly':
        return current_date + timedelta(weeks=1)
    elif billing_cycle == 'yearly':
        return current_date + relativedelta(years=1)
```

---

## Related Notes

- [[models/user]] — User.recurring_expenses relationship
- [[models/expense]] — Recurring bills auto-create Expense rows
- [[features/recurring-bills]] — Full feature plan
- [[decisions#DEC-011]] — Why model import matters
