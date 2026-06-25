---
title: Finance360 — Home
updated: 2026-06-25
---

# Finance360

> AI-powered Organizational Financial Management Platform.
> Built on the BudgetBuddy AI base. Python + Flask + SQLAlchemy + SQLite → PostgreSQL.
> Branch: `finance360` | Base: `main` (BudgetBuddy AI v1)

---

## Quick Navigation

### Project
- [[architecture]] — System design and layer overview
- [[stack]] — Tech stack choices and why
- [[setup]] — How to run the project locally
- [[roadmap]] — Finance360 build phases
- [[decisions]] — All architectural decisions
- [[progress]] — Session-by-session build log
- [[database]] — Schema, relationships, migrations

### Modules (Finance360)
- [[features/dashboard]] — Executive dashboard, KPI cards, charts
- [[features/revenue]] — Revenue management, invoices, payments
- [[features/expenses]] — Business expense management
- [[features/budgets]] — Budget planning and tracking
- [[features/departments]] — Department financials
- [[features/vendors]] — Vendor management
- [[features/customers]] — Customer management
- [[features/assets]] — Asset tracking and depreciation
- [[features/liabilities]] — Liability management
- [[features/payroll]] — Payroll management
- [[features/reports]] — Financial reports (P&L, Balance Sheet, etc.)
- [[features/ai-insights]] — AI Financial Advisor

### Data Models
- [[models/user]] — User + roles (Super Admin, CEO, CFO, etc.)
- [[models/organization]] — Organization + branches
- [[models/department]] — Department with budget allocation
- [[models/employee]] — Employee records
- [[models/vendor]] — Vendor profiles
- [[models/customer]] — Customer database
- [[models/revenue]] — Revenue + invoices
- [[models/expense]] — Business expenses
- [[models/budget]] — Budget definitions
- [[models/asset]] — Assets + depreciation
- [[models/payroll]] — Payroll records

### Code Layers
- [[routes]] — All HTTP endpoints by blueprint
- [[services]] — Business logic layer
- [[database]] — Schema, relationships, migrations

---

## Finance360 Build Status

| Phase | Feature | Status |
|-------|---------|--------|
| 0 | Git setup + Finance360 branch | ✅ Done |
| 0 | Obsidian vault updated for Finance360 | ✅ Done |
| 1 | Database models (26 new tables) | 🔲 Next |
| 2 | Flask blueprints restructure | 🔲 Planned |
| 3 | Executive Dashboard | 🔲 Planned |
| 4 | Expense Management | 🔲 Planned |
| 5 | Revenue Management | 🔲 Planned |
| 6 | Budget Management | 🔲 Planned |
| 7 | Department Financials | 🔲 Planned |
| 8 | Vendors + Customers | 🔲 Planned |
| 9 | Assets + Liabilities | 🔲 Planned |
| 10 | Payroll | 🔲 Planned |
| 11 | Financial Reports | 🔲 Planned |
| 12 | AI Financial Advisor | 🔲 Planned |

---

## Key Info

- Branch: `finance360` (base: `main` = BudgetBuddy AI v1)
- App entry point: `run.py` → `http://127.0.0.1:5000`
- Database: `instance/budget_buddy.db` (SQLite dev)
- Spec: `FINANCE360.md` in repo root (organization app folder)
- Decisions log: [[decisions]]
- Progress log: [[progress]]
