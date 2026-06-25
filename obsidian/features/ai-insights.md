---
title: Feature — AI Insights
updated: 2026-05-26
---

# AI Insights

[[home]] | [[routes]] | [[services]] | [[models/ai-insight]] | [[decisions#DEC-004]] | [[decisions#DEC-005]] | [[decisions#DEC-012]]

---

## What It Does

Generates personalised budget recommendations by sending the user's spending data to OpenRouter's AI API. Falls back to rule-based insights when the API is unavailable.

---

## Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ai/insights` | Insights page |
| POST | `/ai/generate` | Generate new insights |
| POST | `/ai/insights/<id>/read` | Mark as read |
| GET | `/ai/insights/data` | JSON list |

---

## Template

`app/templates/ai/insights.html`

- Insight cards with type-based styling:
  - `warning` → amber border
  - `success` → mint/green border
  - `tip` → blue border
  - `alert` → red border
- Priority badge (1 = high, 2 = medium, 3 = low)
- Mark as read button
- "Generate New Insights" button → `POST /ai/generate`

---

## AI Integration

Uses [[services#ai_service]] which calls:

```
POST https://openrouter.ai/api/v1/chat/completions
Model: openai/gpt-oss-20b:free  (configurable via OPENROUTER_MODEL in .env)
```

Required headers: `HTTP-Referer` + `X-Title` (OpenRouter requirement).

Prompt sends: monthly budget, total spent, category breakdown, active goals, recent 30 expenses.
Expects response: JSON array of `{type, title, message, priority}`.

---

## Fallback Insights (Offline Mode)

When OpenRouter fails (no key, network error, rate limit), `_fallback_insights()` runs:

1. **Budget usage warning** — if spent > 80% of monthly budget
2. **Top category alert** — if one category > 40% of spending
3. **Month-end projection** — pace-based estimate of end-of-month total

Users never see a blank insights section. See [[decisions#DEC-012]].

---

## Insight Model

[[models/ai-insight]] — type, title, message, priority (1-3), is_read, created_at.

Old unread insights are cleared when generating new ones to avoid accumulation.

---

## CSRF on AJAX

`POST /ai/generate` is called via JavaScript fetch (not a traditional form). The route uses `validate_csrf()` manually and reads the token from `X-CSRFToken` header set by the frontend.

---

## Live Test Result

OpenRouter integration tested live on 2026-05-26.
Model `openai/gpt-oss-20b:free` returned valid structured JSON insights.

---

## Related Notes

- [[services]] — `ai_service.py` implementation details
- [[models/ai-insight]] — AIInsight model
- [[features/dashboard]] — AI insight preview on dashboard
- [[decisions#DEC-004]] — Why OpenRouter
- [[decisions#DEC-005]] — Model choice
- [[decisions#DEC-012]] — Fallback strategy
