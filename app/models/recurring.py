from datetime import datetime, timezone
from app import db


class RecurringExpense(db.Model):
    __tablename__ = 'recurring_expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly / yearly / weekly
    next_due_date = db.Column(db.Date)
    auto_add = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    category = db.relationship('ExpenseCategory', backref='recurring_expenses')

    def __repr__(self):
        return f'<RecurringExpense {self.title}>'
