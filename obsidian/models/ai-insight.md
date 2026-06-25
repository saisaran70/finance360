---
title: Model — AIInsight
updated: 2026-05-26
---

# AIInsight Model

[[home]] | [[database]] | [[features/ai-insights]] | [[models/user]]

---

## File

[app/models/ai_insight.py](../../app/models/ai_insight.py)

---

## Class: `AIInsight`

Stores AI-generated recommendations for a user. Regenerated on demand.

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `user_id` | FK → user.id NOT NULL | |
| `insight_type` | String(50) | `warning` / `success` / `tip` / `alert` |
| `title` | String(200) NOT NULL | Short headline |
| `message` | Text NOT NULL | 2-3 sentence explanation |
| `priority` | Integer | 1 = high, 2 = medium, 3 = low |
| `is_read` | Boolean | Default False |
| `created_at` | DateTime | `default=datetime.utcnow` |

---

## Insight Types

| Type | Visual Style | Meaning |
|------|-------------|---------|
| `warning` | Amber border | Overspending risk |
| `success` | Mint/green border | On-track or good behaviour |
| `tip` | Blue border | Suggestion to improve |
| `alert` | Red border | Immediate action needed |

---

## `to_dict()` method

```python
{
    "id": 1,
    "type": "warning",
    "title": "High Food Spending",
    "message": "You've spent 37% of your budget on Food this month...",
    "priority": 1,
    "is_read": False,
    "created_at": "2026-05-26T14:30:00"
}
```

---

## Generation Flow

When user hits "Generate Insights":
1. `ai_service.generate_insights(user)` runs
2. Old unread insights for this user are deleted
3. New AIInsight rows are inserted (3–5 typically)
4. User sees fresh cards on the insights page

See [[features/ai-insights]] and [[services#ai_service]].

---

## Related Notes

- [[models/user]] — User.ai_insights relationship
- [[features/ai-insights]] — Insights UI and generation flow
- [[services]] — ai_service.py generates and saves insights
- [[decisions#DEC-012]] — Fallback insights strategy
