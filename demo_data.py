#!/usr/bin/env python3
"""
Demo data seed: January 2026 – May 2026
Clears existing expenses, goals, and recurring expenses for the test user,
then seeds 5 months of realistic Indian finance data.
Run: python demo_data.py
"""
from datetime import date
from app import create_app, db
from app.models.user import User
from app.models.expense import Expense, ExpenseCategory
from app.models.goal import Goal
from app.models.recurring import RecurringExpense
from app.models.settings import UserSettings

app = create_app()

with app.app_context():

    # ── Find user ────────────────────────────────────────────────
    user = User.query.filter_by(email='test@budgetbuddy.com').first()
    if not user:
        print('Test user not found. Run seed.py first.')
        exit(1)
    print(f'Seeding demo data for: {user.full_name} ({user.email})')

    # ── Clear existing data ──────────────────────────────────────
    Expense.query.filter_by(user_id=user.id).delete()
    Goal.query.filter_by(user_id=user.id).delete()
    RecurringExpense.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    print('Cleared existing expenses, goals, recurring expenses.')

    # ── Update settings ──────────────────────────────────────────
    settings = user.settings
    if not settings:
        settings = UserSettings(user_id=user.id)
        db.session.add(settings)
    settings.monthly_budget       = 80000
    settings.monthly_saving_goal  = 10000
    settings.monthly_investing_goal = 8000
    settings.ai_alerts_enabled    = True
    settings.notifications_enabled = True
    db.session.commit()
    print('Settings: budget ₹80,000 | savings ₹10,000 | investing ₹8,000')

    # ── Category helpers ─────────────────────────────────────────
    def cat(name):
        c = ExpenseCategory.query.filter_by(name=name).first()
        if not c:
            raise ValueError(f'Category "{name}" not found. Run seed.py first.')
        return c

    food          = cat('Food')
    transport     = cat('Transport')
    shopping      = cat('Shopping')
    bills         = cat('Bills')
    entertainment = cat('Entertainment')
    health        = cat('Health')
    education     = cat('Education')
    others        = cat('Others')
    goals_cat     = cat('Goals')

    # ── Fixed / Recurring costs ──────────────────────────────────
    recurring_items = [
        ('House Rent',          25000, 'monthly',  bills,         date(2026, 6, 1)),
        ('Phone Bill – Airtel',   999, 'monthly',  bills,         date(2026, 6, 2)),
        ('Jio Fiber Internet',    800, 'monthly',  bills,         date(2026, 6, 3)),
        ('Netflix',               649, 'monthly',  entertainment, date(2026, 6, 3)),
        ('Hotstar Premium',       299, 'monthly',  entertainment, date(2026, 6, 4)),
        ('Spotify Premium',       119, 'monthly',  entertainment, date(2026, 6, 4)),
        ('Gym Membership',       1500, 'monthly',  health,        date(2026, 6, 5)),
        ('Amazon Prime',         1499, 'yearly',   entertainment, date(2027, 1, 5)),
    ]
    for title, amount, cycle, category, next_due in recurring_items:
        db.session.add(RecurringExpense(
            user_id=user.id,
            category_id=category.id,
            title=title,
            amount=amount,
            billing_cycle=cycle,
            next_due_date=next_due,
            auto_add=False,
        ))
    db.session.commit()
    print(f'Created {len(recurring_items)} fixed/recurring costs.')

    # ── Goals ────────────────────────────────────────────────────
    goals = [
        Goal(user_id=user.id, name='Emergency Fund',  goal_type='emergency',
             target_amount=200000, current_amount=50000, monthly_contribution=5000,
             status='active', target_date=date(2026, 12, 31)),
        Goal(user_id=user.id, name='Goa Vacation',    goal_type='vacation',
             target_amount=60000,  current_amount=30000, monthly_contribution=3000,
             status='active', target_date=date(2026, 10, 31)),
        Goal(user_id=user.id, name='Stock Portfolio', goal_type='investment',
             target_amount=500000, current_amount=80000, monthly_contribution=8000,
             status='active', target_date=date(2027, 6, 30)),
    ]
    for g in goals:
        db.session.add(g)
    db.session.commit()
    print('Created 3 goals: Emergency Fund | Goa Vacation | Stock Portfolio')

    # ── Expense helper ───────────────────────────────────────────
    def exp(category, amount, note, yr, mo, day):
        db.session.add(Expense(
            user_id=user.id,
            category_id=category.id,
            amount=amount,
            note=note,
            expense_date=date(yr, mo, day),
        ))

    # ════════════════════════════════════════════════════════════
    # JANUARY 2026  –  total ≈ ₹68,006
    # ════════════════════════════════════════════════════════════
    print('Seeding January 2026...')
    # Fixed bills
    exp(bills,         25000, 'House Rent',                        2026,1,1)
    exp(bills,           999, 'Phone Bill – Airtel',               2026,1,2)
    exp(bills,           800, 'Jio Fiber Internet',                2026,1,3)
    exp(entertainment,   649, 'Netflix subscription',              2026,1,3)
    exp(entertainment,   299, 'Hotstar Premium',                   2026,1,4)
    exp(entertainment,   119, 'Spotify Premium',                   2026,1,4)
    exp(entertainment,  1499, 'Amazon Prime – Annual',             2026,1,5)
    exp(health,         1500, 'Gym membership',                    2026,1,5)
    # Food
    exp(food,           2800, 'BigBasket – weekly groceries',      2026,1,6)
    exp(food,            450, 'Zomato – New Year dinner',          2026,1,8)
    exp(food,            380, 'Swiggy – lunch',                    2026,1,10)
    exp(food,           2600, 'BigBasket – weekly groceries',      2026,1,13)
    exp(food,            520, 'Zomato – biryani',                  2026,1,15)
    exp(food,            480, 'Cafe Coffee Day – team outing',     2026,1,17)
    exp(food,           2400, 'BigBasket – weekly groceries',      2026,1,20)
    exp(food,            650, 'Swiggy – family dinner',            2026,1,22)
    exp(food,           2200, 'BigBasket – weekly groceries',      2026,1,27)
    exp(food,            390, 'Zomato – pizza night',              2026,1,29)
    # Transport
    exp(transport,       450, 'Ola – office commute',              2026,1,7)
    exp(transport,       380, 'Petrol – Hero Splendor',            2026,1,10)
    exp(transport,       290, 'Uber – airport drop',               2026,1,14)
    exp(transport,       420, 'Ola cabs – weekly',                 2026,1,18)
    exp(transport,       380, 'Petrol refill',                     2026,1,24)
    exp(transport,       200, 'Auto rides – misc',                 2026,1,28)
    # Shopping – New Year
    exp(shopping,       3200, 'Myntra – New Year clothes',         2026,1,7)
    exp(shopping,       1800, 'Amazon – home essentials',          2026,1,12)
    exp(shopping,        800, 'D-Mart – household supplies',       2026,1,20)
    # Entertainment
    exp(entertainment,   500, 'PVR – movie tickets',               2026,1,15)
    exp(entertainment,   800, 'Weekend outing – bowling',          2026,1,22)
    # Health
    exp(health,          350, 'Pharmacy – medicines',              2026,1,9)
    exp(health,          200, 'Doctor consultation',               2026,1,18)
    # Goal contributions
    exp(goals_cat,      5000, 'Savings towards: Emergency Fund',   2026,1,1)
    exp(goals_cat,      3000, 'Savings towards: Goa Vacation',     2026,1,1)
    exp(goals_cat,      8000, 'Savings towards: Stock Portfolio',  2026,1,1)

    # ════════════════════════════════════════════════════════════
    # FEBRUARY 2026  –  total ≈ ₹65,776
    # ════════════════════════════════════════════════════════════
    print('Seeding February 2026...')
    exp(bills,         25000, 'House Rent',                        2026,2,1)
    exp(bills,           999, 'Phone Bill – Airtel',               2026,2,2)
    exp(bills,           800, 'Jio Fiber Internet',                2026,2,3)
    exp(entertainment,   649, 'Netflix subscription',              2026,2,3)
    exp(entertainment,   299, 'Hotstar Premium',                   2026,2,4)
    exp(entertainment,   119, 'Spotify Premium',                   2026,2,4)
    exp(health,         1500, 'Gym membership',                    2026,2,5)
    # Food
    exp(food,           2600, 'BigBasket – weekly groceries',      2026,2,5)
    exp(food,            420, 'Zomato – dinner',                   2026,2,7)
    exp(food,            350, 'Swiggy – lunch',                    2026,2,9)
    exp(food,           2400, 'BigBasket – weekly groceries',      2026,2,12)
    exp(food,           1200, "Valentine's Day dinner – Farzi",    2026,2,14)
    exp(food,           2200, 'BigBasket – weekly groceries',      2026,2,19)
    exp(food,            480, 'Zomato – pizza',                    2026,2,21)
    exp(food,           2100, 'BigBasket – weekly groceries',      2026,2,26)
    # Transport
    exp(transport,       380, 'Petrol refill',                     2026,2,6)
    exp(transport,       320, 'Ola cabs – office',                 2026,2,11)
    exp(transport,       400, 'Petrol refill',                     2026,2,18)
    exp(transport,       280, 'Auto rides – misc',                 2026,2,25)
    # Shopping
    exp(shopping,       2500, "Valentine's Day gift – Tanishq",    2026,2,13)
    exp(shopping,        800, 'Amazon – household items',          2026,2,19)
    # Entertainment
    exp(entertainment,   700, 'Weekend outing',                    2026,2,8)
    exp(entertainment,   500, 'PVR – movie',                       2026,2,21)
    # Education
    exp(education,      2500, 'Udemy – Python course',             2026,2,10)
    # Health
    exp(health,          280, 'Pharmacy – cold medicines',         2026,2,15)
    # Goal contributions
    exp(goals_cat,      5000, 'Savings towards: Emergency Fund',   2026,2,1)
    exp(goals_cat,      3000, 'Savings towards: Goa Vacation',     2026,2,1)
    exp(goals_cat,      8000, 'Savings towards: Stock Portfolio',  2026,2,1)

    # ════════════════════════════════════════════════════════════
    # MARCH 2026  –  total ≈ ₹71,366  (Holi – highest month)
    # ════════════════════════════════════════════════════════════
    print('Seeding March 2026...')
    exp(bills,         25000, 'House Rent',                        2026,3,1)
    exp(bills,           999, 'Phone Bill – Airtel',               2026,3,2)
    exp(bills,           800, 'Jio Fiber Internet',                2026,3,3)
    exp(entertainment,   649, 'Netflix subscription',              2026,3,3)
    exp(entertainment,   299, 'Hotstar Premium',                   2026,3,4)
    exp(entertainment,   119, 'Spotify Premium',                   2026,3,4)
    exp(health,         1500, 'Gym membership',                    2026,3,5)
    # Food
    exp(food,           3200, 'BigBasket – weekly groceries',      2026,3,4)
    exp(food,            580, 'Zomato – team dinner',              2026,3,7)
    exp(food,           1800, 'Holi celebration food & sweets',    2026,3,10)
    exp(food,           2800, 'BigBasket – weekly groceries',      2026,3,14)
    exp(food,            650, 'Swiggy – family dinner',            2026,3,16)
    exp(food,           2400, 'BigBasket – weekly groceries',      2026,3,21)
    exp(food,            520, 'Cafe – team lunch outing',          2026,3,24)
    exp(food,           2200, 'BigBasket – weekly groceries',      2026,3,28)
    # Transport
    exp(transport,       420, 'Petrol refill',                     2026,3,5)
    exp(transport,       350, 'Ola cabs',                          2026,3,10)
    exp(transport,       800, 'Train tickets – Holi trip',         2026,3,12)
    exp(transport,       380, 'Petrol refill',                     2026,3,20)
    exp(transport,       300, 'Auto rides',                        2026,3,27)
    # Shopping – Holi
    exp(shopping,       4500, 'Holi clothes & gifts',              2026,3,8)
    exp(shopping,       1800, 'Amazon – home decor',               2026,3,15)
    exp(shopping,       1200, 'D-Mart – grocery essentials',       2026,3,22)
    # Entertainment
    exp(entertainment,   600, 'Holi party supplies',               2026,3,9)
    exp(entertainment,   800, 'Weekend – movie + dinner',          2026,3,23)
    # Health
    exp(health,          400, 'Pharmacy – Holi skin care',         2026,3,13)
    exp(health,          300, 'Doctor visit – allergy',            2026,3,25)
    # Goal contributions
    exp(goals_cat,      5000, 'Savings towards: Emergency Fund',   2026,3,1)
    exp(goals_cat,      3000, 'Savings towards: Goa Vacation',     2026,3,1)
    exp(goals_cat,      8000, 'Savings towards: Stock Portfolio',  2026,3,1)

    # ════════════════════════════════════════════════════════════
    # APRIL 2026  –  total ≈ ₹63,486
    # ════════════════════════════════════════════════════════════
    print('Seeding April 2026...')
    exp(bills,         25000, 'House Rent',                        2026,4,1)
    exp(bills,           999, 'Phone Bill – Airtel',               2026,4,2)
    exp(bills,           800, 'Jio Fiber Internet',                2026,4,3)
    exp(entertainment,   649, 'Netflix subscription',              2026,4,3)
    exp(entertainment,   299, 'Hotstar Premium',                   2026,4,4)
    exp(entertainment,   119, 'Spotify Premium',                   2026,4,4)
    exp(health,         1500, 'Gym membership',                    2026,4,5)
    # Food
    exp(food,           2700, 'BigBasket – weekly groceries',      2026,4,5)
    exp(food,            480, 'Zomato – dinner',                   2026,4,8)
    exp(food,            420, 'Swiggy – lunch',                    2026,4,11)
    exp(food,           2500, 'BigBasket – weekly groceries',      2026,4,14)
    exp(food,            560, 'Restaurant – family lunch',         2026,4,17)
    exp(food,           2300, 'BigBasket – weekly groceries',      2026,4,21)
    exp(food,            400, 'Zomato – biryani night',            2026,4,24)
    exp(food,           2100, 'BigBasket – weekly groceries',      2026,4,28)
    # Transport
    exp(transport,       400, 'Petrol refill',                     2026,4,6)
    exp(transport,       350, 'Ola cabs',                          2026,4,12)
    exp(transport,       380, 'Petrol refill',                     2026,4,19)
    exp(transport,       280, 'Auto rides',                        2026,4,26)
    # Shopping
    exp(shopping,       1800, 'Ajio – summer clothes',             2026,4,9)
    exp(shopping,        900, 'Amazon – household',                2026,4,16)
    # Entertainment
    exp(entertainment,   700, 'IPL live stream + snacks',          2026,4,12)
    exp(entertainment,   500, 'Weekend outing',                    2026,4,26)
    # Health – summer checkups
    exp(health,          350, 'Annual health check',               2026,4,10)
    exp(health,          800, 'Dermatologist – summer skin',       2026,4,20)
    exp(health,          200, 'Pharmacy – sunscreen + vitamins',   2026,4,24)
    # Education
    exp(education,      1800, 'Coursera – Data Science module',    2026,4,15)
    # Goal contributions
    exp(goals_cat,      5000, 'Savings towards: Emergency Fund',   2026,4,1)
    exp(goals_cat,      3000, 'Savings towards: Goa Vacation',     2026,4,1)
    exp(goals_cat,      8000, 'Savings towards: Stock Portfolio',  2026,4,1)

    # ════════════════════════════════════════════════════════════
    # MAY 2026  –  total ≈ ₹57,476  (partial – up to 27th)
    # ════════════════════════════════════════════════════════════
    print('Seeding May 2026...')
    exp(bills,         25000, 'House Rent',                        2026,5,1)
    exp(bills,           999, 'Phone Bill – Airtel',               2026,5,2)
    exp(bills,           800, 'Jio Fiber Internet',                2026,5,3)
    exp(entertainment,   649, 'Netflix subscription',              2026,5,3)
    exp(entertainment,   299, 'Hotstar Premium',                   2026,5,4)
    exp(entertainment,   119, 'Spotify Premium',                   2026,5,5)
    exp(health,         1500, 'Gym membership',                    2026,5,5)
    # Food
    exp(food,           2800, 'BigBasket – weekly groceries',      2026,5,5)
    exp(food,            460, 'Zomato – dinner',                   2026,5,8)
    exp(food,            380, 'Swiggy – lunch',                    2026,5,12)
    exp(food,           2400, 'BigBasket – weekly groceries',      2026,5,14)
    exp(food,            520, 'Restaurant – birthday dinner',      2026,5,18)
    exp(food,           2200, 'BigBasket – weekly groceries',      2026,5,21)
    exp(food,            480, 'Zomato – dinner',                   2026,5,25)
    # Transport
    exp(transport,       420, 'Petrol refill',                     2026,5,7)
    exp(transport,       350, 'Ola cabs',                          2026,5,13)
    exp(transport,       300, 'Petrol refill',                     2026,5,22)
    # Shopping
    exp(shopping,       1200, 'Myntra – casual wear',              2026,5,10)
    exp(shopping,        800, 'Amazon – essentials',               2026,5,20)
    # Entertainment
    exp(entertainment,   600, 'Weekend movie – PVR',               2026,5,17)
    # Health
    exp(health,          300, 'Pharmacy – seasonal',               2026,5,15)
    # Goal contributions
    exp(goals_cat,      5000, 'Savings towards: Emergency Fund',   2026,5,1)
    exp(goals_cat,      3000, 'Savings towards: Goa Vacation',     2026,5,1)
    exp(goals_cat,      8000, 'Savings towards: Stock Portfolio',  2026,5,1)

    # ════════════════════════════════════════════════════════════
    # JUNE 2026  –  total ≈ ₹56,326  (up to 14th — current month)
    # ════════════════════════════════════════════════════════════
    print('Seeding June 2026...')
    # Fixed bills
    exp(bills,         25000, 'House Rent',                        2026,6,1)
    exp(bills,           999, 'Phone Bill – Airtel',               2026,6,2)
    exp(bills,           800, 'Jio Fiber Internet',                2026,6,3)
    exp(entertainment,   649, 'Netflix subscription',              2026,6,3)
    exp(entertainment,   299, 'Hotstar Premium',                   2026,6,4)
    exp(entertainment,   119, 'Spotify Premium',                   2026,6,4)
    exp(health,         1500, 'Gym membership',                    2026,6,5)
    # Food
    exp(food,           2900, 'BigBasket – weekly groceries',      2026,6,5)
    exp(food,            480, 'Zomato – dinner with team',         2026,6,7)
    exp(food,            350, 'Swiggy – lunch',                    2026,6,9)
    exp(food,           2600, 'BigBasket – weekly groceries',      2026,6,12)
    exp(food,            650, 'Zomato – weekend dinner',           2026,6,14)
    # Transport
    exp(transport,       420, 'Petrol refill – Hero Splendor',     2026,6,9)
    exp(transport,       360, 'Ola cabs – office',                 2026,6,11)
    # Shopping – Myntra mid-year sale
    exp(shopping,       3200, 'Myntra – mid-year sale haul',       2026,6,13)
    # Goal contributions
    exp(goals_cat,      5000, 'Savings towards: Emergency Fund',   2026,6,1)
    exp(goals_cat,      3000, 'Savings towards: Goa Vacation',     2026,6,1)
    exp(goals_cat,      8000, 'Savings towards: Stock Portfolio',  2026,6,1)

    db.session.commit()

    # ── Summary ──────────────────────────────────────────────────
    total = Expense.query.filter_by(user_id=user.id).count()
    print(f'\n✅ Demo data seeded successfully!')
    print(f'   Expenses : {total} entries across Jan–Jun 2026')
    print(f'   Goals    : Emergency Fund | Goa Vacation | Stock Portfolio')
    print(f'   Fixed    : {len(recurring_items)} recurring bills')
    print(f'   Settings : Budget ₹80,000 | Save ₹10,000 | Invest ₹8,000')
    print(f'\n   Monthly spend estimates:')
    print(f'   Jan ≈ ₹68,006  |  Feb ≈ ₹65,776  |  Mar ≈ ₹71,366 (Holi)')
    print(f'   Apr ≈ ₹63,486  |  May ≈ ₹57,476  |  Jun ≈ ₹56,326 (up to 14th)')
