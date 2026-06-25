import json
import logging
import requests
from flask import current_app
from app import db
from app.models.ai_insight import AIInsight
from app.services.analytics_service import get_dashboard_summary, get_monthly_trends

logger = logging.getLogger(__name__)


def generate_insights(user):
    summary = get_dashboard_summary(user)
    trends = get_monthly_trends(user)

    category_text = ', '.join(
        f"{c['category']}: {user.currency} {c['amount']:.0f} ({c['percentage']}%)"
        for c in summary['category_breakdown']
    ) or 'No expenses this month'

    trend_text = ', '.join(
        f"{t['month']}: {user.currency} {t['total']:.0f}"
        for t in trends
    )

    prompt = f"""Analyze this user's monthly spending data and provide brief financial insights.

Monthly Budget: {user.currency} {summary['monthly_budget']:.0f}
Total Spent: {user.currency} {summary['total_spent']:.0f}
Remaining: {user.currency} {summary['remaining']:.0f}
Savings Goal: {user.currency} {summary['saving_goal']:.0f}
Category Breakdown: {category_text}
6-Month Trend: {trend_text}

Provide exactly 3 insights in this JSON format:
[
  {{"type": "warning", "title": "short title", "message": "one sentence insight", "priority": "high"}},
  {{"type": "suggestion", "title": "short title", "message": "one sentence insight", "priority": "medium"}},
  {{"type": "prediction", "title": "short title", "message": "one sentence insight", "priority": "low"}}
]

Only return valid JSON. No markdown, no extra text."""

    api_key = current_app.config.get('OPENROUTER_API_KEY', '')
    if not api_key or api_key == 'your-openrouter-api-key-here':
        logger.warning('OpenRouter API key not set — using fallback insights.')
        return _fallback_insights(user, summary)

    model = current_app.config.get('OPENROUTER_MODEL', 'openai/gpt-oss-20b:free')

    try:
        response = requests.post(
            f"{current_app.config['OPENROUTER_BASE_URL']}/chat/completions",
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://budget-buddy-ai.local',
                'X-Title': 'Budget Buddy AI',
            },
            json={
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 600,
                'temperature': 0.4,
            },
            timeout=20,
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content'].strip()

        # Strip markdown code fences if the model wraps the JSON
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
            content = content.strip()

        parsed = json.loads(content)
        if not isinstance(parsed, list):
            raise ValueError('Expected a JSON array from the model.')

        logger.info('AI insights generated via OpenRouter (%s).', model)
        return _save_insights(user, parsed)

    except requests.HTTPError as e:
        logger.error('OpenRouter HTTP error %s: %s', e.response.status_code, e.response.text)
        return _fallback_insights(user, summary)
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.error('OpenRouter response parse error: %s', e)
        return _fallback_insights(user, summary)
    except requests.RequestException as e:
        logger.error('OpenRouter request failed: %s', e)
        return _fallback_insights(user, summary)


def _save_insights(user, parsed_list):
    saved = []
    for item in parsed_list[:3]:
        insight = AIInsight(
            user_id=user.id,
            insight_type=item.get('type', 'suggestion'),
            title=item.get('title', 'Insight'),
            message=item.get('message', ''),
            priority=item.get('priority', 'medium'),
        )
        db.session.add(insight)
        saved.append(insight)
    db.session.commit()
    return saved


def _fallback_insights(user, summary):
    insights_data = []
    spent = summary['total_spent']
    budget = summary['monthly_budget']
    remaining = summary['remaining']

    if budget > 0 and spent > budget * 0.9:
        insights_data.append({
            'type': 'warning',
            'title': 'Budget Alert',
            'message': f"You've used {summary['budget_used_pct']}% of your monthly budget — watch your spending for the rest of the month.",
            'priority': 'high',
        })
    else:
        insights_data.append({
            'type': 'suggestion',
            'title': 'On Track',
            'message': f"You have {user.currency} {remaining:.0f} remaining this month — great budget discipline!",
            'priority': 'medium',
        })

    if summary['category_breakdown']:
        top = summary['category_breakdown'][0]
        insights_data.append({
            'type': 'suggestion',
            'title': f"{top['category']} Spending",
            'message': f"{top['category']} is your highest category at {top['percentage']}% of total spending — consider setting a category limit.",
            'priority': 'medium',
        })

    insights_data.append({
        'type': 'prediction',
        'title': 'Month-End Projection',
        'message': f"At your current pace, you'll spend approximately {user.currency} {spent * 30 / max(1, __import__('datetime').date.today().day):.0f} this month.",
        'priority': 'low',
    })

    return _save_insights(user, insights_data)
