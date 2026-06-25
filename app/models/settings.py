from datetime import datetime, timezone
from app import db


class UserSettings(db.Model):
    __tablename__ = 'user_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    monthly_budget = db.Column(db.Numeric(12, 2), default=0)
    monthly_saving_goal = db.Column(db.Numeric(12, 2), default=0)
    monthly_investing_goal = db.Column(db.Numeric(12, 2), default=0)
    ai_alerts_enabled = db.Column(db.Boolean, default=True)
    notifications_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<UserSettings user_id={self.user_id}>'
