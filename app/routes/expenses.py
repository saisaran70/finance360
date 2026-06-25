from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.expense import Expense, ExpenseCategory

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')


@expenses_bp.route('/')
@login_required
def index():
    period    = request.args.get('period', '3m')
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    expenses  = _get_filtered_expenses(current_user.id, period, date_from, date_to)
    categories = ExpenseCategory.query.all()
    return render_template('expenses/index.html',
                           expenses=expenses,
                           categories=categories,
                           period=period,
                           date_from=date_from,
                           date_to=date_to)


@expenses_bp.route('/add', methods=['POST'])
@login_required
def add():
    try:
        amount = float(request.form.get('amount', 0))
        category_id = int(request.form.get('category_id', 0))
        note = request.form.get('note', '').strip()
        expense_date_str = request.form.get('expense_date', '')
        expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d').date() if expense_date_str else date.today()

        if amount <= 0:
            flash('Amount must be greater than zero.', 'error')
            return redirect(url_for('expenses.index'))

        expense = Expense(
            user_id=current_user.id,
            category_id=category_id,
            amount=amount,
            note=note,
            expense_date=expense_date,
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully.', 'success')
    except (ValueError, TypeError):
        flash('Invalid expense data.', 'error')

    return redirect(request.referrer or url_for('expenses.index'))


@expenses_bp.route('/<int:expense_id>/edit', methods=['POST'])
@login_required
def edit(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    try:
        expense.amount = float(request.form.get('amount', expense.amount))
        expense.category_id = int(request.form.get('category_id', expense.category_id))
        expense.note = request.form.get('note', expense.note or '').strip()
        date_str = request.form.get('expense_date', '')
        if date_str:
            expense.expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        db.session.commit()
        flash('Expense updated.', 'success')
    except (ValueError, TypeError):
        flash('Invalid data.', 'error')

    return redirect(url_for('expenses.index'))


@expenses_bp.route('/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted.', 'success')
    return redirect(url_for('expenses.index'))


@expenses_bp.route('/data')
@login_required
def data():
    period = request.args.get('period', '3m')
    expenses = _get_filtered_expenses(current_user.id, period)
    return jsonify([e.to_dict() for e in expenses])


def _get_filtered_expenses(user_id, period, date_from='', date_to=''):
    from datetime import timedelta
    today = date.today()

    if period == 'custom' and date_from and date_to:
        try:
            start = datetime.strptime(date_from, '%Y-%m-%d').date()
            end   = datetime.strptime(date_to,   '%Y-%m-%d').date()
            return (Expense.query
                    .filter(Expense.user_id == user_id,
                            Expense.expense_date >= start,
                            Expense.expense_date <= end)
                    .order_by(Expense.expense_date.desc())
                    .all())
        except ValueError:
            pass

    if period == '3m':
        start = today.replace(day=1) - timedelta(days=60)
    elif period == '6m':
        start = today.replace(day=1) - timedelta(days=150)
    elif period == '1y':
        start = today.replace(day=1) - timedelta(days=335)
    else:
        start = date(2000, 1, 1)

    return (Expense.query
            .filter(Expense.user_id == user_id, Expense.expense_date >= start)
            .order_by(Expense.expense_date.desc())
            .all())
