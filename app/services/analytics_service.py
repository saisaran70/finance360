from datetime import date, timedelta
from sqlalchemy import func
from app import db
from app.models.expense import Expense, ExpenseCategory


def _current_month_range():
    today = date.today()
    start = today.replace(day=1)
    if today.month == 12:
        end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    return start, end


def get_dashboard_summary(user):
    start, end = _current_month_range()
    settings = user.settings

    total_spent = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == user.id,
        Expense.expense_date >= start,
        Expense.expense_date <= end,
    ).scalar() or 0
    total_spent = float(total_spent)

    monthly_budget = float(settings.monthly_budget) if settings else 0
    saving_goal = float(settings.monthly_saving_goal or 0) if settings else 0
    investing_goal = float(settings.monthly_investing_goal or 0) if settings else 0
    remaining = monthly_budget - total_spent
    budget_used_pct = round(total_spent / monthly_budget * 100, 1) if monthly_budget > 0 else 0

    # Fixed cost monthly total
    from app.models.recurring import RecurringExpense
    recurring = RecurringExpense.query.filter_by(user_id=user.id).all()
    fixed_cost_monthly = 0.0
    for r in recurring:
        if r.billing_cycle == 'yearly':
            fixed_cost_monthly += float(r.amount) / 12
        elif r.billing_cycle == 'weekly':
            fixed_cost_monthly += float(r.amount) * 4.33
        else:
            fixed_cost_monthly += float(r.amount)

    recent_expenses = (Expense.query
                       .filter_by(user_id=user.id)
                       .order_by(Expense.expense_date.desc())
                       .limit(5)
                       .all())

    category_data = get_category_breakdown(user)

    return {
        'total_spent': total_spent,
        'monthly_budget': monthly_budget,
        'remaining': remaining,
        'saving_goal': saving_goal,
        'investing_goal': investing_goal,
        'fixed_cost_monthly': round(fixed_cost_monthly),
        'budget_used_pct': budget_used_pct,
        'month_label': start.strftime('%B %Y'),
        'recent_expenses': [e.to_dict() for e in recent_expenses],
        'category_breakdown': category_data,
        'currency': user.currency or 'INR',
    }


def get_category_breakdown(user):
    start, end = _current_month_range()

    rows = db.session.query(
        ExpenseCategory.name,
        ExpenseCategory.color,
        func.sum(Expense.amount).label('total')
    ).join(Expense, Expense.category_id == ExpenseCategory.id
    ).filter(
        Expense.user_id == user.id,
        Expense.expense_date >= start,
        Expense.expense_date <= end,
    ).group_by(ExpenseCategory.name, ExpenseCategory.color
    ).order_by(func.sum(Expense.amount).desc()
    ).all()

    grand_total = sum(float(r.total) for r in rows)

    result = [
        {
            'category': r.name,
            'color': r.color,
            'amount': float(r.total),
            'percentage': round(float(r.total) / grand_total * 100, 1) if grand_total > 0 else 0,
            'is_goal': r.name == 'Goals',
        }
        for r in rows
    ]

    # Always include Goals row if user has goals but none logged this month
    from app.models.goal import Goal
    has_goals = Goal.query.filter_by(user_id=user.id).count() > 0
    if has_goals and not any(r['category'] == 'Goals' for r in result):
        goals_cat = ExpenseCategory.query.filter_by(name='Goals').first()
        if goals_cat:
            result.append({
                'category': 'Goals',
                'color': goals_cat.color,
                'amount': 0.0,
                'percentage': 0.0,
                'is_goal': True,
            })

    return result


def get_monthly_trends(user):
    today = date.today()
    results = []

    for i in range(5, -1, -1):
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1

        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)

        total = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user.id,
            Expense.expense_date >= start,
            Expense.expense_date <= end,
        ).scalar() or 0

        results.append({
            'month': start.strftime('%b %Y'),
            'total': float(total),
        })

    return results


