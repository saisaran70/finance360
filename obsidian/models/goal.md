---
title: Model — Goal
updated: 2026-05-26
---

# Goal Model

[[home]] | [[database]] | [[features/goals]] | [[models/user]]

---

## File

[app/models/goal.py](../../app/models/goal.py)

---

## Class: `Goal`

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `user_id` | FK → user.id NOT NULL | |
| `name` | String(100) NOT NULL | |
| `target_amount` | Float NOT NULL | Total to save |
| `current_amount` | Float | Amount saved so far, default 0 |
| `target_date` | Date | Optional deadline |
| `description` | String(300) | Optional notes |
| `created_at` | DateTime | |

### Computed Properties

```python
@property
def progress_percent(self) -> float:
    if self.target_amount == 0:
        return 0.0
    return min(round((self.current_amount / self.target_amount) * 100, 1), 100.0)

@property
def amount_remaining(self) -> float:
    return max(self.target_amount - self.current_amount, 0.0)
```

These are Python properties — not stored in the DB. Calculated on each access.

### `to_dict()` method

```python
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

`days_remaining` is calculated as `(target_date - date.today()).days` if `target_date` is set, else `None`.

---

## Seed Data

```python
Goal(name="Emergency Fund", target_amount=100000, current_amount=45000, target_date=..., user_id=...)
Goal(name="Vacation to Goa", target_amount=30000, current_amount=12000, ...)
Goal(name="Laptop Upgrade", target_amount=80000, current_amount=20000, ...)
```

---

## Related Notes

- [[models/user]] — User.goals relationship
- [[features/goals]] — Goal CRUD and progress UI
- [[features/dashboard]] — Goals summary widget
- [[services]] — Dashboard summary uses goal data
