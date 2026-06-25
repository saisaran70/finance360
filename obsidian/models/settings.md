---
title: Model — UserSettings
updated: 2026-05-26
---

# UserSettings Model

[[home]] | [[database]] | [[features/settings]] | [[models/user]]

---

## File

[app/models/settings.py](../../app/models/settings.py)

---

## Class: `UserSettings`

One-to-one with `User`. Created automatically when a user registers.

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `id` | Integer PK | | |
| `user_id` | FK → user.id UNIQUE | | One-to-one enforced by UNIQUE |
| `monthly_budget` | Float | `0.0` | 0 means not set |
| `saving_goal_percentage` | Float | `20.0` | % of income to save |
| `currency` | String(10) | `₹` | Display symbol |
| `ai_insights_enabled` | Boolean | `True` | |
| `budget_alerts_enabled` | Boolean | `True` | |
| `weekly_summary_enabled` | Boolean | `False` | |

---

## Creation on Register

In `routes/auth.py` register handler:
```python
user_settings = UserSettings(user_id=user.id)
db.session.add(user_settings)
db.session.commit()
```

---

## Access Pattern

From any route with `current_user`:
```python
settings = current_user.settings
if settings and settings.monthly_budget > 0:
    budget = settings.monthly_budget
```

---

## Usage in Services

`analytics_service.get_dashboard_summary()` reads `monthly_budget` to calculate budget remaining and budget percent.

`ai_service.generate_insights()` reads `monthly_budget` and `saving_goal_percentage` to include in the AI prompt.

---

## Related Notes

- [[models/user]] — One-to-one relationship
- [[features/settings]] — Settings edit UI
- [[services]] — Budget values used in analytics
