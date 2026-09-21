"""Admin routes — dashboard, user management, system settings."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.auth_service import admin_required
from app.services.user_service import get_all_users, get_users_by_status, update_user_status, get_user_by_id
from app.services.admin_service import get_dashboard_stats, log_admin_action, get_recent_admin_actions

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with high-level statistics."""
    stats = get_dashboard_stats()
    recent_actions = get_recent_admin_actions(limit=5)
    return render_template('admin/dashboard.html', stats=stats, recent_actions=recent_actions)


@admin_bp.route('/users')
@admin_required
def users():
    """List and filter users."""
    status_filter = request.args.get('status')
    
    if status_filter and status_filter in ['pending', 'approved', 'waitlisted', 'banned', 'rejected']:
        user_list = get_users_by_status(status_filter)
    else:
        user_list = get_all_users()
        
    return render_template('admin/users.html', users=user_list, current_filter=status_filter)


@admin_bp.route('/users/<int:user_id>/status', methods=['POST'])
@admin_required
def change_user_status(user_id):
    """Change a user's status (approve, reject, ban, etc)."""
    new_status = request.form.get('status')
    valid_statuses = ['pending', 'approved', 'rejected', 'waitlisted', 'banned', 'removed']
    
    if new_status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin.users'))
        
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users'))
        
    # Don't allow changing your own status from here
    if user_id == session.get('user_id'):
        flash('Cannot change your own status.', 'warning')
        return redirect(url_for('admin.users'))
        
    try:
        update_user_status(user_id, new_status)
        log_admin_action(
            session.get('user_id'),
            f'status_change_{new_status}',
            user_id,
            f"Status changed from {user['status']} to {new_status}"
        )
        flash(f"User {user['name']} status updated to {new_status}.", 'success')
    except Exception as e:
        flash(f'Error updating status: {str(e)}', 'danger')
        
    return redirect(request.referrer or url_for('admin.users'))
