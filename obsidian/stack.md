---
title: Budget Buddy AI — Tech Stack
updated: 2026-05-26
---

# Tech Stack

[[home]] | [[architecture]] | [[decisions]]

---

## Backend

| Technology | Version | Role | Decision |
|-----------|---------|------|---------|
| Python | 3.14.4 | Language | — |
| Flask | latest | Web framework | [[decisions#DEC-001]] |
| SQLAlchemy | latest | ORM | [[decisions#DEC-003]] |
| Flask-Migrate | latest | DB migrations (Alembic) | [[decisions#DEC-010]] |
| Flask-Login | latest | Session auth | [[decisions#DEC-006]] |
| Flask-WTF | latest | CSRF protection | [[decisions#DEC-007]] |
| Werkzeug | (Flask dep) | Password hashing | [[decisions#DEC-006]] |
| APScheduler | latest | Cron jobs (Phase 8) | — |
| pdfplumber | latest | PDF parsing (Phase 11) | — |
| pandas | 3.0.3 | CSV parsing (Phase 11) | — |
| requests | latest | OpenRouter HTTP calls | [[decisions#DEC-004]] |
| python-dotenv | latest | `.env` loading | — |

> **Note:** pandas 3.0.3 installed with `--only-binary :all:` due to Python 3.14 wheel availability.

---

## Frontend

| Technology | How loaded | Role | Decision |
|-----------|-----------|------|---------|
| HTML5 + Jinja2 | Server-rendered | Templates | [[decisions#DEC-002]] |
| Vanilla JavaScript | `static/js/main.js` | UI interactions | [[decisions#DEC-002]] |
| CSS (custom) | `static/css/main.css` | Design system | [[decisions#DEC-008]] |
| Chart.js | CDN | Donut + line charts | [[decisions#DEC-009]] |

No npm, no build step, no bundler.

---

## Database

| Environment | DB | Config |
|------------|-----|--------|
| Development | SQLite — `instance/budget_buddy.db` | `DATABASE_URL` defaults to sqlite |
| Production | PostgreSQL | Set `DATABASE_URL=postgresql://...` in env |

See [[decisions#DEC-003]] and [[database]].

---

## AI / External APIs

| Service | Endpoint | Model | Decision |
|---------|---------|-------|---------|
| OpenRouter | `https://openrouter.ai/api/v1/chat/completions` | `openai/gpt-oss-20b:free` | [[decisions#DEC-004]] and [[decisions#DEC-005]] |

Fallback rule-based insights run when API is unavailable — see [[features/ai-insights]] and [[decisions#DEC-012]].

---

## Design System

Colors defined as CSS variables in `static/css/main.css`:

| Variable | Value | Usage |
|---------|-------|-------|
| `--bg-primary` | `#0F172A` | Page background |
| `--bg-secondary` | `#0B1120` | Sidebar background |
| `--card-bg` | `#1E293B` | Card surfaces |
| `--mint` | `#5EF2D6` | Primary accent |
| `--text-primary` | `#F1F5F9` | Main text |
| `--text-muted` | `#94A3B8` | Secondary text |
| `--danger` | `#F87171` | Error / over-budget |
| `--success` | `#34D399` | Success / on-track |
| `--warning` | `#FBBF24` | Warning / near-limit |

See [[decisions#DEC-008]].

---

## Environment Variables

Loaded from `.env` via `python-dotenv` in `config.py`:

| Variable | Required | Default | Purpose |
|---------|---------|---------|---------|
| `SECRET_KEY` | Yes | `fallback-dev-key` | Flask session signing |
| `DATABASE_URL` | No | `sqlite:///budget_buddy.db` | DB connection string |
| `OPENROUTER_API_KEY` | For AI | — | OpenRouter auth |
| `OPENROUTER_MODEL` | No | `openai/gpt-oss-20b:free` | AI model selection |
| `FLASK_ENV` | No | — | Dev/prod mode |
| `FLASK_DEBUG` | No | `0` | Debug mode |

---

## Related Notes

- [[architecture]] — How the stack fits together
- [[decisions]] — Why each choice was made
- [[setup]] — Installation and run instructions
