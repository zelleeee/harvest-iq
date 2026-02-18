from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models.user import User
from app.utils.validators import validate_password_strength, validate_phone

auth_bp = Blueprint('auth', __name__)


# ─── LOGIN ────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Validate credentials
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=bool(remember))
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')


# ─── REGISTER ─────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        role = request.form.get('role', 'buyer')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        region = request.form.get('region', '')

        # Validate passwords match
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        # Validate password strength
        valid, msg = validate_password_strength(password)
        if not valid:
            flash(msg, 'danger')
            return render_template('auth/register.html')

        # Validate phone number format
        if phone and not validate_phone(phone):
            flash('Invalid phone number format. Use: 09XXXXXXXXX', 'danger')
            return render_template('auth/register.html')

        # For buyers, email is required
        if role == 'buyer' and not email:
            flash('Email is required for buyers.', 'danger')
            return render_template('auth/register.html')

        # Check if email already exists (only if email is provided)
        if email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('Email already registered.', 'danger')
                return render_template('auth/register.html')

        # Check if username already exists
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already taken.', 'danger')
            return render_template('auth/register.html')

        # For farmers without email, generate a unique placeholder email
        if role == 'farmer' and not email:
            email = f"{username}@harvestiq.local"

        # Create new user
        user = User(
            username=username,
            email=email,
            role=role,
            full_name=full_name,
            phone=phone,
            region=region
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()

        # Auto-login after registration
        login_user(user)
        flash('Account created! Welcome to Harvest IQ!', 'success')
        return redirect(url_for('users.dashboard'))
    
    return render_template('auth/register.html')


# ─── LOGOUT ───────────────────────────────────────────────────────────────────

@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# ─── PASSWORD RESET (Optional - Placeholder) ──────────────────────────────────

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page (placeholder for future implementation)."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        
        if user:
            # TODO: Implement email sending with reset token
            flash('Password reset instructions have been sent to your email.', 'info')
        else:
            # Don't reveal if email exists or not (security best practice)
            flash('If that email exists, password reset instructions have been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token (placeholder for future implementation)."""
    # TODO: Implement token verification and password reset
    flash('Password reset feature coming soon!', 'info')
    return redirect(url_for('auth.login'))


# ─── EMAIL VERIFICATION (Optional - Placeholder) ──────────────────────────────

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify email with token (placeholder for future implementation)."""
    # TODO: Implement email verification
    flash('Email verification feature coming soon!', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/resend-verification')
@login_required
def resend_verification():
    """Resend verification email (placeholder)."""
    if current_user.is_verified:
        flash('Your email is already verified.', 'info')
    else:
        # TODO: Implement verification email sending
        flash('Verification email sent!', 'success')
    return redirect(url_for('users.profile'))