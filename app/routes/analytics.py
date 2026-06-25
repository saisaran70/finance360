from datetime import date
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.services.analytics_service import (
    get_category_breakdown, get_monthly_trends, get_fixed_cost_analysis,
    get_projected_spend, get_goal_analytics, get_spending_savings_trend,
)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/')
@login_required
def index():
    projected = get_projected_spend(current_user)
    goals = get_goal_analytics(current_user)
    return render_template('analytics/index.html',
                           now=date.today(),
                           projected=projected,
                           goals=goals)


@analytics_bp.route('/categories')
@login_required
def categories():
    return jsonify(get_category_breakdown(current_user))


@analytics_bp.route('/trends')
@login_required
def trends():
    return jsonify(get_monthly_trends(current_user))


@analytics_bp.route('/fixed-costs')
@login_required
def fixed_costs():
    return jsonify(get_fixed_cost_analysis(current_user))


@analytics_bp.route('/spending-savings')
@login_required
def spending_savings():
    range_key = request.args.get('range', '6m')
    if range_key not in ('7d', '30d', '6m', '1y'):
        range_key = '6m'
    return jsonify(get_spending_savings_trend(current_user, range_key))


@analytics_bp.route('/ai-insights')
@login_required
def ai_insights():
    from app.models.ai_insight import AIInsight
    insights = (AIInsight.query
                .filter_by(user_id=current_user.id)
                .order_by(AIInsight.generated_at.desc())
                .limit(4)
                .all())
    return jsonify([i.to_dict() for i in insights])
