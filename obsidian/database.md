---
title: Budget Buddy AI — Database
updated: 2026-05-26
---

# Database

[[home]] | [[architecture]] | [[models/user]] | [[models/expense]] | [[models/goal]] | [[models/settings]] | [[models/ai-insight]] | [[models/recurring]]

---

## Engine

- **Dev:** SQLite — `instance/budget_buddy.db`
- **Prod:** PostgreSQL (set `DATABASE_URL` in `.env`)
- **ORM:** SQLAlchemy — see [[decisions#DEC-003]]
- **Migrations:** Flask-Migrate (Alembic) — see [[decisions#DEC-010]]

---

## Entity Relationship Diagram

```
User (1) ──────────────── (1) UserSettings
  │
  ├── (1) ──── (many) Expense
  │                      │
  │              ExpenseCategory (shared, seeded)
  │                      │
  │              (many) ─┘
  │
  ├── (1) ──── (many) Goal
  │
  ├── (1) ──── (many) AIInsight
  │
  └── (1) ──── (many) RecurringExpense
```

---

## Tables

### `user`
| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `email` | String(120) UNIQUE | Login identifier |
| `username` | String(80) UNIQUE | Display name |
| `password_hash` | String(255) | PBKDF2 SHA-256 — see [[models/user]] |
| `created_at` | DateTime | |
| `is_active` | Boolean | Flask-Login |

### `user_settings`
| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `user_id` | FK → user.id | One-to-one |
| `monthly_budget` | Float | 0 = not set |
| `saving_goal_percentage` | Float | % of income to save |
| `currency` | String(10) | Default `₹` |
| `ai_insights_enabled` | Boolean | |
| `budget_alerts_enabled` | Boolean | |
| `weekly_summary_enabled` | Boolean | |

### `expense_category`
| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `name` | String(50) UNIQUE | Seeded: 8 defaults |
| `icon` | String(10) | Emoji |
| `color` | String(7) | Hex color |

Default categories seeded by `ExpenseCategory.seed_defaults()`:
Food, Transport, Shopping, Bills, Entertainment, Health, Education, Others

### `expense`
| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `user_id` | FK → user.id | |
| `category_id` | FK → expense_category.id | Nullable |
| `amount` | Float | |
| `description` | String(200) | |
| `date` | Date | |
| `is_recurring` | Boolean | Links to recurring table |
| `created_at` | DateTime | |

### `goal`
| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `user_id` | FK → user.id | |
| `name` | String(100) | |
| `target_amount` | Float | |
| `current_amount` | Float | |
| `target_date` | Date | Nullable |
| `description` | String(300) | Nullable |
| `created_at` | DateTime | |

Properties: `progress_percent`, `amount_remaining` — see [[models/goal]].

### `ai_insight`
| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `user_id` | FK → user.id | |
| `insight_type` | String(50) | `warning`/`success`/`tip`/`alert` |
| `title` | String(200) | |
| `message` | Text | |
| `priority` | Integer | 1=high, 3=low |
| `is_read` | Boolean | |
| `created_at` | DateTime | |

See [[models/ai-insight]] and [[features/ai-insights]].

### `recurring_expense`
| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | |
| `user_id` | FK → user.id | |
| `name` | String(100) | |
| `amount` | Float | |
| `category_id` | FK → expense_category.id | Nullable |
| `billing_cycle` | String(20) | `monthly`/`weekly`/`yearly` |
| `next_due_date` | Date | |
| `is_active` | Boolean | |
| `auto_add` | Boolean | Auto-create expense on due date |
| `created_at` | DateTime | |

See [[models/recurring]] and [[features/recurring-bills]].

---

## Migrations

Migration files are versioned in `migrations/versions/`.

```powershell
# Create migration after model changes
flask db migrate -m "add new field"
flask db upgrade
```

Initial migration created all tables. A second migration added `recurring_expense` after the model import issue was fixed — see [[decisions#DEC-011]].

---

## Seeded Data (`seed.py`)

| Table | Records |
|-------|---------|
| User | 1 — `test@budgetbuddy.com` / `test1234` |
| UserSettings | 1 — monthly budget ₹50,000 |
| ExpenseCategory | 8 — defaults |
| Expense | 12 — sample expenses across categories |
| Goal | 3 — Emergency Fund, Vacation to Goa, Laptop Upgrade |

---

## Related Notes

- [[models/user]] — User + UserSettings model details
- [[models/expense]] — Expense + ExpenseCategory details
- [[models/goal]] — Goal model details
- [[models/ai-insight]] — AIInsight model details
- [[models/recurring]] — RecurringExpense model details
- [[decisions#DEC-003]] — Why SQLite + PostgreSQL-ready
- [[decisions#DEC-010]] — Why Flask-Migrate
- [[decisions#DEC-011]] — Critical: model import order
