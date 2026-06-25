---
title: Model — Expense
updated: 2026-05-26
---

# Expense Model

[[home]] | [[database]] | [[features/expenses]] | [[features/analytics]] | [[models/user]]

---

## File

[app/models/expense.py](../../app/models/expense.py)

---

## Class: `ExpenseCategory`

Lookup table. Seeded with 8 defaults on first run.

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `name` | String(50) UNIQUE | |
| `icon` | String(10) | Emoji |
| `color` | String(7) | Hex color |

### Default Categories

| Name | Icon | Color |
|------|------|-------|
| Food | 🍕 | #FF6B6B |
| Transport | 🚗 | #4ECDC4 |
| Shopping | 🛍️ | #45B7D1 |
| Bills | ⚡ | #FFA07A |
| Entertainment | 🎬 | #98D8C8 |
| Health | 💊 | #F7DC6F |
| Education | 📚 | #BB8FCE |
| Others | 📦 | #85C1E9 |

### `seed_defaults()` classmethod

Called from `seed.py` and can be called from `flask shell`. Checks if categories already exist before inserting.

---

## Class: `Expense`

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `user_id` | FK → user.id NOT NULL | |
| `category_id` | FK → expense_category.id | Nullable |
| `amount` | Float NOT NULL | |
| `description` | String(200) NOT NULL | |
| `date` | Date NOT NULL | |
| `is_recurring` | Boolean | Links to RecurringExpense |
| `created_at` | DateTime | |

### `to_dict()` method

Returns JSON-serializable dict for AJAX endpoints:
```python
{
    "id": 1,
    "amount": 450.0,
    "description": "Lunch",
    "category": "Food",
    "category_color": "#FF6B6B",
    "category_icon": "🍕",
    "date": "2026-05-20",
    "is_recurring": False
}
```

---

## Query Patterns

Filter by period (used in `/expenses/data`):
```python
since = date.today() - timedelta(days=90)  # 3m
expenses = Expense.query.filter(
    Expense.user_id == current_user.id,
    Expense.date >= since
).order_by(Expense.date.desc()).all()
```

---

## Related Notes

- [[models/user]] — User.expenses relationship
- [[features/expenses]] — CRUD and filter UI
- [[features/analytics]] — Category breakdown uses Expense data
- [[services]] — analytics_service queries Expense
