"""AURA Authentication Service.

Handles password hashing, verification, and route protection decorators.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    """Hash a password using werkzeug's PBKDF2.

    Args:
        password: Plain text password.

    Returns:
        str: Hashed password string.
    """
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)


def check_password(password, password_hash):
    """Verify a password against its hash.

    Args:
        password: Plain text password to check.
        password_hash: Stored hash to compare against.

    Returns:
        bool: True if password matches.
    """
    return check_password_hash(password_hash, password)


def get_current_user_id():
    """Get the current logged-in user's ID from session.

    Returns:
        int or None: User ID if logged in, None otherwise.
    """
    return session.get('user_id')


def is_logged_in():
    """Check if a user is currently logged in."""
    return 'user_id' in session


def login_required(f):
    """Decorator to protect routes that require authentication.

    Redirects to login page if user is not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def approved_required(f):
    """Decorator for routes that require approved user status.

    Checks both authentication and approval status.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('user_status') != 'approved':
            flash('Your account is pending approval. Please wait for admin confirmation.', 'info')
            return redirect(url_for('auth.pending'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator for routes that require admin role.

    Checks authentication, approval status, and admin role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('user_role') != 'admin':
            flash('Administrator access required.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function
