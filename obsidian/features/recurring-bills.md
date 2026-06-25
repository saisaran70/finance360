---
title: Feature — Recurring Bills (Phase 8)
updated: 2026-05-26
---

# Recurring Bills

[[home]] | [[roadmap]] | [[models/recurring]] | [[features/expenses]] | [[features/analytics]]

---

## Status

🔲 **Not yet built** — Phase 8 of [[roadmap]]

Model exists: [[models/recurring]] — `RecurringExpense` table is in the DB.
APScheduler is installed but not yet wired up.

---

## Planned Functionality

- User defines a recurring bill: name, amount, category, billing cycle (monthly/weekly/yearly), next due date
- A background job (APScheduler) checks daily: if `next_due_date <= today` and `auto_add = True`, create an `Expense` row automatically
- After auto-creating, advance `next_due_date` by one billing cycle
- Dashboard widget shows upcoming bills (next 7 days)
- Toggle `auto_add` per bill (manual vs automatic)

---

## Existing Model

[[models/recurring]] — `RecurringExpense` columns:
- `name`, `amount`, `category_id`
- `billing_cycle` — `monthly` / `weekly` / `yearly`
- `next_due_date` — Date
- `is_active` — Boolean
- `auto_add` — Boolean (auto-create expense)

---

## Implementation Plan

### 1. APScheduler Setup

In `app/__init__.py`:
```python
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

def create_app(...):
    ...
    from app.tasks import check_recurring_bills
    scheduler.add_job(check_recurring_bills, 'cron', hour=6, minute=0)
    scheduler.start()
```

### 2. Task Function

```python
# app/tasks.py
def check_recurring_bills():
    with app.app_context():
        today = date.today()
        due = RecurringExpense.query.filter(
            RecurringExpense.is_active == True,
            RecurringExpense.auto_add == True,
            RecurringExpense.next_due_date <= today
        ).all()
        for bill in due:
            expense = Expense(
                user_id=bill.user_id,
                amount=bill.amount,
                description=bill.name,
                category_id=bill.category_id,
                date=today,
                is_recurring=True,
            )
            db.session.add(expense)
            # Advance next_due_date
            bill.next_due_date = advance_date(bill.next_due_date, bill.billing_cycle)
        db.session.commit()
```

### 3. UI Routes (to add)

- `GET /recurring/` — list recurring bills
- `POST /recurring/add` — add new
- `POST /recurring/edit/<id>` — update
- `POST /recurring/toggle/<id>` — activate/deactivate

### 4. Dashboard Widget

Show bills due in next 7 days, ordered by `next_due_date`.

---

## Related Notes

- [[models/recurring]] — RecurringExpense model
- [[roadmap]] — Full phase plan
- [[features/expenses]] — Auto-created expense rows land here
- [[features/analytics]] — Fixed cost analysis uses recurring data
