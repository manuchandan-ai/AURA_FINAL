"""AURA User Service.

Handles user CRUD operations, profile management, and status updates.
"""

import logging
from database.db import query_db, execute_db
from app.services.auth_service import hash_password

logger = logging.getLogger(__name__)


def create_user(email, password, name, phone=None):
    """Create a new user with pending status.

    Also creates an empty user_profiles record.

    Args:
        email: User email (unique).
        password: Plain text password (will be hashed).
        name: User's full name.
        phone: Optional phone number.

    Returns:
        int: New user's ID.

    Raises:
        Exception: If email already exists or DB error.
    """
    password_hash = hash_password(password)
    user_id = execute_db(
        'INSERT INTO users (email, password_hash, name, phone, status, role) VALUES (?, ?, ?, ?, ?, ?)',
        (email, password_hash, name, phone, 'pending', 'user')
    )
    # Create associated profile record
    execute_db(
        'INSERT INTO user_profiles (user_id) VALUES (?)',
        (user_id,)
    )
    logger.info("New user created: %s (id=%d, status=pending)", email, user_id)
    return user_id


def get_user_by_email(email):
    """Find a user by email address.

    Args:
        email: Email to search for.

    Returns:
        sqlite3.Row or None: User record if found.
    """
    return query_db('SELECT * FROM users WHERE email = ?', (email,), one=True)


def get_user_by_id(user_id):
    """Find a user by ID.

    Args:
        user_id: User's integer ID.

    Returns:
        sqlite3.Row or None: User record if found.
    """
    return query_db('SELECT * FROM users WHERE id = ?', (user_id,), one=True)


def get_user_profile(user_id):
    """Get a user's profile.

    Args:
        user_id: User's integer ID.

    Returns:
        sqlite3.Row or None: Profile record if found.
    """
    return query_db('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,), one=True)


def update_user_profile(user_id, **kwargs):
    """Update user profile fields.

    Only updates fields that are in the allowed list.

    Args:
        user_id: User's integer ID.
        **kwargs: Field=value pairs to update.
    """
    allowed_fields = ['address', 'city', 'state', 'pincode', 'country', 'profile_photo', 'bio']
    updates = []
    values = []

    for field, value in kwargs.items():
        if field in allowed_fields and value is not None:
            updates.append(f'{field} = ?')
            values.append(value)

    if updates:
        values.append(user_id)
        query = f"UPDATE user_profiles SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?"
        execute_db(query, tuple(values))
        logger.info("Profile updated for user_id=%d: %s", user_id, list(kwargs.keys()))


def update_user_name(user_id, name):
    """Update user's display name."""
    execute_db(
        'UPDATE users SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (name, user_id)
    )


def update_user_phone(user_id, phone):
    """Update user's phone number."""
    execute_db(
        'UPDATE users SET phone = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (phone, user_id)
    )


def get_all_users():
    """Get all users (for admin). Returns list ordered by creation date."""
    return query_db('SELECT * FROM users ORDER BY created_at DESC')


def get_users_by_status(status):
    """Get users filtered by status."""
    return query_db('SELECT * FROM users WHERE status = ? ORDER BY created_at DESC', (status,))


def update_user_status(user_id, new_status):
    """Update a user's account status.

    Args:
        user_id: User's integer ID.
        new_status: New status (approved, rejected, waitlisted, banned, removed).
    """
    valid_statuses = ['pending', 'approved', 'rejected', 'waitlisted', 'banned', 'removed']
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status: {new_status}. Must be one of {valid_statuses}")

    execute_db(
        'UPDATE users SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (new_status, user_id)
    )
    logger.info("User %d status changed to %s", user_id, new_status)


def email_exists(email):
    """Check if an email is already registered."""
    result = query_db('SELECT id FROM users WHERE email = ?', (email,), one=True)
    return result is not None
