"""AURA Admin Service.

Handles administrative actions, statistics, and audit logging.
"""

import logging
from database.db import query_db, execute_db

logger = logging.getLogger(__name__)


def get_dashboard_stats():
    """Get system statistics for the admin dashboard.
    
    Returns:
        dict: Statistics including user counts by status.
    """
    stats = {
        'total_users': 0,
        'pending_users': 0,
        'approved_users': 0,
        'banned_users': 0,
        'total_analyses': 0
    }
    
    # User stats
    rows = query_db('SELECT status, COUNT(*) as count FROM users GROUP BY status')
    for row in rows:
        stats['total_users'] += row['count']
        if row['status'] == 'pending':
            stats['pending_users'] = row['count']
        elif row['status'] == 'approved':
            stats['approved_users'] = row['count']
        elif row['status'] == 'banned':
            stats['banned_users'] = row['count']
            
    # Analysis stats
    analysis_count = query_db('SELECT COUNT(*) as count FROM analysis_history', one=True)
    if analysis_count:
        stats['total_analyses'] = analysis_count['count']
        
    return stats


def log_admin_action(admin_id, action_type, target_user_id=None, details=None):
    """Log an administrative action.
    
    Args:
        admin_id: ID of the admin performing the action.
        action_type: String identifier for the action (e.g., 'approve_user').
        target_user_id: Optional ID of the user affected.
        details: Optional string with more context.
    """
    execute_db(
        'INSERT INTO admin_actions (admin_id, action_type, target_user_id, details) VALUES (?, ?, ?, ?)',
        (admin_id, action_type, target_user_id, details)
    )
    logger.info("Admin %d performed %s on user %s", admin_id, action_type, target_user_id)


def get_recent_admin_actions(limit=10):
    """Get recent admin audit logs.
    
    Returns:
        list: Recent admin actions with admin and target user details.
    """
    query = '''
        SELECT a.*, 
               admin.name as admin_name, admin.email as admin_email,
               target.name as target_name, target.email as target_email
        FROM admin_actions a
        JOIN users admin ON a.admin_id = admin.id
        LEFT JOIN users target ON a.target_user_id = target.id
        ORDER BY a.created_at DESC
        LIMIT ?
    '''
    return query_db(query, (limit,))
