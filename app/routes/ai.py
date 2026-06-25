from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from app import db
from app.models.ai_insight import AIInsight
from app.services.ai_service import generate_insights

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')


@ai_bp.route('/insights')
@login_required
def insights():
    all_insights = (AIInsight.query
                    .filter_by(user_id=current_user.id)
                    .order_by(AIInsight.generated_at.desc())
                    .limit(20)
                    .all())
    return render_template('ai/insights.html', insights=all_insights)


@ai_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    if not current_user.settings or not current_user.settings.ai_alerts_enabled:
        return jsonify({'error': 'AI alerts are disabled.'}), 403

    new_insights = generate_insights(current_user)
    return jsonify({'insights': [i.to_dict() for i in new_insights]})


@ai_bp.route('/insights/data')
@login_required
def insights_data():
    all_insights = (AIInsight.query
                    .filter_by(user_id=current_user.id)
                    .order_by(AIInsight.generated_at.desc())
                    .limit(10)
                    .all())
    return jsonify([i.to_dict() for i in all_insights])


@ai_bp.route('/insights/<int:insight_id>/read', methods=['POST'])
@login_required
def mark_read(insight_id):
    insight = AIInsight.query.filter_by(id=insight_id, user_id=current_user.id).first_or_404()
    insight.is_read = True
    db.session.commit()
    return jsonify({'ok': True})
