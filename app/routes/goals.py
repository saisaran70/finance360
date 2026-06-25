from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.goal import Goal

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')


def _log_goal_expense(user_id, goal_name, amount):
    from app.models.expense import Expense, ExpenseCategory
    cat = ExpenseCategory.query.filter_by(name='Goals').first()
    if not cat:
        cat = ExpenseCategory(name='Goals', color='#A78BFA', icon='target')
        db.session.add(cat)
        db.session.flush()
    db.session.add(Expense(
        user_id=user_id,
        category_id=cat.id,
        amount=amount,
        note=f'Savings towards: {goal_name}',
        expense_date=date.today(),
    ))


@goals_bp.route('/')
@login_required
def index():
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.created_at.desc()).all()
    return render_template('goals/index.html', goals=goals)


@goals_bp.route('/add', methods=['POST'])
@login_required
def add():
    try:
        name = request.form.get('name', '').strip()
        goal_type = request.form.get('goal_type', 'savings')
        target_amount = float(request.form.get('target_amount', 0))
        current_amount = float(request.form.get('current_amount', 0))
        target_date_str = request.form.get('target_date', '')
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date() if target_date_str else None

        if not name or target_amount <= 0:
            flash('Goal name and target amount are required.', 'error')
            return redirect(url_for('goals.index'))

        monthly_contribution = float(request.form.get('monthly_contribution', 0) or 0)

        goal = Goal(
            user_id=current_user.id,
            name=name,
            goal_type=goal_type,
            target_amount=target_amount,
            current_amount=current_amount,
            monthly_contribution=monthly_contribution,
            target_date=target_date,
        )
        db.session.add(goal)
        db.session.flush()
        if current_amount > 0:
            _log_goal_expense(current_user.id, name, current_amount)
        db.session.commit()
        flash('Goal created!', 'success')
    except (ValueError, TypeError):
        flash('Invalid goal data.', 'error')

    return redirect(url_for('goals.index'))


@goals_bp.route('/<int:goal_id>/edit', methods=['POST'])
@login_required
def edit(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    try:
        goal.name = request.form.get('name', goal.name).strip()
        goal.goal_type = request.form.get('goal_type', goal.goal_type)
        goal.target_amount = float(request.form.get('target_amount', goal.target_amount))
        goal.current_amount = float(request.form.get('current_amount', goal.current_amount))
        goal.monthly_contribution = float(request.form.get('monthly_contribution', 0) or 0)
        goal.status = request.form.get('status', goal.status)
        date_str = request.form.get('target_date', '')
        if date_str:
            goal.target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Log this month's saving as an expense if filled in
        add_contribution = float(request.form.get('add_contribution', 0) or 0)
        if add_contribution > 0:
            goal.current_amount = float(goal.current_amount) + add_contribution
            _log_goal_expense(current_user.id, goal.name, add_contribution)

        if float(goal.current_amount) >= float(goal.target_amount):
            goal.status = 'completed'

        db.session.commit()
        flash('Goal updated.', 'success')
    except (ValueError, TypeError):
        flash('Invalid data.', 'error')

    return redirect(url_for('goals.index'))


@goals_bp.route('/<int:goal_id>/contribute', methods=['POST'])
@login_required
def contribute(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    try:
        amount = float(request.form.get('amount', 0) or 0)
        if amount <= 0:
            flash('Enter a valid amount.', 'error')
            return redirect(url_for('goals.index'))
        goal.current_amount = float(goal.current_amount) + amount
        if goal.current_amount >= float(goal.target_amount):
            goal.status = 'completed'
        _log_goal_expense(current_user.id, goal.name, amount)
        db.session.commit()
        flash(f'Added {current_user.currency} {amount:,.0f} to "{goal.name}".', 'success')
    except (ValueError, TypeError):
        flash('Invalid amount.', 'error')
    return redirect(url_for('goals.index'))


@goals_bp.route('/<int:goal_id>/delete', methods=['POST'])
@login_required
def delete(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted.', 'success')
    return redirect(url_for('goals.index'))


@goals_bp.route('/data')
@login_required
def data():
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    return jsonify([g.to_dict() for g in goals])
