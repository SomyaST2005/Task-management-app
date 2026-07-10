from flask import Blueprint, render_template, session
from routes.db import get_db
from routes.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute('SELECT COUNT(*) as count FROM employees')
        total_employees = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM tasks')
        total_tasks = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'Pending'")
        pending_tasks = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'In Progress'")
        in_progress_tasks = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'Completed'")
        completed_tasks = cursor.fetchone()['count']

        cursor.execute(
            '''SELECT t.*, e.name as employee_name
               FROM tasks t
               JOIN employees e ON t.employee_id = e.id
               ORDER BY t.created_at DESC LIMIT 5'''
        )
        recent_tasks = cursor.fetchall()

        cursor.execute(
            '''SELECT t.*, e.name as employee_name
               FROM tasks t
               JOIN employees e ON t.employee_id = e.id
               WHERE t.due_date >= CURDATE() AND t.status != 'Completed'
               ORDER BY t.due_date ASC LIMIT 5'''
        )
        upcoming_deadlines = cursor.fetchall()

        return render_template(
            'admin/dashboard.html',
            total_employees=total_employees,
            total_tasks=total_tasks,
            pending_tasks=pending_tasks,
            in_progress_tasks=in_progress_tasks,
            completed_tasks=completed_tasks,
            recent_tasks=recent_tasks,
            upcoming_deadlines=upcoming_deadlines,
        )
    finally:
        cursor.close()
        conn.close()
