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


@api_bp.route('/chat', methods=['POST'])
@api_login_required
def chat():
    """Execute the AURA intelligence LLM pipeline with memory."""
    user_id = session.get('user_id')
    
    text = request.form.get('text', '').strip()
    conversation_id = request.form.get('conversation_id')
    
    if not text:
        return jsonify({'status': 'error', 'message': 'No input provided.'}), 400
        
    from database.db import query_db, execute_db
    from intelligence.llm_core import process_chat
    
    # 1. Create or verify conversation
    if not conversation_id:
        # Create new
        title = text[:30] + "..." if len(text) > 30 else text
        conversation_id = execute_db(
            'INSERT INTO conversations (user_id, title) VALUES (?, ?)',
            (user_id, title)
        )
    else:
        # Verify ownership
        conv = query_db('SELECT id FROM conversations WHERE id = ? AND user_id = ?', (conversation_id, user_id), one=True)
        if not conv:
            return jsonify({'status': 'error', 'message': 'Conversation not found.'}), 404
            
    # 2. Save User Message
    execute_db(
        'INSERT INTO messages (conversation_id, sender, content) VALUES (?, ?, ?)',
        (conversation_id, 'user', text)
    )
    
    # 3. Process LLM Logic
    result = process_chat(user_id, conversation_id, text)
    
    # 4. Save AURA Message
    execute_db(
        'INSERT INTO messages (conversation_id, sender, content, metadata) VALUES (?, ?, ?, ?)',
        (conversation_id, 'aura', result.get('response', ''), json.dumps({
            'module': result.get('module'),
            'confidence': result.get('confidence'),
            'decision': result.get('decision')
        }))
    )
    
    # 5. Handle Goals
    new_goal = result.get('new_goal')
    if new_goal:
        execute_db(
            'INSERT INTO goals (user_id, title, description, roadmap) VALUES (?, ?, ?, ?)',
            (user_id, new_goal.get('title'), new_goal.get('description'), new_goal.get('roadmap'))
        )
    
    return jsonify({
        'status': 'success',
        'conversation_id': conversation_id,
        'module': result.get('module', 'AURA Core'),
        'confidence': result.get('confidence', 0),
        'decision': result.get('decision', ''),
        'explanation': result.get('response', '')
    })


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
            'date': r['created_at'],
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

@api_bp.route('/goals', methods=['GET'])
@api_login_required
def get_goals():
    """Fetch user's active goals."""
    user_id = session.get('user_id')
    rows = query_db('SELECT id, title, description, progress, status FROM goals WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    goals = [dict(r) for r in rows]
    return jsonify({'status': 'success', 'goals': goals})
    
@api_bp.route('/reminders', methods=['GET'])
@api_login_required
def get_reminders():
    """Fetch user's active reminders."""
    user_id = session.get('user_id')
    rows = query_db('SELECT id, task, priority, due_date FROM reminders WHERE user_id = ? AND is_completed = 0 ORDER BY due_date ASC', (user_id,))
    reminders = [dict(r) for r in rows]
    return jsonify({'status': 'success', 'reminders': reminders})
