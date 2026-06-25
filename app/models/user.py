from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    currency = db.Column(db.String(10), default='INR')
    city = db.Column(db.String(100))
    theme_preference = db.Column(db.String(20), default='dark')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    expenses = db.relationship('Expense', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    settings = db.relationship('UserSettings', backref='user', uselist=False, cascade='all, delete-orphan')
    ai_insights = db.relationship('AIInsight', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    recurring_expenses = db.relationship('RecurringExpense', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash or self.password_hash.startswith('OAUTH:'):
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_oauth_user(self):
        return bool(self.password_hash and self.password_hash.startswith('OAUTH:'))

    def __repr__(self):
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
