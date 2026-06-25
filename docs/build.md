# Budget Buddy AI — Detailed Build Plan

# 1. Project Overview

## Product

Budget Buddy AI

## Product Type

AI-powered personal finance and budgeting platform.

## Build Goal

Create a scalable fintech-style web application that allows users to:

* Track expenses
* Analyze spending
* Manage budgets
* Set money goals
* Receive AI insights
* Monitor subscriptions
* Improve financial habits

---

# 2. Product Scope

## Core Modules

| Module           | Priority |
| ---------------- | -------- |
| Authentication   | High     |
| Dashboard        | High     |
| Expense Tracking | High     |
| Analytics        | High     |
| Goals            | High     |
| Settings         | Medium   |
| AI Insights      | High     |
| Notifications    | Medium   |
| Recurring Bills  | Medium   |
| Money Score      | Medium   |
| Voice Logging    | Medium   |
| Bank Statements  | Low      |

---

# 3. Tech Stack

## Frontend

| Technology     | Purpose            |
| -------------- | ------------------ |
| HTML5 + CSS3   | Structure & styles |
| Vanilla JS     | Interactivity      |
| Chart.js       | Analytics charts   |
| Web Speech API | Voice expense input|

---

## Backend

| Technology      | Purpose          |
| --------------- | ---------------- |
| Python 3.11+    | Runtime          |
| Flask           | Web framework    |
| SQLAlchemy      | ORM              |
| Flask-Migrate   | DB migrations    |
| Flask-Login     | Session auth     |
| Werkzeug        | Password hashing |

---

## Database

| Stage       | Database              |
| ----------- | --------------------- |
| Development | SQLite                |
| Production  | PostgreSQL            |

---

## AI Layer

| Technology    | Purpose                  |
| ------------- | ------------------------ |
| OpenRouter API| AI insights engine       |
| APScheduler   | Scheduled analytics jobs |

---

## File Processing

| Library    | Purpose             |
| ---------- | ------------------- |
| pdfplumber | PDF statement parse |
| pandas     | CSV import/export   |
| PyPDF2     | PDF backup parser   |

---

## Deployment

| Layer    | Platform              |
| -------- | --------------------- |
| Backend  | Railway / Render      |
| Database | PostgreSQL (Supabase) |
| Files    | Cloudinary / local    |

---

# 4. System Architecture

```text
Browser (HTML + CSS + Vanilla JS)
          ↓
Flask Routes (Blueprints)
          ↓
Service Layer (business logic)
          ↓
SQLAlchemy ORM
          ↓
SQLite (dev) / PostgreSQL (prod)
          ↓
OpenRouter AI Service
```

---

# 5. Folder Structure

```text
budget-buddy-ai/
├── app/
│   ├── __init__.py          ← Flask app factory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── expense.py
│   │   ├── goal.py
│   │   ├── settings.py
│   │   ├── ai_insight.py
│   │   └── recurring.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── expenses.py
│   │   ├── analytics.py
│   │   ├── goals.py
│   │   ├── settings.py
│   │   └── ai.py
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── analytics_service.py
│   │   └── score_service.py
│   ├── static/
│   │   ├── css/
│   │   │   └── main.css
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   ├── charts.js
│   │   │   └── voice.js
│   │   └── images/
│   └── templates/
│       ├── base.html
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       ├── dashboard/
│       │   └── index.html
│       ├── expenses/
│       │   └── index.html
│       ├── analytics/
│       │   └── index.html
│       ├── goals/
│       │   └── index.html
│       └── settings/
│           └── index.html
├── migrations/
├── tests/
├── .env
├── .gitignore
├── config.py
├── requirements.txt
└── run.py
```

---

# 6. Development Phases

| Phase    | Focus                    |
| -------- | ------------------------ |
| Phase 1  | Project setup            |
| Phase 2  | Authentication system    |
| Phase 3  | Expense management       |
| Phase 4  | Dashboard                |
| Phase 5  | Analytics engine         |
| Phase 6  | Goals system             |
| Phase 7  | AI insights engine       |
| Phase 8  | Recurring bills          |
| Phase 9  | Money score system       |
| Phase 10 | Voice expense logging    |
| Phase 11 | Bank statement import    |
| Phase 12 | Optimization + deployment|

---

# 7. PHASE 1 — PROJECT SETUP

## Goal

Create foundational architecture.

---

## Setup Commands

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1       # Windows
source .venv/bin/activate         # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db init
flask db migrate -m "initial"
flask db upgrade

