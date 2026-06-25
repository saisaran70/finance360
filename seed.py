from app import create_app, db
from app.models.user import User
from app.models.settings import UserSettings
from app.models.expense import Expense, ExpenseCategory
from app.models.goal import Goal
from datetime import date, timedelta

app = create_app()

with app.app_context():
    # Seed categories if missing
    ExpenseCategory.seed_defaults()

    # Remove existing test user if re-running
    existing = User.query.filter_by(email='test@budgetbuddy.com').first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        print('Removed old test user.')

    # Create test user
    user = User(full_name='Test User', email='test@budgetbuddy.com', currency='INR', city='Chennai')
    user.set_password('test1234')
    db.session.add(user)
    db.session.flush()

    # User settings
    settings = UserSettings(
        user_id=user.id,
        monthly_budget=30000,
        monthly_saving_goal=5000,
        ai_alerts_enabled=True,
        notifications_enabled=True,
    )
    db.session.add(settings)

    # Sample expenses for current month
    cats = {c.name: c for c in ExpenseCategory.query.all()}
    today = date.today()

    sample_expenses = [
        (450,  'Food',          'Lunch at office canteen',      today),
        (1200, 'Transport',     'Monthly bus pass',             today - timedelta(days=1)),
        (3500, 'Shopping',      'Groceries from supermarket',   today - timedelta(days=2)),
        (999,  'Entertainment', 'Netflix subscription',         today - timedelta(days=3)),
        (800,  'Food',          'Dinner with friends',          today - timedelta(days=4)),
        (2500, 'Bills',         'Electricity bill',             today - timedelta(days=5)),
        (350,  'Food',          'Breakfast + coffee',           today - timedelta(days=6)),
        (600,  'Health',        'Pharmacy — vitamins',          today - timedelta(days=7)),
        (1800, 'Shopping',      'Clothes from Myntra',          today - timedelta(days=8)),
        (250,  'Transport',     'Auto to metro station',        today - timedelta(days=9)),
        (4200, 'Education',     'Udemy course bundle',          today - timedelta(days=10)),
        (700,  'Food',          'Weekend brunch',               today - timedelta(days=11)),
    ]

    for amount, cat_name, note, exp_date in sample_expenses:
        cat = cats.get(cat_name) or cats.get('Others')
        db.session.add(Expense(
            user_id=user.id,
            category_id=cat.id,
            amount=amount,
            note=note,
            expense_date=exp_date,
        ))

    # Sample goals
    db.session.add(Goal(
        user_id=user.id,
        name='Emergency Fund',
        goal_type='emergency',
        target_amount=100000,
        current_amount=35000,
        target_date=date(2026, 12, 31),
    ))
    db.session.add(Goal(
        user_id=user.id,
        name='Vacation to Goa',
        goal_type='vacation',
        target_amount=25000,
        current_amount=8000,
        target_date=date(2026, 10, 1),
    ))
    db.session.add(Goal(
        user_id=user.id,
        name='Laptop Upgrade',
        goal_type='savings',
        target_amount=60000,
        current_amount=12000,
        target_date=date(2027, 3, 1),
    ))

    db.session.commit()

    total = sum(a for a, *_ in sample_expenses)
    print('=' * 40)
    print('Test user created successfully!')
    print('=' * 40)
    print(f'  Email    : test@budgetbuddy.com')
    print(f'  Password : test1234')
    print(f'  Budget   : INR 30,000 / month')
    print(f'  Spent    : INR {total:,} (sample expenses)')
    print(f'  Goals    : 3 goals added')
    print('=' * 40)
