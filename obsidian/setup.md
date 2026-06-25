---
title: Budget Buddy AI — Setup Guide
updated: 2026-05-26
---

# Setup Guide

[[home]] | [[stack]] | [[architecture]]

---

## Prerequisites

- Python 3.11+ (project uses 3.14.4)
- Git
- An OpenRouter API key (free at openrouter.ai)

---

## Installation

```powershell
# 1. Clone
git clone https://github.com/saisaran70/budget-buddy-ai
cd budget-buddy-ai

# 2. Create virtual environment
python -m venv .venv

# 3. Activate (PowerShell)
.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt
# Note: if pandas fails on Python 3.14+:
pip install pandas --only-binary :all:
pip install pdfplumber --only-binary :all:
```

---

## Configuration

Create `.env` in the project root (never commit this file):

```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///budget_buddy.db
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=openai/gpt-oss-20b:free
```

See [[stack#Environment Variables]] for all options.

---

## Database Setup

```powershell
# First time only
flask db init
flask db migrate -m "initial schema"
flask db upgrade

# Seed test data (creates test@budgetbuddy.com / test1234)
python seed.py
```

Migration files are in `migrations/versions/`. See [[decisions#DEC-010]].

---

## Running the App

```powershell
python run.py
```

App is available at `http://127.0.0.1:5000`

Test credentials: `test@budgetbuddy.com` / `test1234`

---

## Project Structure

```
budget-buddy-ai/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py          # [[models/user]]
│   │   ├── expense.py       # [[models/expense]]
│   │   ├── goal.py          # [[models/goal]]
│   │   ├── settings.py      # [[models/settings]]
│   │   ├── ai_insight.py    # [[models/ai-insight]]
│   │   └── recurring.py     # [[models/recurring]]
│   ├── routes/              # Blueprint route handlers
│   │   ├── auth.py          # [[features/auth]]
│   │   ├── dashboard.py     # [[features/dashboard]]
│   │   ├── expenses.py      # [[features/expenses]]
│   │   ├── analytics.py     # [[features/analytics]]
│   │   ├── goals.py         # [[features/goals]]
│   │   ├── ai.py            # [[features/ai-insights]]
│   │   └── settings.py      # [[features/settings]]
│   ├── services/            # Business logic
│   │   ├── analytics_service.py  # [[services]]
│   │   └── ai_service.py         # [[services]]
│   ├── static/
│   │   ├── css/main.css     # Design system
│   │   └── js/main.js       # Modal + flash helpers
│   └── templates/           # Jinja2 HTML templates
├── migrations/              # Alembic migration files
├── instance/
│   └── budget_buddy.db      # SQLite database (gitignored)
├── obsidian/                # This vault
├── scripts/
│   └── update_obsidian.py   # Stop hook script
├── docs/
│   ├── prd.md               # Product requirements
│   ├── design.md            # UI/UX design spec
│   ├── database.md          # DB schema spec
│   └── build.md             # Build plan
├── config.py                # App configuration
├── run.py                   # Dev entry point
├── seed.py                  # Test data seeder
├── requirements.txt         # Python dependencies
└── .env                     # Secrets (not committed)
```

---

## Common Commands

```powershell
# Run dev server
python run.py

# Create new DB migration after model change
flask db migrate -m "description"
flask db upgrade

# Re-seed the database
python seed.py

# Open Flask shell
flask shell
```

---

## Obsidian Vault

The `obsidian/` folder is a self-contained vault. Open it in Obsidian:
1. File → Open vault → Open folder as vault
2. Select `budget-buddy-ai/obsidian/`
3. Open Graph View (Ctrl+G) to see the knowledge graph

The Stop hook at `.claude/settings.json` auto-updates [[progress]] and [[decisions]] at the end of every Claude Code session.

---

## Related Notes

- [[architecture]] — How everything connects
- [[stack]] — Technology choices
- [[database]] — Schema reference
- [[roadmap]] — What's left to build
