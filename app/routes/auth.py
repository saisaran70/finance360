from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, oauth
from app.models.user import User
from app.models.settings import UserSettings

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()
        if user and user.is_oauth_user:
            flash('This account uses Google Sign-In. Use the button below.', 'error')
        elif user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not full_name or not email or not password:
            flash('All fields are required.', 'error')
        elif password != confirm:
            flash('Passwords do not match.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
        else:
            user = User(full_name=full_name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            settings = UserSettings(user_id=user.id, monthly_budget=0, monthly_saving_goal=0)
            db.session.add(settings)
            db.session.commit()

            login_user(user)
            flash(f'Welcome, {full_name}! Set up your monthly budget to get started.', 'success')
            return redirect(url_for('settings.index'))

    return render_template('auth/register.html')


@auth_bp.route('/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/google/callback')
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')

    if not user_info:
        flash('Google sign-in failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

    google_id = user_info['sub']
    email = user_info['email'].lower()
    name = user_info.get('name') or email.split('@')[0]

    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            # Link Google to existing email/password account
            user.google_id = google_id
            db.session.commit()
        else:
            # Brand new user — auto-register
            user = User(full_name=name, email=email,
                        google_id=google_id, password_hash='OAUTH:google')
            db.session.add(user)
            db.session.flush()
            settings = UserSettings(user_id=user.id, monthly_budget=0, monthly_saving_goal=0)
            db.session.add(settings)
            db.session.commit()
            flash(f'Welcome, {name}! Set up your monthly budget to get started.', 'success')

    login_user(user, remember=True)
    return redirect(url_for('dashboard.index'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
