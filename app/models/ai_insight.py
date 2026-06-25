from datetime import datetime, timezone
from app import db


class AIInsight(db.Model):
    __tablename__ = 'ai_insights'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    insight_type = db.Column(db.String(50))  # warning / suggestion / prediction / saving
    title = db.Column(db.String(150))
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low / medium / high
    is_read = db.Column(db.Boolean, default=False)
    generated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.insight_type,
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'is_read': self.is_read,
            'generated_at': self.generated_at.strftime('%d %b %Y'),
        }

    def __repr__(self):
        return f'<AIInsight {self.insight_type}: {self.title}>'
