# Budget Buddy AI — App Documentation for Test Case Generation

## Overview

Budget Buddy AI is a personal finance tracker web app built with Flask (Python). Users can log expenses, set savings/investing goals, track recurring fixed costs (subscriptions, rent), and view AI-generated financial insights. The UI is a dark-themed fintech dashboard.

**Demo credentials**
- Email: `test@budgetbuddy.com`
- Password: `test123`
- Pre-loaded with Jan–May 2026 realistic Indian expense data (₹60k–₹71k/month)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask 3.x |
| Database | SQLite (dev), PostgreSQL-ready |
| ORM | SQLAlchemy + Flask-Migrate (Alembic) |
| Auth | Flask-Login, Werkzeug password hashing |
| CSRF | Flask-WTF |
| Frontend | Jinja2 templates, vanilla JS, Chart.js |
| AI | OpenRouter API (rule-based fallback if unavailable) |

---

## Database Models

### User (`users` table)
| Field | Type | Notes |
|---|---|---|
| id | Integer PK | |
| full_name | String(100) | Required |
| email | String(150) | Unique, required |
| password_hash | Text | Werkzeug pbkdf2 |
| currency | String(10) | Default: `INR` |
| city | String(100) | Optional |
| theme_preference | String(20) | Default: `dark` |
| created_at / updated_at | DateTime | UTC |

**Relationships:** has one `UserSettings`, many `Expense`, many `Goal`, many `RecurringExpense`, many `AIInsight`.

---

### UserSettings (`user_settings` table)
| Field | Type | Notes |
|---|---|---|
| id | Integer PK | |
| user_id | FK → users | Unique (one-to-one) |
| monthly_budget | Numeric(12,2) | Total monthly income/budget |
| monthly_saving_goal | Numeric(12,2) | How much to save per month |
| monthly_investing_goal | Numeric(12,2) | How much to invest per month |
| ai_alerts_enabled | Boolean | Default True |
| notifications_enabled | Boolean | Default True |

**Business logic:** Settings are auto-created on first login/registration with budget=0. A settings row always exists for authenticated users.

---

### ExpenseCategory (`expense_categories` table)
| Field | Type | Notes |
|---|---|---|
| id | Integer PK | |
| name | String(50) | Unique |
| color | String(20) | Hex color for charts |
| icon | String(50) | Icon key for emoji mapping |