def get_fixed_cost_analysis(user):
    from app.models.recurring import RecurringExpense
    recurring = RecurringExpense.query.filter_by(user_id=user.id).all()
    items = []
    for r in recurring:
        monthly_equiv = float(r.amount)
        if r.billing_cycle == 'yearly':
            monthly_equiv = float(r.amount) / 12
        elif r.billing_cycle == 'weekly':
            monthly_equiv = float(r.amount) * 4.33
        items.append({
            'title': r.title,
            'amount': float(r.amount),
            'monthly_equiv': round(monthly_equiv),
            'billing_cycle': r.billing_cycle,
            'next_due_date': r.next_due_date.strftime('%d %b %Y') if r.next_due_date else None,
            'category': r.category.name if r.category else 'Other',
            'color': r.category.color if r.category else '#94A3B8',
        })
    return items


def get_projected_spend(user):
    today = date.today()
    start = today.replace(day=1)
    days_elapsed = today.day

    if today.month == 12:
        end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)
    days_in_month = end_of_month.day
    days_remaining = (end_of_month - today).days

    total_so_far = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == user.id,
        Expense.expense_date >= start,
        Expense.expense_date <= today,
    ).scalar() or 0
    total_so_far = float(total_so_far)

    projected = round(total_so_far / days_elapsed * days_in_month) if days_elapsed > 0 else round(total_so_far)
    return {
        'projected': projected,
        'days_until_cycle': days_remaining,
    }


def get_goal_analytics(user):
    from app.models.goal import Goal
    goals = Goal.query.filter_by(user_id=user.id, status='active').all()
    total_saved = sum(float(g.current_amount) for g in goals)
    total_target = sum(float(g.target_amount) for g in goals)
    remaining = max(0.0, total_target - total_saved)
    pct_funded = round(total_saved / total_target * 100) if total_target > 0 else 0
    return {
        'total_saved': total_saved,
        'total_target': total_target,
        'remaining': remaining,
        'pct_funded': pct_funded,
        'has_goals': len(goals) > 0,
    }


def get_spending_savings_trend(user, range_key='6m'):
    today = date.today()
    settings = user.settings
    monthly_budget = float(settings.monthly_budget) if settings and settings.monthly_budget else 0

    labels, spending_data, savings_data = [], [], []

    investing_goal = float(settings.monthly_investing_goal or 0) if settings else 0
    # Savings = what's left after spending AND investing allocation
    effective_savings_base = monthly_budget - investing_goal

    if range_key in ('7d', '30d'):
        days = 7 if range_key == '7d' else 30
        for i in range(days - 1, -1, -1):
            d = today - timedelta(days=i)
            if d.month == 12:
                days_in_month = 31
            else:
                days_in_month = (date(d.year, d.month + 1, 1) - timedelta(days=1)).day
            daily_base = effective_savings_base / days_in_month if days_in_month > 0 else 0

            spent = db.session.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user.id,
                Expense.expense_date == d,
            ).scalar() or 0
            spent = float(spent)

            labels.append(d.strftime('%d %b'))
            spending_data.append(round(spent))
            savings_data.append(round(daily_base - spent))

    else:
        months = 6 if range_key == '6m' else 12
        for i in range(months - 1, -1, -1):
            month = today.month - i
            year = today.year
            while month <= 0:
                month += 12
                year -= 1

            start = date(year, month, 1)
            if month == 12:
                end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end = date(year, month + 1, 1) - timedelta(days=1)

            spent = db.session.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user.id,
                Expense.expense_date >= start,
                Expense.expense_date <= end,
            ).scalar() or 0
            spent = float(spent)

            labels.append(start.strftime('%b %Y'))
            spending_data.append(round(spent))
            savings_data.append(round(effective_savings_base - spent))

    return {'labels': labels, 'spending': spending_data, 'savings': savings_data}


def get_chart_data(user):
    return {
        'category_breakdown': get_category_breakdown(user),
        'monthly_trends': get_monthly_trends(user),
    }
