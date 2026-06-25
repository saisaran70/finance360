from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.settings import UserSettings
from app.models.expense import ExpenseCategory
from app.models.recurring import RecurringExpense

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('/')
@login_required
def index():
    settings = current_user.settings
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()
    categories = ExpenseCategory.query.order_by(ExpenseCategory.name).all()
    fixed_costs = RecurringExpense.query.filter_by(user_id=current_user.id).order_by(RecurringExpense.title).all()
    return render_template('settings/index.html', settings=settings, categories=categories, fixed_costs=fixed_costs)


@settings_bp.route('/update', methods=['POST'])
@login_required
def update():
    settings = current_user.settings
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.session.add(settings)

    try:
        settings.monthly_budget = float(request.form.get('monthly_budget', 0))
        settings.monthly_saving_goal = float(request.form.get('monthly_saving_goal', 0))
        settings.monthly_investing_goal = float(request.form.get('monthly_investing_goal', 0) or 0)
        settings.ai_alerts_enabled = request.form.get('ai_alerts_enabled') == 'on'
        settings.notifications_enabled = request.form.get('notifications_enabled') == 'on'

        current_user.full_name = request.form.get('full_name', current_user.full_name).strip()
        current_user.currency = request.form.get('currency', current_user.currency)
        current_user.city = request.form.get('city', current_user.city or '').strip()

        db.session.commit()
        flash('Settings updated successfully.', 'success')
    except (ValueError, TypeError):
        flash('Invalid data.', 'error')

    return redirect(url_for('settings.index') + '?tab=profile')


@settings_bp.route('/fixed-costs/add', methods=['POST'])
@login_required
def add_fixed_cost():
    try:
        title = request.form.get('title', '').strip()
        amount = float(request.form.get('amount', 0))
        category_id = int(request.form.get('category_id'))
        billing_cycle = request.form.get('billing_cycle', 'monthly')
        next_due_raw = request.form.get('next_due_date', '')
        next_due = date.fromisoformat(next_due_raw) if next_due_raw else None

        if not title or amount <= 0:
            flash('Please enter a valid name and amount.', 'error')
            return redirect(url_for('settings.index') + '?tab=fixed-costs')

        item = RecurringExpense(
            user_id=current_user.id,
            category_id=category_id,
            title=title,
            amount=amount,
            billing_cycle=billing_cycle,
            next_due_date=next_due,
            auto_add=False,
        )
        db.session.add(item)
        db.session.commit()
        flash(f'"{title}" added to fixed costs.', 'success')
    except (ValueError, TypeError):
        flash('Invalid data.', 'error')

    return redirect(url_for('settings.index') + '?tab=fixed-costs')


@settings_bp.route('/fixed-costs/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_fixed_cost(item_id):
    item = RecurringExpense.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    title = item.title
    db.session.delete(item)
    db.session.commit()
    flash(f'"{title}" removed from fixed costs.', 'success')
    return redirect(url_for('settings.index') + '?tab=fixed-costs')