# Run development server
python run.py
```

---

## requirements.txt

```text
flask
flask-sqlalchemy
flask-migrate
flask-login
flask-wtf
python-dotenv
werkzeug
requests
pdfplumber
pandas
PyPDF2
apscheduler
```

---

# 8. PHASE 2 — AUTHENTICATION SYSTEM

## Features

* User registration (name, email, password)
* User login with JWT-style sessions
* Password hashing via Werkzeug
* Protected routes via Flask-Login
* Logout

## API Routes

```text
GET  /auth/login       → Login page
POST /auth/login       → Process login
GET  /auth/register    → Register page
POST /auth/register    → Create account
GET  /auth/logout      → Logout + clear session
```

## Frontend Screens

* Login: email, password, CTA button
* Register: name, email, password, confirm password

---

# 9. PHASE 3 — EXPENSE MANAGEMENT

## Goal

Core financial tracking system.

---

## Features

* Add expense (amount, category, note, date)
* Edit expense
* Delete expense
* Expense history with filters (3M / 6M / 1Y / custom)

## Default Categories

Food · Transport · Shopping · Bills · Entertainment · Health · Education · Others

## API Routes

```text
GET    /expenses            → Expense history page
POST   /expenses/add        → Add new expense
POST   /expenses/<id>/edit  → Edit expense
POST   /expenses/<id>/delete→ Delete expense
GET    /expenses/data       → JSON for charts (AJAX)
```

## Frontend Components

| Component      | Purpose           |
| -------------- | ----------------- |
| ExpenseModal   | Add/edit form     |
| ExpenseCard    | Single row        |
| ExpenseFilters | Date range filter |
| CategoryChips  | Quick category UI |

---

# 10. PHASE 4 — DASHBOARD

## Goal

Financial overview at a glance.

---

## Dashboard Sections

| Section              | Data                              |
| -------------------- | --------------------------------- |
| Spending summary     | Total spend, budget bar, remaining|
| AI alert card        | Dynamic AI recommendation         |
| Goal cards           | Savings + investment progress     |
| Category pie chart   | Chart.js donut chart              |
| Recent expenses      | Last 5–10 transactions            |
| Prediction card      | AI month-end projection           |

## API Routes

```text
GET /dashboard           → Dashboard page
GET /dashboard/summary   → JSON summary (AJAX)
GET /dashboard/charts    → JSON chart data (AJAX)
```

---

# 11. PHASE 5 — ANALYTICS ENGINE

## Goal

Visual and AI-driven spending analytics.

---

## Features

* Category breakdown (horizontal progress bars)
* Monthly trend line chart
* Fixed cost / subscription analysis
* Spending vs budget comparison

## Category Percentage Formula

```text
Category % = (Category Spend / Total Spend) × 100
```

## API Routes

```text
GET /analytics              → Analytics page
GET /analytics/categories   → JSON category breakdown
GET /analytics/trends       → JSON monthly trend data
GET /analytics/insights     → JSON AI insights
```

---

# 12. PHASE 6 — GOALS SYSTEM

## Goal

Financial goal tracking and gamification.

---

## Features

* Create goal (name, type, target amount, current amount, target date)
* Update goal progress (add deposit)
* Goal analytics (progress %, amount left, completion rate)

## Goal Types

savings · investment · emergency · vacation

## Goal Progress Formula

```text
Goal Progress % = (Current Amount / Target Amount) × 100
```

## API Routes

```text
GET  /goals           → Goals page
POST /goals/add       → Create goal
POST /goals/<id>/edit → Update goal
POST /goals/<id>/delete → Delete goal
```

---

# 13. PHASE 7 — AI INSIGHTS ENGINE

## Goal

AI-powered financial recommendations via OpenRouter.

---

## AI Features

* Overspending warnings
* Savings suggestions
* Monthly spending predictions
* Behavioral nudges

## AI Workflow

```text
User expense data
      ↓
analytics_service.py — aggregate stats
      ↓
ai_service.py — build prompt
      ↓
OpenRouter API call (free model)
      ↓
Parse AI response
      ↓
Store in ai_insights table
      ↓
Display on Dashboard + Analytics
```

## Example Prompt Template

```text
Analyze this user's monthly spending data:
- Total budget: {budget}
- Total spent: {total_spent}
- Category breakdown: {categories}
- Previous month comparison: {prev_month}

Provide:
1. One overspending warning (if applicable)
2. One savings suggestion
3. One spending prediction for month-end
Keep each response under 2 sentences.
```

## API Routes

```text
GET  /ai/insights      → AI insights page
POST /ai/generate      → Trigger new insight generation
```

---

# 14. PHASE 8 — RECURRING BILLS SYSTEM

## Goal

Track subscriptions and fixed monthly payments.

---

## Features

* Add subscription (name, amount, billing cycle)
* Auto-add expense via APScheduler cron job
* Upcoming bill alerts

## Cron Schedule

```python
# Runs on the 1st of every month at 00:00
@scheduler.task('cron', id='auto_add_recurring', day=1, hour=0)
def auto_add_recurring_expenses():
    ...
