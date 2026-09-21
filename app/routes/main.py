"""Main routes — home page, health check, public pages."""

from flask import Blueprint, render_template, jsonify, current_app, request

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


@main_bp.route('/api/analyze', methods=['POST'])
def analyze():
    """Execute the AURA intelligence pipeline."""
    from intelligence.core.pipeline import IntelligencePipeline
    from flask import session
    
    # Get user_id if logged in
    user_id = session.get('user_id')
    if not user_id:
        # Fallback to the first available admin for testing purposes
        from database.db import query_db
        admin = query_db('SELECT id FROM users WHERE role="admin" LIMIT 1', one=True)
        if admin:
            user_id = admin['id']
        else:
            return jsonify({'status': 'error', 'message': 'No valid user found for analysis.'})
    
    text = request.form.get('text', '').strip()
    url = request.form.get('url', '').strip()
    
    # Handle file upload (mock for now, just getting filename)
    filename = None
    if 'file' in request.files:
        file = request.files['file']
        if file.filename:
            filename = file.filename
            
    if not text and not url and not filename:
        return jsonify({'status': 'error', 'message': 'No input provided.'})
        
    pipeline = IntelligencePipeline()
    result = pipeline.process(user_id=user_id, text=text, filename=filename, url=url)
    
    # Map the dictionary to match the UI expectations
    if result.get('status') == 'success':
        return jsonify({
            'status': 'success',
            'module': result.get('module', 'AURA Core'),
            'confidence': result.get('confidence', 0),
            'signals': result.get('signals', []),
            'decision': result.get('decision', ''),
            'explanation': result.get('explanation', '')
        })
    else:
        return jsonify(result)
