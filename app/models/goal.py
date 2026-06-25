from datetime import datetime, timezone
from app import db


class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    goal_type = db.Column(db.String(50), default='savings')  # savings / investment / emergency / vacation
    target_amount = db.Column(db.Numeric(12, 2), nullable=False)
    current_amount = db.Column(db.Numeric(12, 2), default=0)
    monthly_contribution = db.Column(db.Numeric(12, 2), default=0)
    target_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')  # active / completed / paused
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    @property
    def progress_percent(self):
        if self.target_amount == 0:
            return 0
        return min(100, round(float(self.current_amount) / float(self.target_amount) * 100, 1))

    @property
    def amount_remaining(self):
        return max(0, float(self.target_amount) - float(self.current_amount))

    @property
    def months_to_goal(self):
        contrib = float(self.monthly_contribution or 0)
        if contrib <= 0 or self.amount_remaining <= 0:
            return None
        import math
        return math.ceil(self.amount_remaining / contrib)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'goal_type': self.goal_type,
            'target_amount': float(self.target_amount),
            'current_amount': float(self.current_amount),
            'monthly_contribution': float(self.monthly_contribution or 0),
            'progress_percent': self.progress_percent,
            'amount_remaining': self.amount_remaining,
            'months_to_goal': self.months_to_goal,
            'status': self.status,
            'target_date': self.target_date.strftime('%Y-%m-%d') if self.target_date else None,
        }

    def __repr__(self):
        return f'<Goal {self.name}>'