```

## API Routes

```text
GET  /subscriptions           → Subscriptions page
POST /subscriptions/add       → Add subscription
POST /subscriptions/<id>/delete → Remove subscription
```

---

# 15. PHASE 9 — MONEY SCORE SYSTEM

## Goal

Gamified financial health score (0–100).

---

## Score Factors

| Factor               | Weight |
| -------------------- | ------ |
| Staying under budget | 30%    |
| Savings consistency  | 25%    |
| Goal progress        | 20%    |
| Subscription control | 10%    |
| Spending stability   | 15%    |

## Score Formula

```text
Money Score = (0.30 × B + 0.25 × S + 0.20 × G + 0.10 × R + 0.15 × T) × 100

Where:
  B = Budget discipline   (1.0 if under budget, scales down)
  S = Savings score       (savings / saving_goal)
  G = Goal progress       (avg goal completion %)
  R = Recurring control   (1.0 if < 30% of budget on subscriptions)
  T = Trend stability     (1.0 if spend variance is low)
```

---

# 16. PHASE 10 — VOICE EXPENSE LOGGING

## Goal

Let users speak expenses naturally.

---

## Examples

* "I spent 250 on lunch"
* "Add 500 for fuel"
* "Spent 1200 shopping yesterday"

## Tech

* Web Speech API (browser-native, no cost)
* Regex/NLP parser to extract amount, category, note, date
* Confirmation modal before saving

## UI

* Floating mic button (bottom-right)
* Animated listening indicator
* Transcription preview text
* Confirm / Edit / Cancel popup

---

# 17. PHASE 11 — BANK STATEMENT IMPORT

## Goal

Import expenses from PDF or CSV bank statements.

---

## Features

* Upload PDF (pdfplumber to extract text)
* Upload CSV (pandas to parse rows)
* AI categorization of transactions
* Duplicate detection
* Review screen before saving

## API Routes

```text
GET  /import           → Import page
POST /import/upload    → Handle file upload
POST /import/confirm   → Save approved transactions
```

---

# 18. SECURITY PLAN

## Must Implement

| Security Feature    | Implementation              |
| ------------------- | --------------------------- |
| Password hashing    | Werkzeug pbkdf2             |
| Session management  | Flask-Login + secure cookie |
| CSRF protection     | Flask-WTF                   |
| Input validation    | WTForms validators          |
| SQL injection       | SQLAlchemy ORM (safe)       |
| File upload safety  | Allowed extensions check    |
| Rate limiting       | Flask-Limiter (optional)    |

---

# 19. RESPONSIVE DESIGN PLAN

## Desktop

* Left sidebar fixed
* Multi-column card grid

## Tablet

* Collapsible sidebar
* 2-column layout

## Mobile

* Bottom navigation bar
* Single-column cards
* Simplified charts

---

# 20. PERFORMANCE OPTIMIZATION

## Frontend

* Lazy load Chart.js only on analytics pages
* AJAX for dashboard data (no full page reload)
* CSS transitions instead of JS animations

## Backend

* SQLAlchemy indexed queries
* Precomputed monthly_analytics table
* Cache dashboard summary in session

---

# 21. TESTING PLAN

| Layer    | Tool     | Purpose              |
| -------- | -------- | -------------------- |
| Backend  | pytest   | Unit + API testing   |
| Frontend | Manual   | UI interaction tests |

---

# 22. DEPLOYMENT PLAN

## Environment Variables (.env)

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///budget_buddy.db
OPENROUTER_API_KEY=your-openrouter-key
```

## Production

```env
FLASK_ENV=production
DATABASE_URL=postgresql://...
```

## Deploy Commands

```bash
# Railway / Render
pip install gunicorn
gunicorn run:app
```

---

# 23. BUILD TIMELINE

| Week   | Deliverable                     |
| ------ | ------------------------------- |
| Week 1 | Setup + Auth                    |
| Week 2 | Expense tracking + Dashboard    |
| Week 3 | Analytics + Goals               |
| Week 4 | AI Insights + Recurring bills   |
| Week 5 | Voice logging + Money score     |
| Week 6 | Bank import + Optimization      |
| Week 7 | Testing + Deployment            |

---

# 24. MVP PRIORITY FEATURES

## Must Have

- Authentication
- Add / edit / delete expense
- Dashboard overview
- Category analytics (Chart.js)
- Budget tracking
- AI insights (OpenRouter)
- Goal tracking

## Nice to Have

- Notifications
- Money score
- Recurring bills
- Voice expense logging
- Bank statement import

---

# 25. Final Build Summary

Budget Buddy AI is built as:

* Python Flask full-stack web app
* SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)
* Vanilla JS + Chart.js frontend (no framework overhead)
* OpenRouter AI for financial insights
* Modular Blueprint architecture for maintainability