**Seeded defaults:** Food (#5EF2D6), Transport (#5BA8FF), Shopping (#F59DB1), Bills (#F7D154), Entertainment (#A78BFA), Health (#FCA5A5), Education (#60DBFF), Others (#94A3B8).

**Special category:** `Goals` (#A78BFA, icon=`target`) — created on-demand when a goal contribution is logged. Never in the seed list.

**Icon → Emoji map:** utensils→🍽️, car→🚗, shopping-bag→🛍️, receipt→⚡, film→🎬, heart→💊, book→📚, circle→📦, target→🎯.

---

### Expense (`expenses` table)
| Field | Type | Notes |
|---|---|---|
| id | Integer PK | |
| user_id | FK → users | CASCADE delete |
| category_id | FK → expense_categories | |
| amount | Numeric(12,2) | Must be > 0 |
| note | Text | Optional description |
| expense_date | Date | Defaults to today |
| is_recurring | Boolean | Default False |
| created_at / updated_at | DateTime | UTC |

**`to_dict()` returns:** id, amount (float), category name, category_color, category_icon (emoji), note, date (`YYYY-MM-DD`), date_display (`DD Mon YYYY`).

---

### RecurringExpense (`recurring_expenses` table)
| Field | Type | Notes |
|---|---|---|
| id | Integer PK | |
| user_id | FK → users | CASCADE delete |
| category_id | FK → expense_categories | |
| title | String(100) | Required |
| amount | Numeric(12,2) | Required |
| billing_cycle | String(20) | `monthly` / `yearly` / `weekly` |
| next_due_date | Date | Optional |
| auto_add | Boolean | Default False (manual tracking only) |

**Monthly equivalent calculation:**
- `monthly`: amount as-is
- `yearly`: amount ÷ 12
- `weekly`: amount × 4.33

---

### Goal (`goals` table)
| Field | Type | Notes |
|---|---|---|
| id | Integer PK | |
| user_id | FK → users | CASCADE delete |
| name | String(100) | Required |
| goal_type | String(50) | `savings` / `investment` / `emergency` / `vacation` |
| target_amount | Numeric(12,2) | Required, must be > 0 |
| current_amount | Numeric(12,2) | Default 0 |
| monthly_contribution | Numeric(12,2) | How much set aside per month |
| target_date | Date | Optional |
| status | String(20) | `active` / `completed` / `paused` |

**Computed properties:**
- `progress_percent` = `min(100, current_amount / target_amount * 100)`
- `amount_remaining` = `max(0, target_amount - current_amount)`
- `months_to_goal` = `ceil(amount_remaining / monthly_contribution)` — returns `None` if contribution ≤ 0 or goal already met

**`to_dict()` includes:** all fields + progress_percent, amount_remaining, months_to_goal.

**Auto-completion:** status set to `completed` automatically when `current_amount >= target_amount`.

---

## Routes / API Endpoints

### Auth (`/auth`)

| Method | URL | Description | Auth Required |
|---|---|---|---|
| GET | `/auth/login` | Login page | No |
| POST | `/auth/login` | Submit login | No |
| GET | `/auth/register` | Register page | No |
| POST | `/auth/register` | Create account | No |
| GET | `/auth/logout` | Logout and redirect | Yes |

**Login POST fields:** `email`, `password`, `remember` (checkbox → "on")

**Register POST fields:** `full_name`, `email`, `password`, `confirm_password`

**Register validations:**
- All fields required
- Password == confirm_password
- Password length ≥ 6 characters
- Email must not already be registered

**On register success:** creates `UserSettings` (budget=0, saving_goal=0), logs user in, redirects to `/settings`.

---

### Dashboard (`/`)

| Method | URL | Description | Auth Required |
|---|---|---|---|
| GET | `/` | Main dashboard | Yes |

**Template variables provided:**
- `summary.total_spent` — current month spending
- `summary.monthly_budget` — from settings
- `summary.remaining` — budget - total_spent
- `summary.saving_goal` — monthly saving goal
- `summary.investing_goal` — monthly investing goal
- `summary.fixed_cost_monthly` — sum of recurring expense monthly equivalents
- `summary.budget_used_pct` — `(total_spent / monthly_budget) * 100`
- `summary.month_label` — e.g. "May 2026"
- `summary.recent_expenses` — last 5 expenses as dicts
- `summary.category_breakdown` — list of `{category, color, amount, percentage, is_goal}`
- `summary.currency` — user's currency setting

**Money Score formula (0–99):**
1. Budget adherence base: `max(0, 99 - budget_used_pct)`
2. +10 if saving_goal > 0
3. +10 if investing_goal > 0
4. If fixed_cost_monthly > budget × 50%: score reduced

**Budget Allocation row** (shown only if budget > 0):
- Savings % = `saving_goal / budget * 100`
- Investing % = `investing_goal / budget * 100`
- Fixed Costs % = `fixed_cost_monthly / budget * 100`
- Free to Spend % = remainder

---

### Expenses (`/expenses`)

| Method | URL | Description | Auth Required |
|---|---|---|---|
| GET | `/expenses/` | Expense list with filters | Yes |
| POST | `/expenses/add` | Add new expense | Yes |
| POST | `/expenses/<id>/edit` | Edit expense | Yes |
| POST | `/expenses/<id>/delete` | Delete expense | Yes |
| GET | `/expenses/data` | JSON list of expenses | Yes |

**GET `/expenses/` query params:**
- `period` — `3m` (default) / `6m` / `1y` / `custom`
- `from` — start date string `YYYY-MM-DD` (used when period=custom)
- `to` — end date string `YYYY-MM-DD` (used when period=custom)

**Period → date range:**
- `3m`: last ~3 months (today minus 60 days from month start)
- `6m`: today minus 150 days
- `1y`: today minus 335 days
- `custom`: exact from/to range

**POST `/expenses/add` fields:** `amount` (float, >0), `category_id` (int), `note` (optional), `expense_date` (`YYYY-MM-DD`, defaults to today)

**POST `/expenses/<id>/edit` fields:** `amount`, `category_id`, `note`, `expense_date`

**Ownership check:** All edit/delete routes check `user_id == current_user.id`, return 404 if not found.

---

### Analytics (`/analytics`)

| Method | URL | Description | Auth Required |
|---|---|---|---|
| GET | `/analytics/` | Analytics dashboard page | Yes |
| GET | `/analytics/spending-savings` | Spending vs Savings chart data JSON | Yes |
| GET | `/analytics/ai-insights` | Latest AI insights JSON | Yes |

**GET `/analytics/spending-savings` query params:**
- `range` — `7d` / `30d` / `6m` (default) / `1y`

**Returns JSON:**
```json
{
  "labels": ["28 Apr", "29 Apr", ...],
  "spending": [1200, 0, 3500, ...],
  "savings": [800, 2000, -1500, ...]
}
```

**Savings formula:** `savings = (monthly_budget - monthly_investing_goal) - spending`
(investing allocation is treated as committed, not available as savings)

**Analytics page template variables:**
- `category_breakdown` — list with is_goal flag; Goals always included if user has goals
- `monthly_trends` — last 6 months spending totals
- `fixed_costs` — list of recurring expenses with monthly_equiv, category, color
- `projected` — `{projected: int, days_until_cycle: int}` for stat cards
- `goals` — `{total_saved, total_target, remaining, pct_funded, has_goals}`

**Category breakdown** includes a Goals row with amount=0 and `is_goal=True` even if no goal contributions logged yet (provided user has at least one goal).

---

### Goals (`/goals`)

| Method | URL | Description | Auth Required |
|---|---|---|---|
| GET | `/goals/` | Goals list page | Yes |
| POST | `/goals/add` | Create new goal | Yes |
| POST | `/goals/<id>/edit` | Edit goal | Yes |
| POST | `/goals/<id>/contribute` | Add contribution to goal | Yes |
| POST | `/goals/<id>/delete` | Delete goal | Yes |
| GET | `/goals/data` | JSON list of goals | Yes |

**POST `/goals/add` fields:**
- `name` (required, non-empty)
- `goal_type` — `savings` / `investment` / `emergency` / `vacation`
- `target_amount` (float, required, > 0)
- `current_amount` (float, optional, default 0)
- `monthly_contribution` (float, optional, default 0)
- `target_date` (`YYYY-MM-DD`, optional)

**On creation:** if `current_amount > 0`, an Expense is auto-logged under the "Goals" category (creates category if missing).

**POST `/goals/<id>/edit` fields:** same as add, plus:
- `status` — `active` / `completed` / `paused`
- `add_contribution` (float, optional) — extra amount to add to current_amount this month; also auto-logged as Expense

**Auto-completion rule:** if `current_amount >= target_amount` after any update or contribution, `status` is set to `completed`.

**POST `/goals/<id>/contribute` fields:** `amount` (float, > 0)
- Adds to `current_amount`, logs expense, auto-completes if target reached.

**Goal expense auto-logging (`_log_goal_expense`):**
- Finds or creates `ExpenseCategory(name='Goals', color='#A78BFA', icon='target')`
- Creates `Expense(user_id, category_id, amount, note=f'Savings towards: {goal_name}', expense_date=today)`
- This means goal contributions appear in the dashboard pie chart, expense list, and analytics category breakdown

---

### Settings (`/settings`)

| Method | URL | Description | Auth Required |
|---|---|---|---|
| GET | `/settings/` | Settings page (two tabs) | Yes |
| POST | `/settings/update` | Save profile & budget settings | Yes |
| POST | `/settings/fixed-costs/add` | Add recurring fixed cost | Yes |
| POST | `/settings/fixed-costs/<id>/delete` | Delete recurring fixed cost | Yes |

**GET `/settings/` query params:**
- `tab` — `profile` (default) / `fixed-costs` — persists active tab in URL

**POST `/settings/update` fields:**
- `full_name`, `currency`, `city`
- `monthly_budget`, `monthly_saving_goal`, `monthly_investing_goal` (all floats)
- `ai_alerts_enabled`, `notifications_enabled` (checkboxes → "on")

**POST `/settings/fixed-costs/add` fields:**
- `title` (required, non-empty)
- `amount` (float, > 0)
- `category_id` (int, required)
- `billing_cycle` — `monthly` / `yearly` / `weekly`
- `next_due_date` (`YYYY-MM-DD`, optional)

**Redirect after success:** Settings routes redirect back to the appropriate tab via `?tab=profile` or `?tab=fixed-costs`.

---

## Analytics Service — Business Logic

### `get_dashboard_summary(user)`
Returns current month stats. Month range: 1st to last day of current calendar month.

### `get_category_breakdown(user)`
SQL GROUP BY category for current month. Returns `[{category, color, amount, percentage, is_goal}]` sorted by amount desc. Always appends Goals row with amount=0 if user has goals but no contributions this month.

### `get_monthly_trends(user)`
Returns last 6 months of spending totals: `[{month: "Jan 2026", total: 68000.0}, ...]`

### `get_fixed_cost_analysis(user)`
Returns all RecurringExpenses for user with monthly equivalents calculated.

### `get_projected_spend(user)`
- `projected` = `(total_spent_so_far / days_elapsed) * days_in_month`
- `days_until_cycle` = days remaining until end of month

### `get_goal_analytics(user)`
Sums all **active** goals only.
- `total_saved`, `total_target`, `remaining`, `pct_funded`, `has_goals`

### `get_spending_savings_trend(user, range_key)`
- For `7d`/`30d`: per-day data. Labels like "27 May"
- For `6m`/`1y`: per-month data. Labels like "Jan 2026"
- `savings = (monthly_budget - investing_goal) - spending` per period

---

## Business Rules & Edge Cases

1. **Zero budget:** `budget_used_pct` is 0 (not division error) when budget = 0.
2. **Goals auto-complete:** `status = 'completed'` set server-side when `current_amount >= target_amount`.
3. **Currency:** Stored per user (default `INR`). Display only — no conversion logic.
4. **Negative savings:** When spending exceeds `(budget - investing_goal)`, savings values in chart go negative. This is valid/expected.
5. **Goal with no monthly_contribution:** `months_to_goal` returns `None` — displayed as "—" in UI.
6. **Expense ownership:** Every edit/delete endpoint filters by both `id` AND `user_id`, returning 404 for cross-user access attempts.
7. **Settings auto-create:** If a user somehow has no settings row, `GET /settings/` auto-creates one. Same guard in `get_dashboard_summary()`.
8. **Goals category creation:** "Goals" ExpenseCategory is created on-demand during first goal contribution. If deleted manually from DB, it is recreated on next contribution.
9. **Fixed cost vs expense:** Recurring expenses (fixed costs) are tracked separately in `recurring_expenses` table — they do NOT automatically create `Expense` rows. Fixed cost totals on dashboard come from summing `RecurringExpense.amount` monthly equivalents, not from the `Expense` table.
10. **CSRF:** All POST forms include CSRF token via Flask-WTF. Missing/invalid token returns 400.
11. **Login redirect:** Unauthenticated users accessing protected routes are redirected to `/auth/login?next=<original_url>`.
12. **Remember me:** Flask-Login session persists across browser closes when "remember me" checked.
13. **Contribute amount validation:** `amount <= 0` returns error flash, no DB change.
14. **Edit goal add_contribution:** Adding 0 or empty is a no-op — no expense logged, no amount change.

---

## URL Structure Summary

```
/                          → Dashboard
/auth/login                → Login
/auth/register             → Register
/auth/logout               → Logout
/expenses/                 → Expense list (filterable)
/expenses/add              → POST: add expense
/expenses/<id>/edit        → POST: edit expense
/expenses/<id>/delete      → POST: delete expense
/expenses/data             → GET JSON: expense list
/analytics/                → Analytics dashboard
/analytics/spending-savings → GET JSON: chart data (?range=7d|30d|6m|1y)
/analytics/ai-insights     → GET JSON: latest AI insights
/goals/                    → Goals list
/goals/add                 → POST: create goal
/goals/<id>/edit           → POST: edit goal
/goals/<id>/contribute     → POST: add contribution
/goals/<id>/delete         → POST: delete goal
/goals/data                → GET JSON: goals list
/settings/                 → Settings page (?tab=profile|fixed-costs)
/settings/update           → POST: save profile/budget settings
/settings/fixed-costs/add  → POST: add fixed cost
/settings/fixed-costs/<id>/delete → POST: delete fixed cost
```

---

## Suggested Test Case Areas for ChatGPT

1. **Auth flows:** register, login, logout, remember me, invalid credentials, duplicate email, short password
2. **Expense CRUD:** add valid/invalid, edit own/other user's, delete, filter by period, custom date range
3. **Goal lifecycle:** create, contribute, auto-complete at 100%, edit with add_contribution, ETA calculation, delete
4. **Goal expense logging:** verify Goals expense auto-created on contribution; verify it appears in category breakdown
5. **Settings:** update budget/goals, add fixed cost, delete fixed cost, tab persistence in URL
6. **Analytics calculations:** category breakdown percentages, projected spend, savings = (budget - investing) - spending
7. **Edge cases:** zero budget, zero monthly_contribution, negative savings values, no goals, no expenses this month
8. **Security:** CSRF validation, cross-user ownership (trying to edit another user's expense/goal), unauthenticated access
9. **Business rules:** Goals auto-complete trigger, fixed cost monthly equivalent calculations (yearly/weekly/monthly)
10. **API endpoints:** `/expenses/data`, `/goals/data`, `/analytics/spending-savings` with each range key
