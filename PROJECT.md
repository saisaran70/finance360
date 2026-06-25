# Budget Buddy AI — Complete Project Reference

> AI-powered personal finance tracker. Dark fintech UI. Built for Indian users.  
> Stack: Python + Flask + SQLite + OpenRouter AI  
> Live at: `http://127.0.0.1:5000` | Entry point: `python run.py`

---

## Table of Contents

1. [What This App Is](#1-what-this-app-is)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [Features — Detailed Breakdown](#4-features--detailed-breakdown)
   - [Authentication](#41-authentication)
   - [Dashboard](#42-dashboard)
   - [Expense Tracking](#43-expense-tracking)
   - [Analytics](#44-analytics)
   - [Savings Goals](#45-savings-goals)
   - [AI Insights](#46-ai-insights)
   - [Recurring Bills / Fixed Costs](#47-recurring-bills--fixed-costs)
   - [Settings](#48-settings)
5. [Database Models](#5-database-models)
6. [API Endpoints (All Routes)](#6-api-endpoints-all-routes)
7. [Services Layer](#7-services-layer)
8. [Frontend & UI](#8-frontend--ui)
9. [Configuration & Environment](#9-configuration--environment)
10. [Setup & Seeding](#10-setup--seeding)
11. [Test Suite](#11-test-suite)
12. [Data Flow Diagrams](#12-data-flow-diagrams)

---

## 1. What This App Is

**Budget Buddy AI** is a full-stack personal finance management web application. It lets users:

- Log and categorise every rupee they spend
- Track savings goals with progress bars and contribution history
- View spending analytics — donut charts, 6-month trends, spending vs savings
- Get AI-generated financial insights (warnings, suggestions, predictions) powered by OpenRouter
- Manage fixed monthly costs (rent, subscriptions, EMIs) separately from variable spending
- Sign in with email/password **or** Google OAuth

The app is intentionally designed for **Indian users** — default currency is INR, demo data uses Indian merchants (BigBasket, Zomato, Myntra, Ola, Swiggy), and amounts reflect Indian income/expense ranges.

---

## 2. Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Web Framework | Flask | 3.1.0 |
| ORM | Flask-SQLAlchemy | 3.1.1 |
| Migrations | Flask-Migrate (Alembic) | 4.0.7 |
| Auth | Flask-Login + Werkzeug PBKDF2 | 0.6.3 / 3.1.3 |
| OAuth | Authlib | 1.3.2 |
| CSRF | Flask-WTF | 1.2.2 |
| Database | SQLite (dev) / PostgreSQL-ready | — |
| Templates | Jinja2 | (bundled with Flask) |
| Charts | Chart.js | CDN |
| AI | OpenRouter API | `openai/gpt-oss-20b:free` |
| HTTP client | requests | 2.32.3 |
| PDF parsing | pdfplumber + PyPDF2 | 0.11.4 / 3.0.1 |
| Data analysis | pandas | 2.2.3 |
| Task scheduling | APScheduler | 3.10.4 |
| Config | python-dotenv | 1.0.1 |

**Design:** Custom dark fintech CSS — `#0F172A` background, `#1E293B` cards, `#5EF2D6` mint accent colour.

---

## 3. Project Structure

```
budget-buddy-ai/
│
├── run.py                    # Entry point — starts Flask dev server on port 5000
├── config.py                 # DevelopmentConfig / ProductionConfig, reads .env
├── setup_db.py               # Auto-setup: runs migrations, seeds categories + demo user
├── seed.py                   # Legacy seeder (12 expenses, 3 goals)
├── demo_data.py              # Realistic 6-month Indian expense data (Jan–Jun 2026)
├── requirements.txt          # All Python dependencies
├── .env                      # Secrets: API keys, DB URL, Google OAuth creds
│
├── app/
│   ├── __init__.py           # Flask app factory — registers extensions + blueprints
│   │
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── user.py           # User (auth, profile, OAuth)
│   │   ├── expense.py        # Expense + ExpenseCategory
│   │   ├── goal.py           # Goal (savings/investment/vacation)
│   │   ├── settings.py       # UserSettings (budget, saving/investing goals, toggles)
│   │   ├── ai_insight.py     # AIInsight (stored AI-generated alerts)
│   │   └── recurring.py      # RecurringExpense (fixed bills)
│   │
│   ├── routes/               # Flask blueprints
│   │   ├── auth.py           # Login, register, logout, Google OAuth
│   │   ├── dashboard.py      # Home page + summary/chart JSON APIs
│   │   ├── expenses.py       # Expense CRUD + filter
│   │   ├── analytics.py      # Charts, trends, fixed-cost breakdown
│   │   ├── goals.py          # Goal CRUD + contributions
│   │   ├── settings.py       # Profile, budget config, recurring bills management
│   │   └── ai.py             # AI insight generation + display
│   │
│   ├── services/             # Business logic (no Flask context assumed)
│   │   ├── analytics_service.py  # All data aggregation and computation
│   │   └── ai_service.py         # OpenRouter API integration + fallback
│   │
│   ├── static/
│   │   ├── css/main.css      # All styles (dark theme, responsive)
│   │   └── js/main.js        # Client-side interactivity
│   │
│   └── templates/
│       ├── base.html         # Layout: sidebar + bottom nav + flash messages
│       ├── auth/             # login.html, register.html
│       ├── dashboard/        # index.html
│       ├── expenses/         # index.html
│       ├── analytics/        # index.html
│       ├── goals/            # index.html
│       ├── settings/         # index.html
│       └── ai/               # insights.html
│
├── migrations/               # Alembic migration history
│   └── versions/
│       ├── fd00d10ec326_initial_schema.py
│       ├── ec299781169f_add_google_oauth.py
│       ├── 6253db890ead_add_recurring_expenses.py
│       ├── 13cd86524e84_add_monthly_contribution_to_goals.py
│       └── 0a8ad919d283_add_monthly_investing_goal_to_settings.py
│
├── tests/                    # pytest suite (10 files)
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_dashboard.py
│   ├── test_expenses.py
│   ├── test_analytics.py
│   ├── test_goals.py
│   ├── test_settings.py
│   ├── test_api.py
│   ├── test_edge_cases.py
│   └── test_security.py
│
├── obsidian/                 # Obsidian knowledge graph vault (24 notes, 272 wikilinks)
└── scripts/
    └── update_obsidian.py    # Stop hook: auto-updates the Obsidian vault on Claude stop
```

---

## 4. Features — Detailed Breakdown

### 4.1 Authentication

**Routes:** `/auth/`

Two sign-in methods:

**Email / Password**
- Register with full name, email, password (min 6 chars)
- Passwords hashed with Werkzeug PBKDF2 (never stored in plain text)
- Login with "remember me" option (30-day session)
- CSRF protection on all forms via Flask-WTF

**Google OAuth**
- One-click sign in via Google
- Implemented with Authlib OAuth2 client
- On first login: auto-creates a User record (`password_hash = 'OAUTH:google'`, `google_id` stored)
- On subsequent logins: looks up by `google_id` or falls back to email match
- `is_oauth_user` property on User distinguishes OAuth-only accounts

**On registration**, the app automatically creates:
- A `UserSettings` record (defaults: `monthly_budget = 50000`, `monthly_saving_goal = 10000`)
- All expense categories are shared (seeded globally, not per-user)

---

### 4.2 Dashboard

**Route:** `/` and `/dashboard`

The home screen. Loads on every login. Shows a complete monthly snapshot.

**What's on the Dashboard:**

| Card | Data Shown |
|---|---|
| Monthly Budget Hero | Total spent, budget remaining, % used, progress bar |
| Fixed Costs | Sum of all recurring bills (monthly equivalent) |
| Savings Goal | Monthly saving target from settings |
| Investing Goal | Monthly investing target from settings |
| Category Donut Chart | Spending breakdown by category for current month |
| Recent Expenses | Last 5 transactions with category icon + amount |
| Monthly Trends Bar Chart | Total spending for last 6 months |

**JSON APIs served by this module:**
- `GET /dashboard/summary` — full summary object
- `GET /dashboard/charts` — category breakdown + 6-month trends combined

**How it calculates "current month":** date range `first day of month → last day of month`, computed dynamically each request (no caching).

---

### 4.3 Expense Tracking

**Route:** `/expenses/`

Full CRUD for individual expense entries.

**Adding an Expense:**
- Fields: Amount (₹), Category (dropdown), Note (optional text), Date (defaults to today)
- Category options: Food, Transport, Shopping, Bills, Entertainment, Health, Education, Others, Goals
- Each category has a colour (hex) and icon (emoji mapping)
- Validates: amount must be > 0, date must parse as `YYYY-MM-DD`

**Editing an Expense:**
- Inline edit form (same fields)
- Only the owner can edit (filtered by `user_id`)

**Deleting an Expense:**
- POST to `/<id>/delete` — owner-only, immediate

**Filtering / Viewing:**
- Default view: last 3 months
- Period options: `3m`, `6m`, `1y`, `all`, or `custom` (pick date range)
- Custom range: pick `from` and `to` dates via query params
- Results ordered by `expense_date DESC`

**Expense Categories (seeded globally):**

| Name | Colour | Icon |
|---|---|---|
| Food | `#EF4444` | 🍽️ |
| Transport | `#F59E0B` | 🚗 |
| Shopping | `#8B5CF6` | 🛍️ |
| Bills | `#3B82F6` | ⚡ |
| Entertainment | `#EC4899` | 🎬 |
| Health | `#10B981` | 🏥 |
| Education | `#06B6D4` | 📚 |
| Others | `#6B7280` | 📦 |
| Goals | `#5EF2D6` | 🎯 |

---

### 4.4 Analytics

**Route:** `/analytics/`

Deep-dive spending analysis page with 5 data views.

**1. Category Breakdown**
- Doughnut/pie chart + table
- Shows category name, total amount, % of spend for current month
- Ordered by highest spend first
- "Goals" category always present if user has any goals

**2. Monthly Trends**
- Bar chart of total spending across the last 6 months
- Month labels + amounts

**3. Spending vs Savings Trend**
- Line chart comparing spending vs savings over time
- Range options: `7d` (daily), `30d` (daily), `6m` (monthly), `1y` (monthly)
- Savings = `monthly_budget − investing_goal − daily_spend`

**4. Fixed Costs Analysis**
- Lists all recurring bills with their monthly-equivalent cost
- Billing cycle normalisation: yearly ÷ 12, weekly × 4.33, monthly = as-is
- Shows next due date per item

**5. Projected Month-End Spend**
- Extrapolates current pace: `spent_so_far ÷ days_elapsed × days_in_month`
- Shows days remaining in the billing cycle

**6. Goal Analytics Summary**
- Total saved across all active goals
- Total target across all active goals
- Overall % funded

---

### 4.5 Savings Goals

**Route:** `/goals/`

Track multiple savings/investment goals with progress and contribution history.

**Goal Types:** `savings`, `investment`, `emergency`, `vacation`

**Creating a Goal:**
- Fields: Name, Type, Target Amount, Current Amount (starting point), Monthly Contribution, Target Date
- Status starts as `active`

**Tracking Progress:**
- `progress_percent` = `current_amount / target_amount × 100`
- `amount_remaining` = `target_amount − current_amount`
- `months_to_goal` = `amount_remaining / monthly_contribution` (if contribution > 0)
- Auto-completes: status set to `completed` when `current_amount ≥ target_amount`

**Contributing to a Goal:**
- `POST /goals/<id>/contribute` — adds amount to `current_amount`
- Simultaneously logs a `Goals` category expense so it shows up in spending analytics
- This keeps the dashboard totals accurate (goals spending counts toward monthly total)

**Editing a Goal:** update any field, re-checks completion status on save.

**Deleting a Goal:** removes the goal record only (linked expense entries remain).

---

### 4.6 AI Insights

**Route:** `/ai/insights`

AI-generated financial analysis triggered on demand.

**How It Works:**

1. User clicks "Generate Insights"
2. App collects: current month summary (budget, spent, remaining, category breakdown) + 6-month trend
3. Builds a structured prompt and POSTs to `https://openrouter.ai/api/v1/chat/completions`
4. Model (`openai/gpt-oss-20b:free`, configurable): returns exactly 3 insights as JSON
5. Insights saved to `AIInsight` table and displayed

**Insight Types:**
- `warning` — budget alerts, overspending flags (priority: high)
- `suggestion` — actionable recommendations (priority: medium)
- `prediction` — month-end projections (priority: low)

**Fallback (no API key / API failure):**  
Rule-based insights generated locally:
- Budget alert if >90% of monthly budget used
- Top-category observation
- Month-end projection (linear extrapolation)

**Insights are persistent** — stored in DB, can be marked as read. History visible on the insights page.

---

### 4.7 Recurring Bills / Fixed Costs

**Model exists, UI exists in Settings. APScheduler auto-logging not wired yet.**

Users can manage a list of fixed monthly costs:

**Fields per recurring expense:**
- Title (e.g. "Netflix", "Rent")
- Amount
- Billing Cycle: `monthly`, `yearly`, `weekly`
- Category (linked to ExpenseCategory)
- Next Due Date
- Auto-add flag (for future APScheduler automation)

**Where it shows up:**
- Dashboard "Fixed Costs" card (summed monthly equivalent)
- Analytics "Fixed Costs" breakdown list
- Settings page (add/delete recurring items)

**Currently:** Users add/remove these manually. Auto-adding them as expenses on due date (via APScheduler) is planned but not yet implemented.

---

### 4.8 Settings

**Route:** `/settings/`

Three sections on one page:

**Profile Settings**
- Full name, email, city, currency (default: INR)
- Theme preference (stored, dark mode default)

**Budget & Goals Configuration**
- Monthly Budget (how much you plan to spend)
- Monthly Saving Goal (how much you aim to save)
- Monthly Investing Goal (SIP / stocks allocation)
- These 3 numbers feed all dashboard cards and analytics

**Toggle Preferences**
- AI Alerts enabled/disabled
- Notifications enabled/disabled

**Fixed Costs Management**
- Add new recurring expense (title, amount, cycle, category, due date)
- Delete existing recurring expenses
- Same data as the Analytics fixed-costs view

---

## 5. Database Models

### User

```
id              INT  PK
full_name       VARCHAR(120)
email           VARCHAR(120)  UNIQUE
password_hash   VARCHAR(256)  — 'OAUTH:google' for OAuth-only accounts
google_id       VARCHAR(100)  UNIQUE NULLABLE
currency        VARCHAR(10)   default 'INR'
city            VARCHAR(100)
theme_preference VARCHAR(20)  default 'dark'
created_at      DATETIME
updated_at      DATETIME
```
Relationships: `expenses`, `goals`, `settings` (1:1), `ai_insights`, `recurring_expenses`

---

### Expense

```
id           INT  PK
user_id      INT  FK → User
category_id  INT  FK → ExpenseCategory
amount       NUMERIC(12,2)
note         VARCHAR(255)
expense_date DATE
is_recurring BOOL  default False
created_at   DATETIME
updated_at   DATETIME
```

---

### ExpenseCategory

```
id     INT  PK
name   VARCHAR(50)   UNIQUE
color  VARCHAR(7)    hex e.g. '#EF4444'
icon   VARCHAR(50)   e.g. 'utensils', 'car'
```
9 categories seeded at setup (see Section 4.3).

---

### Goal

```
id                   INT  PK
user_id              INT  FK → User
name                 VARCHAR(120)
goal_type            VARCHAR(30)   savings/investment/emergency/vacation
target_amount        NUMERIC(12,2)
current_amount       NUMERIC(12,2)  default 0
monthly_contribution NUMERIC(12,2)  default 0
target_date          DATE
status               VARCHAR(20)   active/completed/paused
created_at           DATETIME
updated_at           DATETIME
```
Computed properties: `progress_percent`, `amount_remaining`, `months_to_goal`

---

### UserSettings

```
id                    INT  PK
user_id               INT  FK → User  UNIQUE (1:1)
monthly_budget        NUMERIC(12,2)  default 50000
monthly_saving_goal   NUMERIC(12,2)  default 10000
monthly_investing_goal NUMERIC(12,2) default 0
ai_alerts_enabled     BOOL  default True
notifications_enabled BOOL  default True
```

---

### AIInsight

```
id           INT  PK
user_id      INT  FK → User
insight_type VARCHAR(20)   warning/suggestion/prediction/saving
title        VARCHAR(120)
message      TEXT
priority     VARCHAR(10)   low/medium/high
is_read      BOOL  default False
generated_at DATETIME
```

---

### RecurringExpense

```
id            INT  PK
user_id       INT  FK → User
category_id   INT  FK → ExpenseCategory
title         VARCHAR(120)
amount        NUMERIC(12,2)
billing_cycle VARCHAR(20)   monthly/yearly/weekly
next_due_date DATE
auto_add      BOOL  default False
```

---

### Relationships at a Glance

```
User (1) ─────────────────── (∞) Expense
   │                                │
   │                                └── (∞:1) ExpenseCategory
   │
   ├── (1:1) UserSettings
   │
   ├── (1) ─── (∞) Goal
   │
   ├── (1) ─── (∞) AIInsight
   │
   └── (1) ─── (∞) RecurringExpense
                        │
                        └── (∞:1) ExpenseCategory
```

All user relationships have `cascade='all, delete-orphan'` — deleting a user wipes all their data cleanly.

---

## 6. API Endpoints (All Routes)

### Auth — `/auth/`

| Method | URL | Description |
|---|---|---|
| GET | `/auth/login` | Login page |
| POST | `/auth/login` | Submit login (email + password) |
| GET | `/auth/register` | Register page |
| POST | `/auth/register` | Submit registration |
| GET | `/auth/google` | Initiate Google OAuth |
| GET | `/auth/google/callback` | OAuth callback handler |
| POST | `/auth/logout` | Log out current user |

---

### Dashboard — `/`

| Method | URL | Description |
|---|---|---|
| GET | `/` or `/dashboard` | Main dashboard page |
| GET | `/dashboard/summary` | JSON: full month summary |
| GET | `/dashboard/charts` | JSON: category breakdown + 6-month trends |

---

### Expenses — `/expenses/`

| Method | URL | Description |
|---|---|---|
| GET | `/expenses/` | Expense list page (filterable) |
| POST | `/expenses/add` | Add new expense |
| POST | `/expenses/<id>/edit` | Edit existing expense |
| POST | `/expenses/<id>/delete` | Delete expense |
| GET | `/expenses/data` | JSON: filtered expense list |

Query params for `/expenses/`: `period` (3m/6m/1y/all/custom), `from`, `to`

---

### Analytics — `/analytics/`

| Method | URL | Description |
|---|---|---|
| GET | `/analytics/` | Analytics page |
| GET | `/analytics/categories` | JSON: category breakdown (current month) |
| GET | `/analytics/trends` | JSON: 6-month monthly totals |
| GET | `/analytics/fixed-costs` | JSON: recurring expenses list |
| GET | `/analytics/spending-savings` | JSON: spending vs savings trend |
| GET | `/analytics/ai-insights` | JSON: last 4 AI insights |

Query param for `/analytics/spending-savings`: `range` (7d/30d/6m/1y)

---

### Goals — `/goals/`

| Method | URL | Description |
|---|---|---|
| GET | `/goals/` | Goals list page |
| POST | `/goals/add` | Create goal |
| POST | `/goals/<id>/edit` | Update goal |
| POST | `/goals/<id>/contribute` | Add funds to goal |
| POST | `/goals/<id>/delete` | Delete goal |
| GET | `/goals/data` | JSON: all goals |

---

### Settings — `/settings/`

| Method | URL | Description |
|---|---|---|
| GET | `/settings/` | Settings page |
| POST | `/settings/update` | Save profile + budget settings |
| POST | `/settings/fixed-costs/add` | Add recurring expense |
| POST | `/settings/fixed-costs/<id>/delete` | Delete recurring expense |

---

### AI — `/ai/`

| Method | URL | Description |
|---|---|---|
| GET | `/ai/insights` | AI insights page |
| POST | `/ai/generate` | Generate new insights via OpenRouter |
| GET | `/ai/insights/data` | JSON: recent insights list |
| POST | `/ai/insights/<id>/read` | Mark insight as read |

---

## 7. Services Layer

### `analytics_service.py`

Pure computation functions — no Flask request context assumed (can be tested standalone).

| Function | Returns |
|---|---|
| `get_dashboard_summary(user)` | Dict with total_spent, remaining, budget_used_pct, fixed_cost_monthly, saving_goal, investing_goal, recent_expenses, category_breakdown, currency |
| `get_category_breakdown(user)` | List of `{category, color, amount, percentage, is_goal}` for current month |
| `get_monthly_trends(user)` | List of `{month, total}` for last 6 months |
| `get_fixed_cost_analysis(user)` | List of `{title, amount, monthly_equiv, billing_cycle, next_due_date, category, color}` |
| `get_projected_spend(user)` | `{projected, days_until_cycle}` — linear extrapolation |
| `get_goal_analytics(user)` | `{total_saved, total_target, remaining, pct_funded, has_goals}` |
| `get_spending_savings_trend(user, range_key)` | `{labels, spending, savings}` arrays for chart |
| `get_chart_data(user)` | Combined `{category_breakdown, monthly_trends}` |

**Note:** Monthly range (`first → last day`) is calculated fresh each call via `_current_month_range()`.

---

### `ai_service.py`

Handles all AI insight generation.

**`generate_insights(user)`** — main entry point:
1. Collects dashboard summary + 6-month trends
2. Builds prompt asking for exactly 3 JSON insights (warning / suggestion / prediction)
3. Calls OpenRouter: `POST https://openrouter.ai/api/v1/chat/completions`
   - Model: configurable via `OPENROUTER_MODEL` env var
   - `max_tokens: 600`, `temperature: 0.4`
   - Strips markdown code fences if model wraps JSON
4. Saves parsed insights to DB
5. Falls back to rule-based insights on any error

**Fallback logic (`_fallback_insights`):**
- Warning if >90% budget used
- Suggestion about top spending category
- Prediction via linear extrapolation of current month

---

## 8. Frontend & UI

### Layout

`base.html` provides the app shell:
- **Desktop sidebar** (left): Logo, 6 nav links, user avatar + name + email, sign-out button
- **Mobile bottom nav**: 5 icons (Home, Add, Analytics, Goals, AI)
- **Mobile hamburger**: Reveals the sidebar as an overlay panel
- **Flash messages**: Dismissible alerts for success/error/info (auto-dismiss on click)
- **Content area**: `{% block content %}` filled by each page template

### Navigation Links

| Label | Route |
|---|---|
| Dashboard | `/` |
| Expenses | `/expenses/` |
| Analytics | `/analytics/` |
| Goals | `/goals/` |
| AI Insights | `/ai/insights` |
| Settings | `/settings/` |

Active link is highlighted via `request.endpoint` check in the template.

### Charts

All charts use **Chart.js** loaded from CDN. Types used:
- Doughnut chart — category breakdown
- Bar chart — monthly trends
- Line chart — spending vs savings trend

Data fetched via `fetch()` calls to the JSON API endpoints after page load.

### Theme

Single dark theme throughout — `#0F172A` body, `#1E293B` card backgrounds, `#5EF2D6` mint accent for highlights and CTAs. Custom CSS in `app/static/css/main.css`. No CSS framework (no Bootstrap/Tailwind).

---

## 9. Configuration & Environment

### `.env` File

```
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=<random secret — change in production>
DATABASE_URL=sqlite:///budget_buddy.db
GOOGLE_CLIENT_ID=<your Google OAuth client ID>
GOOGLE_CLIENT_SECRET=<your Google OAuth client secret>
OPENROUTER_API_KEY=<your OpenRouter API key>
OPENROUTER_MODEL=openai/gpt-oss-20b:free
```

### `config.py`

- `Config` (base): Reads all `.env` values, sets `SQLALCHEMY_DATABASE_URI`, `MAX_CONTENT_LENGTH = 16MB`
- `DevelopmentConfig`: `DEBUG = True`
- `ProductionConfig`: `DEBUG = False`

Switching to PostgreSQL: just change `DATABASE_URL` to a `postgresql://` URI — SQLAlchemy handles the rest.

---

## 10. Setup & Seeding

### First-time setup

```bash
pip install -r requirements.txt
cp .env.example .env        # fill in your keys
python run.py               # setup_db.py runs automatically on startup
```

`setup_db.py` does on every startup:
1. Checks if tables exist; runs `flask db upgrade` if missing
2. Seeds 9 expense categories (if not already present)
3. Creates demo user `test@budgetbuddy.com` / `test1234` (if missing)
4. Seeds 5 months of realistic demo expenses (Jan–May 2026)
5. Creates 3 demo goals: Emergency Fund, Goa Vacation, Stock Portfolio
6. Creates 8 demo recurring expenses: Rent, Phone, Internet, Netflix, Hotstar, Spotify, Gym, Electricity

### `demo_data.py`

More detailed seeding for testing/demos:
- Clears existing data for the test user
- Seeds 6 months (Jan–Jun 2026) of realistic Indian expenses
- Uses real merchant names: BigBasket, Zomato, Myntra, Amazon, Ola, Swiggy, etc.
- Monthly totals range ₹57,000–₹71,000
- Includes Holi festival spike in March

Run manually: `python demo_data.py`

---

## 11. Test Suite

10 pytest test files in `tests/`:

| File | Coverage |
|---|---|
| `test_auth.py` | Register, login, logout, duplicate email, wrong password |
| `test_dashboard.py` | Dashboard renders, summary JSON, chart JSON |
| `test_expenses.py` | Add/edit/delete expenses, filtering, validation |
| `test_analytics.py` | Category breakdown, trends, fixed costs, projections |
| `test_goals.py` | Create/edit/delete goals, contributions, auto-complete |
| `test_settings.py` | Profile update, budget config, recurring CRUD |
| `test_api.py` | All JSON API endpoints |
| `test_edge_cases.py` | Empty state, zero amounts, boundary conditions |
| `test_security.py` | Auth required on all routes, CSRF, user isolation |
| `conftest.py` | Test app factory, fixtures, test user setup |

Run tests: `pytest tests/`

---

## 12. Data Flow Diagrams

### Authentication Flow

```
POST /auth/register
  → Validate email uniqueness + password length
  → Hash password (PBKDF2)
  → Create User record
  → Create UserSettings record (defaults)
  → Login user → redirect to Dashboard

GET /auth/google
  → Redirect to Google consent screen

GET /auth/google/callback
  → Exchange code for token
  → Fetch Google user info (email, name, google_id)
  → If google_id exists in DB → login existing user
  → Else if email exists → link google_id to existing user
  → Else → create new User (password_hash = 'OAUTH:google')
  → Create UserSettings if missing
  → Login user → redirect to Dashboard
```

### Expense Tracking Flow

```
POST /expenses/add
  → Parse: amount, category_id, note, expense_date
  → Validate amount > 0
  → Insert Expense record (user_id = current_user.id)
  → Redirect back

GET /dashboard
  → analytics_service.get_dashboard_summary(user)
     → SUM(amount) WHERE user_id + current month range
     → GROUP BY category for breakdown
     → Last 5 expenses
  → Render template with summary dict
```

### Goal Contribution Flow

```
POST /goals/<id>/contribute
  → Load Goal (owner check)
  → Add amount to goal.current_amount
  → If current_amount >= target_amount → set status = 'completed'
  → Also insert Expense(category='Goals', amount=amount)
     so it appears in monthly spending totals
  → Commit + redirect
```

### AI Insight Generation Flow

```
POST /ai/generate
  → get_dashboard_summary(user)   ← current month data
  → get_monthly_trends(user)      ← 6-month history
  → Build prompt string
  → POST to OpenRouter API (20s timeout)
     ┌─ Success → parse JSON array of 3 insights
     └─ Failure → _fallback_insights() → rule-based 3 insights
  → INSERT 3 AIInsight records
  → Redirect to /ai/insights
```

---

*Document reflects project state as of 2026-06-24.*
