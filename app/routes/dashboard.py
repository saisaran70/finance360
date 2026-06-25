from datetime import date
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.expense import ExpenseCategory
from app.services.analytics_service import get_dashboard_summary, get_chart_data

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    summary = get_dashboard_summary(current_user)
    categories = ExpenseCategory.query.all()
    return render_template('dashboard/index.html', summary=summary,
                           categories=categories, today=date.today().isoformat())


@dashboard_bp.route('/dashboard/summary')
@login_required
def summary():
    return jsonify(get_dashboard_summary(current_user))


@dashboard_bp.route('/dashboard/charts')
@login_required
def charts():
    return jsonify(get_chart_data(current_user))
