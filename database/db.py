"""AURA Database Helper.

Provides database connection management, initialization,
and query helper functions for the SQLite database.

Usage:
    from database.db import get_db, query_db, execute_db

    # In a Flask route:
    db = get_db()
    users = query_db('SELECT * FROM users WHERE status = ?', ['approved'])
    execute_db('INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)',
               ['user@example.com', 'Test User', 'hashed_pw'])
"""

import os
import sqlite3
import logging
from flask import g, current_app

logger = logging.getLogger(__name__)

# Path to schema file (relative to this file)
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


def get_db():
    """Get a database connection for the current request.

    Stores the connection in Flask's `g` object so that the same
    connection is reused throughout a single request.

    Returns:
        sqlite3.Connection: Active database connection with Row factory.
    """
    if 'db' not in g:
        db_path = current_app.config['DATABASE']

        # Ensure the database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Return rows as dict-like objects (access by column name)
        g.db.row_factory = sqlite3.Row
        # Enable foreign key support (off by default in SQLite)
        g.db.execute('PRAGMA foreign_keys = ON')

    return g.db


def close_db(e=None):
    """Close the database connection at the end of a request.

    Args:
        e: Optional exception (passed by Flask teardown).
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database by executing the schema SQL file.

    Creates all tables if they don't exist and seeds default data.
    Safe to call multiple times due to IF NOT EXISTS and INSERT OR IGNORE.
    """
    db = get_db()

    if not os.path.exists(SCHEMA_PATH):
        logger.error("Schema file not found: %s", SCHEMA_PATH)
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    db.executescript(schema_sql)
    db.commit()
    logger.info("Database initialized successfully from %s", SCHEMA_PATH)


def query_db(query, args=(), one=False):
    """Execute a SELECT query and return results.

    Args:
        query: SQL query string with ? placeholders.
        args: Tuple or list of parameters for the query.
        one: If True, return only the first row (or None).

    Returns:
        List of sqlite3.Row objects, or a single Row if one=True.
    """
    db = get_db()
    cursor = db.execute(query, args)
    results = cursor.fetchall()
    cursor.close()

    if one:
        return results[0] if results else None
    return results


def execute_db(query, args=()):
    """Execute an INSERT, UPDATE, or DELETE query.

    Automatically commits the transaction.

    Args:
        query: SQL query string with ? placeholders.
        args: Tuple or list of parameters for the query.

    Returns:
        int: The lastrowid for INSERT, or rowcount for UPDATE/DELETE.
    """
    db = get_db()
    cursor = db.execute(query, args)
    db.commit()
    last_id = cursor.lastrowid
    cursor.close()
    return last_id


def init_app(app):
    """Register database functions with the Flask application.

    Called during app factory setup to register:
    - Teardown handler (close_db after each request)
    - Database initialization

    Args:
        app: Flask application instance.
    """
    # Close database connection at end of each request
    app.teardown_appcontext(close_db)

    # Initialize database within app context
    with app.app_context():
        init_db()
        logger.info("AURA database ready at %s", app.config['DATABASE'])
