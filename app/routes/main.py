"""Main routes — home page, health check, public pages."""

from flask import Blueprint, render_template, jsonify, current_app

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """Render the AURA home page."""
    return render_template('home.html')


@main_bp.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'service': current_app.config.get('AURA_NAME', 'AURA'),
        'version': current_app.config.get('AURA_VERSION', '1.0.0')
    })


@main_bp.route('/about')
def about():
    """Render the about page."""
    return render_template('home.html')  # Temporary - will get its own template later
