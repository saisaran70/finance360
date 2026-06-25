---
title: Budget Buddy AI — Roadmap
updated: 2026-05-26
---

# Roadmap

[[home]] | [[progress]] | [[decisions]]

---

## Completed Phases ✅

### Phase 1 — Project Setup
- Python venv, Flask app factory, config.py, .env
- SQLAlchemy models: [[models/user]], [[models/expense]], [[models/goal]], [[models/settings]], [[models/ai-insight]], [[models/recurring]]
- Flask-Migrate (Alembic) migrations
- 8 default expense categories seeded

### Phase 2 — Authentication
- Register / Login / Logout — [[features/auth]]
- Werkzeug PBKDF2 password hashing
- Flask-Login session management
- Flask-WTF CSRF protection

### Phase 3 — Dashboard
- Summary cards (budget, expenses, goals) — [[features/dashboard]]
- Category donut chart (Chart.js, AJAX)
- Recent expenses list
- AI insight preview card

### Phase 4 — Expense Tracking
- Add / Edit / Delete expenses — [[features/expenses]]
- Filter by period (3m / 6m / 1y / all)
- Category assignment
- AJAX data endpoint

### Phase 5 — Analytics
- Category breakdown with percentages — [[features/analytics]]
- 6-month spending trend line chart
- Fixed cost analysis
- All charts via Chart.js + JSON endpoints

### Phase 6 — Savings Goals
- CRUD goals — [[features/goals]]
- Progress bars and percentage display
- Target date tracking

### Phase 2.5 — Google OAuth Sign-In
- "Continue with Google" button on login + register pages
- Authlib server-side OAuth 2.0 flow — [[decisions#DEC-015]]
- Auto-register new Google users, auto-link existing accounts by email
- `google_id` column in `users` table — [[models/user]]
- [[features/auth#Google OAuth]]

### Phase 7 — AI Insights
- OpenRouter API integration — [[features/ai-insights]]
- Rule-based fallback when API unavailable
- Insight types: warning / success / tip / alert
- Mark as read functionality

---

## Upcoming Phases 🔲

### Phase 8 — Recurring Bills
- **Feature:** [[features/recurring-bills]]
- Recurring expense list with billing cycle (monthly/weekly/yearly)
- APScheduler cron: daily check → auto-create Expense when `next_due_date` reached
- UI to add/edit/toggle recurring bills
- Dashboard widget showing upcoming bills
- **Key model:** [[models/recurring]]
- **Key decision to make:** How to handle timezone for scheduler

### Phase 9 — Money Score
- Composite score 0–100 based on:
  - Budget adherence (40%)
  - Savings goal progress (30%)
  - Spending consistency (20%)
  - Category diversity (10%)
- Score trend chart (week-over-week)
- Dashboard widget
- Score explanation breakdown

### Phase 10 — Voice Expense Logging
- Web Speech API (browser-native, no extra dependency)
- User speaks: "Spent 450 on lunch today"
- JS parses → pre-fills Add Expense form
- Fallback: manual entry if browser doesn't support speech
- Mobile-first design (bottom nav mic button)

### Phase 11 — Bank Statement Import
- PDF import: `pdfplumber` (already installed)
- CSV import: `pandas` (already installed)
- Parser extracts: date, amount, description
- Smart category suggestion (keyword matching)
- Review + confirm screen before import
- Duplicate detection by date + amount

### Phase 12 — Production Deployment
- Gunicorn WSGI server
- PostgreSQL database (change `DATABASE_URL`)
- Target platform: Render or Railway (both support free tier)
- Environment variables via platform dashboard
- Static file serving (WhiteNoise or CDN)
- `Procfile`: `web: gunicorn run:app`

---

## Known Tech Debt

| Item | File | Priority |
|------|------|---------|
| APScheduler not wired up | `app/__init__.py` | High (Phase 8) |
| No pagination on expense list | `routes/expenses.py` | Medium |
| No input length validation on forms | `routes/*.py` | Medium |
| `seed.py` drops all data on re-run | `seed.py` | Low |

---

## Related Notes

- [[progress]] — What's actually been built session by session
- [[decisions]] — Architecture decisions driving build choices
- [[features/recurring-bills]] — Next feature detail
