"""
Auto-setup script — runs on every launch via launch.bat.
Safe to run multiple times: skips steps that are already done.
"""

from app import create_app, db
from sqlalchemy import inspect, text

app = create_app()

with app.app_context():

    # ── 1. Run migrations if tables are missing ───────────────────────────────
    tables = inspect(db.engine).get_table_names()
    if "users" not in tables:
        print("[setup] Tables missing — running migrations...")
        from alembic.config import Config
        from alembic import command
        try:
            db.session.execute(text("DELETE FROM alembic_version"))
            db.session.commit()
        except Exception:
            pass
        cfg = Config("migrations/alembic.ini")
        cfg.set_main_option("script_location", "migrations")
        command.upgrade(cfg, "head")
        print("[setup] Migrations complete.")
    else:
        print("[setup] Database tables OK.")

    # ── 2. Seed default expense categories ───────────────────────────────────
    from app.models.expense import ExpenseCategory
    ExpenseCategory.seed_defaults()

    # Ensure Goals category exists
    if not ExpenseCategory.query.filter_by(name="Goals").first():
        db.session.add(ExpenseCategory(name="Goals", color="#A78BFA", icon="target"))
        db.session.commit()
        print("[setup] Goals category created.")

    # ── 3. Seed demo account if it doesn't exist ─────────────────────────────
    from app.models.user import User
    from app.models.settings import UserSettings

    demo_email = "test@budgetbuddy.com"
    demo_password = "test1234"

    user = User.query.filter_by(email=demo_email).first()
    if not user:
        print("[setup] Creating demo account...")
        user = User(full_name="Test User", email=demo_email, currency="INR")
        user.set_password(demo_password)
        db.session.add(user)
        db.session.flush()

        settings = UserSettings(
            user_id=user.id,
            monthly_budget=80000,
            monthly_saving_goal=10000,
            monthly_investing_goal=8000,
        )
        db.session.add(settings)
        db.session.commit()

        # Load full demo data
        from datetime import date
        from app.models.expense import Expense
        from app.models.goal import Goal
        from app.models.recurring import RecurringExpense

        # Fixed costs
        bills_cat  = ExpenseCategory.query.filter_by(name="Bills").first()
        ent_cat    = ExpenseCategory.query.filter_by(name="Entertainment").first()
        health_cat = ExpenseCategory.query.filter_by(name="Health").first()
        food_cat   = ExpenseCategory.query.filter_by(name="Food").first()

        fixed = [
            ("House Rent",    15000, "monthly",  bills_cat,  "2026-06-01"),
            ("Phone Bill",     799,  "monthly",  bills_cat,  "2026-06-05"),
            ("Internet",       999,  "monthly",  bills_cat,  "2026-06-07"),
            ("Netflix",        649,  "monthly",  ent_cat,    "2026-06-10"),
            ("Hotstar",        299,  "monthly",  ent_cat,    "2026-06-10"),
            ("Spotify",        119,  "monthly",  ent_cat,    "2026-06-12"),
            ("Gym",           1200,  "monthly",  health_cat, "2026-06-01"),
            ("Amazon Prime",   999,  "yearly",   ent_cat,    "2026-12-01"),
        ]
        for title, amount, cycle, cat, due in fixed:
            if cat:
                db.session.add(RecurringExpense(
                    user_id=user.id, category_id=cat.id,
                    title=title, amount=amount,
                    billing_cycle=cycle,
                    next_due_date=date.fromisoformat(due),
                ))

        # Goals
        goals_cat = ExpenseCategory.query.filter_by(name="Goals").first()
        goals_data = [
            ("Emergency Fund", "emergency", 200000, 45000, 5000, "2027-06-01"),
            ("Goa Vacation",   "vacation",   60000, 18000, 3000, "2026-12-01"),
            ("Stock Portfolio","investment", 500000, 75000, 8000, None),
        ]
        for name, gtype, target, current, monthly, tdate in goals_data:
            g = Goal(
                user_id=user.id, name=name, goal_type=gtype,
                target_amount=target, current_amount=current,
                monthly_contribution=monthly, status="active",
                target_date=date.fromisoformat(tdate) if tdate else None,
            )
            db.session.add(g)
            db.session.flush()
            if current > 0 and goals_cat:
                db.session.add(Expense(
                    user_id=user.id, category_id=goals_cat.id,
                    amount=current, note=f"Savings towards: {name}",
                    expense_date=date(2026, 1, 1),
                ))

        db.session.commit()

        # Monthly expenses Jan–May 2026
        import random
        random.seed(42)
        cat_map = {
            "Food":          ExpenseCategory.query.filter_by(name="Food").first(),
            "Transport":     ExpenseCategory.query.filter_by(name="Transport").first(),
            "Shopping":      ExpenseCategory.query.filter_by(name="Shopping").first(),
            "Bills":         bills_cat,
            "Entertainment": ent_cat,
            "Health":        health_cat,
            "Education":     ExpenseCategory.query.filter_by(name="Education").first(),
            "Others":        ExpenseCategory.query.filter_by(name="Others").first(),
        }
        months = [
            (2026, 1, 31), (2026, 2, 28), (2026, 3, 31),
            (2026, 4, 30), (2026, 5, 25),
        ]
        templates = [
            ("Food",          "Zomato order",        350, 700),
            ("Food",          "Grocery shopping",    800, 2500),
            ("Food",          "Restaurant dinner",   600, 1800),
            ("Food",          "Coffee & snacks",     150, 400),
            ("Transport",     "Uber/Ola ride",       150, 500),
            ("Transport",     "Petrol",             1000, 2500),
            ("Transport",     "Metro/Bus",            50, 200),
            ("Shopping",      "Clothes shopping",   800, 3000),
            ("Shopping",      "Amazon order",        500, 2000),
            ("Entertainment", "Movie tickets",       400, 800),
            ("Entertainment", "Gaming/Streaming",    200, 500),
            ("Health",        "Pharmacy",            300, 800),
            ("Health",        "Doctor visit",        500, 1500),
            ("Education",     "Online course",       500, 2000),
            ("Others",        "Miscellaneous",       200, 800),
        ]
        for year, month, last_day in months:
            num = random.randint(22, 30)
            for _ in range(num):
                cat_name, note, lo, hi = random.choice(templates)
                cat = cat_map.get(cat_name)
                if not cat:
                    continue
                day = random.randint(1, last_day)
                amount = random.randint(lo, hi)
                db.session.add(Expense(
                    user_id=user.id, category_id=cat.id,
                    amount=amount, note=note,
                    expense_date=date(year, month, day),
                ))
        db.session.commit()
        print(f"[setup] Demo account ready — {demo_email} / {demo_password}")
    else:
        print(f"[setup] Demo account already exists — {demo_email} / {demo_password}")

print("[setup] All done. Starting server...")
