from datetime import datetime, timezone, date
from app import db


class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(20), default='#94A3B8')
    icon = db.Column(db.String(50), default='circle')

    expenses = db.relationship('Expense', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'

    @staticmethod
    def seed_defaults():
        defaults = [
            ('Food',          '#5EF2D6', 'utensils'),
            ('Transport',     '#5BA8FF', 'car'),
            ('Shopping',      '#F59DB1', 'shopping-bag'),
            ('Bills',         '#F7D154', 'receipt'),
            ('Entertainment', '#A78BFA', 'film'),
            ('Health',        '#FCA5A5', 'heart'),
            ('Education',     '#60DBFF', 'book'),
            ('Others',        '#94A3B8', 'circle'),
        ]
        for name, color, icon in defaults:
            if not ExpenseCategory.query.filter_by(name=name).first():
                db.session.add(ExpenseCategory(name=name, color=color, icon=icon))
        db.session.commit()


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    note = db.Column(db.Text)
    expense_date = db.Column(db.Date, nullable=False, default=date.today)
    is_recurring = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    _ICON_EMOJI = {
        'utensils': '🍽️', 'car': '🚗', 'shopping-bag': '🛍️',
        'receipt': '⚡', 'film': '🎬', 'heart': '💊',
        'book': '📚', 'circle': '📦', 'target': '🎯',
    }

    def to_dict(self):
        icon_name = self.category.icon if self.category else 'circle'
        return {
            'id': self.id,
            'amount': float(self.amount),
            'category': self.category.name if self.category else 'Other',
            'category_color': self.category.color if self.category else '#94A3B8',
            'category_icon': self._ICON_EMOJI.get(icon_name, '📦'),
            'note': self.note or '',
            'date': self.expense_date.strftime('%Y-%m-%d'),
            'date_display': self.expense_date.strftime('%d %b %Y'),
        }

    def __repr__(self):
        return f'<Expense {self.amount} - {self.category_id}>'
