"""Authentication routes — register, login, logout, profile."""

import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.auth_service import check_password, login_required
from app.services.user_service import (
    create_user, get_user_by_email, get_user_by_id,
    get_user_profile, update_user_profile,
    update_user_name, update_user_phone, email_exists
)

auth_bp = Blueprint('auth', __name__)


def _validate_email(email):
    """Basic email format validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if 'user_id' in session:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        # Collect form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Profile fields
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        country = request.form.get('country', '').strip() or 'India'

        # Validation
        errors = []
        if not name:
            errors.append('Name is required.')
        if not email:
            errors.append('Email is required.')
        elif not _validate_email(email):
            errors.append('Please enter a valid email address.')
        if not password:
            errors.append('Password is required.')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if email_exists(email):
            errors.append('This email is already registered.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html',
                                   form_data=request.form)

        try:
            user_id = create_user(email, password, name, phone or None)

            # Save profile fields
            profile_data = {}
            if address:
                profile_data['address'] = address
            if city:
                profile_data['city'] = city
            if state:
                profile_data['state'] = state
            if pincode:
                profile_data['pincode'] = pincode
            if country:
                profile_data['country'] = country

            if profile_data:
                update_user_profile(user_id, **profile_data)

            flash('Registration successful! Your account is pending admin approval.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash('Registration failed. Please try again.', 'danger')
            return render_template('register.html',
                                   form_data=request.form)

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if 'user_id' in session:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html')

        user = get_user_by_email(email)

        if not user or not check_password(password, user['password_hash']):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')

        # Check account status
        if user['status'] in ('banned', 'removed'):
            flash('Your account has been suspended. Please contact the administrator.', 'danger')
            return render_template('login.html')

        if user['status'] == 'rejected':
            flash('Your registration was not approved. Please contact the administrator.', 'danger')
            return render_template('login.html')

        # Set session data
        session.clear()
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        session['user_role'] = user['role']
        session['user_status'] = user['status']
        session.permanent = True

        # Redirect based on status
        if user['status'] in ('pending', 'waitlisted'):
            status_msg = 'pending admin approval' if user['status'] == 'pending' else 'on the waiting list'
            flash(f'Welcome, {user["name"]}! Your account is {status_msg}.', 'info')
            return redirect(url_for('auth.pending'))

        flash(f'Welcome back, {user["name"]}!', 'success')
        next_url = request.args.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('main.home'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Log out the current user."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/pending')
@login_required
def pending():
    """Pending approval page for unapproved users."""
    user = get_user_by_id(session['user_id'])
    if user and user['status'] == 'approved':
        return redirect(url_for('main.home'))
    return render_template('pending.html', user=user)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile view and edit."""
    user = get_user_by_id(session['user_id'])
    user_profile = get_user_profile(session['user_id'])

    if request.method == 'POST':
        # Update name and phone on users table
        new_name = request.form.get('name', '').strip()
        new_phone = request.form.get('phone', '').strip()

        if new_name and new_name != user['name']:
            update_user_name(session['user_id'], new_name)
            session['user_name'] = new_name

        if new_phone != (user['phone'] or ''):
            update_user_phone(session['user_id'], new_phone or None)

        # Update profile fields
        profile_data = {}
        for field in ['address', 'city', 'state', 'pincode', 'country', 'bio']:
            val = request.form.get(field, '').strip()
            profile_data[field] = val if val else None

        update_user_profile(session['user_id'], **profile_data)

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('profile.html', user=user, profile=user_profile)
