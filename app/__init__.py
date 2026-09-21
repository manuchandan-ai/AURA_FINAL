"""AURA Flask Application Factory."""

import os
from flask import Flask
from app.config import config_map, BASE_DIR


def create_app(config_name=None):
    """Create and configure the Flask application.
    
    Args:
        config_name: Configuration to use ('development', 'production', or 'default').
    
    Returns:
        Configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, 'frontend', 'templates'),
        static_folder=os.path.join(BASE_DIR, 'frontend', 'static')
    )

    # Load configuration
    app.config.from_object(config_map.get(config_name, config_map['default']))

    # Ensure required directories exist
    os.makedirs(app.config.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads')), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'database'), exist_ok=True)

    # Initialize database
    from database.db import init_app as init_db_app
    init_db_app(app)

    # Register blueprints
    _register_blueprints(app)

    return app


def _register_blueprints(app):
    """Register all Flask blueprints."""
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.api import api_bp
    app.register_blueprint(api_bp)
