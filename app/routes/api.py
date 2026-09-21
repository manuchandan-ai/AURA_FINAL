"""API routes for AURA Intelligence Core."""

import json
from functools import wraps
from flask import Blueprint, request, jsonify, session
from database.db import query_db
from intelligence.core.pipeline import IntelligencePipeline

api_bp = Blueprint('api', __name__, url_prefix='/api')

def api_login_required(f):
    """Decorator for API routes that require authentication.
    
    Returns 401 JSON instead of redirecting.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Allow fallback for local development/testing without login
            # In production, this should strictly return 401
            from database.db import query_db
            admin = query_db('SELECT id FROM users WHERE role="admin" LIMIT 1', one=True)
            if admin:
                session['user_id'] = admin['id']
            else:
                return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


@api_bp.route('/analyze', methods=['POST'])
@api_login_required
def analyze():
    """Execute the AURA intelligence pipeline."""
    user_id = session.get('user_id')
    
    text = request.form.get('text', '').strip()
    url = request.form.get('url', '').strip()
    
    filename = None
    if 'file' in request.files:
        file = request.files['file']
        if file.filename:
            filename = file.filename
            
    if not text and not url and not filename:
        return jsonify({'status': 'error', 'message': 'No input provided.'}), 400
        
    pipeline = IntelligencePipeline()
    result = pipeline.process(user_id=user_id, text=text, filename=filename, url=url)
    
    if result.get('status') == 'success':
        return jsonify({
            'status': 'success',
            'analysis_id': result.get('analysis_id'),
            'module': result.get('module', 'AURA Core'),
            'confidence': result.get('confidence', 0),
            'signals': result.get('signals', []),
            'decision': result.get('decision', ''),
            'explanation': result.get('explanation', '')
        })
    else:
        return jsonify(result), 500


@api_bp.route('/history', methods=['GET'])
@api_login_required
def get_history():
    """Fetch user's analysis history."""
    user_id = session.get('user_id')
    limit = request.args.get('limit', 50, type=int)
    
    query = '''
        SELECT h.id, h.input_type, h.input_summary, h.detected_module, 
               h.status, h.created_at, h.confidence,
               r.decision
        FROM analysis_history h
        LEFT JOIN analysis_results r ON h.id = r.analysis_id
        WHERE h.user_id = ?
        ORDER BY h.created_at DESC
        LIMIT ?
    '''
    rows = query_db(query, (user_id, limit))
    
    history = []
    for r in rows:
        history.append({
            'id': r['id'],
            'input_type': r['input_type'],
            'input_summary': r['input_summary'],
            'module': r['detected_module'],
            'status': r['status'],
            'date': r['created_at'].strftime('%Y-%m-%d %H:%M:%S') if r['created_at'] else None,
            'confidence': round((r['confidence'] or 0) * 100, 1),
            'decision': r['decision']
        })
        
    return jsonify({'status': 'success', 'history': history})


@api_bp.route('/modules', methods=['GET'])
def get_modules():
    """Get system health and module status."""
    rows = query_db('SELECT name, slug, description, icon, is_active FROM modules')
    modules = [dict(r) for r in rows]
    return jsonify({'status': 'success', 'modules': modules})
