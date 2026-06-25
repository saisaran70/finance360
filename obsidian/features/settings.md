---
title: Feature — Settings
updated: 2026-05-26
---

# Settings

[[home]] | [[routes]] | [[models/settings]] | [[features/auth]]

---

## What It Does

Allows users to configure their profile, monthly budget limit, saving goal percentage, and notification preferences.

---

## Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/settings/` | Settings page |
| POST | `/settings/profile` | Update username |
| POST | `/settings/budget` | Update budget + saving % |
| POST | `/settings/notifications` | Toggle notification flags |

---

## Template

`app/templates/settings/index.html`

Three sections with separate save buttons:

### Profile
- Username field
- Email (display only, not editable)

### Budget
- Monthly budget (₹)
- Saving goal percentage (% of income to save target)
- Currency preference

### Notifications
- AI insights enabled toggle
- Budget alerts enabled toggle
- Weekly summary enabled toggle

---

## Model

[[models/settings]] — `UserSettings` with one-to-one relationship to `User`.

`UserSettings` is created automatically when a user registers in [[features/auth]].

---

## Default Values

| Setting | Default |
|---------|---------|
| `monthly_budget` | `0` (not set) |
| `saving_goal_percentage` | `20.0` |
| `currency` | `₹` |
| `ai_insights_enabled` | `True` |
| `budget_alerts_enabled` | `True` |
| `weekly_summary_enabled` | `False` |

---

## Related Notes

- [[models/settings]] — UserSettings model detail
- [[features/auth]] — Settings row created on register
- [[features/ai-insights]] — Uses `ai_insights_enabled` flag
- [[services]] — Budget limit used in analytics summary
