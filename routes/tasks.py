from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.db import get_db
from routes.decorators import login_required, admin_required

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks_bp.route('/')
@admin_required
def list():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    priority_filter = request.args.get('priority', '').strip()
    employee_filter = request.args.get('employee_id', '').strip()

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        query = '''SELECT t.*, e.name as employee_name, e.employee_code
                   FROM tasks t
                   JOIN employees e ON t.employee_id = e.id WHERE 1=1'''
        params = []

        if search:
            query += ' AND (t.task_title LIKE %s OR t.description LIKE %s)'
            params.extend([f'%{search}%', f'%{search}%'])

        if status_filter:
            query += ' AND t.status = %s'
            params.append(status_filter)

        if priority_filter:
            query += ' AND t.priority = %s'
            params.append(priority_filter)

        if employee_filter:
            query += ' AND t.employee_id = %s'
            params.append(employee_filter)

        query += ' ORDER BY t.id DESC'
        cursor.execute(query, params)
        tasks = cursor.fetchall()

        cursor.execute('SELECT id, name, employee_code FROM employees ORDER BY name')
        all_employees = cursor.fetchall()

        return render_template(
            'tasks/list.html',
            tasks=tasks,
            search=search,
            status_filter=status_filter,
            priority_filter=priority_filter,
            employee_filter=employee_filter,
            all_employees=all_employees,
        )
    finally:
        cursor.close()
        conn.close()


@tasks_bp.route('/my-tasks')
@login_required
def my_tasks():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        employee_id = session.get('employee_id')
        if not employee_id:
            flash('No employee profile linked.', 'error')
            return redirect(url_for('auth.logout'))

        cursor.execute(
            'SELECT * FROM tasks WHERE employee_id = %s ORDER BY id DESC',
            (employee_id,)
        )
        tasks = cursor.fetchall()

        cursor.execute(
            'SELECT COUNT(*) as count FROM tasks WHERE employee_id = %s',
            (employee_id,)
        )
        total_tasks = cursor.fetchone()['count']

        cursor.execute(
            "SELECT COUNT(*) as count FROM tasks WHERE employee_id = %s AND status = 'Pending'",
            (employee_id,)
        )
        pending_tasks = cursor.fetchone()['count']

        cursor.execute(
            "SELECT COUNT(*) as count FROM tasks WHERE employee_id = %s AND status = 'In Progress'",
            (employee_id,)
        )
        in_progress_tasks = cursor.fetchone()['count']

        cursor.execute(
            "SELECT COUNT(*) as count FROM tasks WHERE employee_id = %s AND status = 'Completed'",
            (employee_id,)
        )
        completed_tasks = cursor.fetchone()['count']

        cursor.execute(
            '''SELECT * FROM tasks WHERE employee_id = %s
               AND due_date >= CURDATE() AND status != 'Completed'
               ORDER BY due_date ASC LIMIT 5''',
            (employee_id,)
        )
        upcoming_deadlines = cursor.fetchall()

        return render_template(
            'employee/dashboard.html',
            tasks=tasks,
            total_tasks=total_tasks,
            pending_tasks=pending_tasks,
            in_progress_tasks=in_progress_tasks,
            completed_tasks=completed_tasks,
            upcoming_deadlines=upcoming_deadlines,
        )
    finally:
        cursor.close()
        conn.close()


@tasks_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'GET':
            cursor.execute('SELECT id, name, employee_code FROM employees ORDER BY name')
            employees = cursor.fetchall()
            return render_template('tasks/add.html', employees=employees)

        # POST
        task_title = request.form.get('task_title', '').strip()
        description = request.form.get('description', '').strip()
        employee_id = request.form.get('employee_id', '').strip()
        priority = request.form.get('priority', 'Medium').strip()
        status = request.form.get('status', 'Pending').strip()
        completed = request.form.get('completed', 'False').strip()
        due_date = request.form.get('due_date', '').strip()

        errors = []
        if not task_title:
            errors.append('Task title is required.')
        if not employee_id:
            errors.append('Employee is required.')

        if errors:
            for err in errors:
                flash(err, 'error')
            cursor.execute('SELECT id, name, employee_code FROM employees ORDER BY name')
            employees = cursor.fetchall()
            return render_template('tasks/add.html', employees=employees, form=request.form)

        if status == 'Completed':
            completed = 'True'
        if completed == 'True':
            status = 'Completed'

        completed_bool = True if completed == 'True' else False
        due_date_val = due_date if due_date else None

        cursor.execute(
            '''INSERT INTO tasks (task_title, description, employee_id, priority, status, completed, due_date)
               VALUES (%s, %s, %s, %s, %s, %s, %s)''',
            (task_title, description, int(employee_id), priority, status, completed_bool, due_date_val)
        )
        conn.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('tasks.list'))
    except Exception as e:
        conn.rollback()
        flash('An error occurred while creating task.', 'error')
        cursor.execute('SELECT id, name, employee_code FROM employees ORDER BY name')
        employees = cursor.fetchall()
        return render_template('tasks/add.html', employees=employees, form=request.form)
    finally:
        cursor.close()
        conn.close()


@tasks_bp.route('/<int:id>')
@login_required
def view(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            '''SELECT t.*, e.name as employee_name, e.employee_code
               FROM tasks t
               JOIN employees e ON t.employee_id = e.id
               WHERE t.id = %s''',
            (id,)
        )
        task = cursor.fetchone()

        if not task:
            flash('Task not found.', 'error')
            if session.get('role') == 'admin':
                return redirect(url_for('tasks.list'))
            return redirect(url_for('tasks.my_tasks'))

        if session.get('role') == 'employee' and task['employee_id'] != session.get('employee_id'):
            flash('You can only view your own tasks.', 'error')
            return redirect(url_for('tasks.my_tasks'))

        return render_template('tasks/view.html', task=task)
    finally:
        cursor.close()
        conn.close()


@tasks_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'GET':
            cursor.execute('SELECT * FROM tasks WHERE id = %s', (id,))
            task = cursor.fetchone()
            if not task:
                flash('Task not found.', 'error')
                return redirect(url_for('tasks.list'))

            cursor.execute('SELECT id, name, employee_code FROM employees ORDER BY name')
            employees = cursor.fetchall()
            return render_template('tasks/edit.html', task=task, employees=employees)

        # POST
        task_title = request.form.get('task_title', '').strip()
        description = request.form.get('description', '').strip()
        employee_id = request.form.get('employee_id', '').strip()
        priority = request.form.get('priority', 'Medium').strip()
        status = request.form.get('status', 'Pending').strip()
        completed = request.form.get('completed', 'False').strip()
        due_date = request.form.get('due_date', '').strip()

        errors = []
        if not task_title:
            errors.append('Task title is required.')
        if not employee_id:
            errors.append('Employee is required.')

        if errors:
            for err in errors:
                flash(err, 'error')
            cursor.execute('SELECT * FROM tasks WHERE id = %s', (id,))
            task = cursor.fetchone()
            cursor.execute('SELECT id, name, employee_code FROM employees ORDER BY name')
            employees = cursor.fetchall()
            return render_template('tasks/edit.html', task=task, employees=employees)

        if status == 'Completed':
            completed = 'True'
        if completed == 'True':
            status = 'Completed'

        completed_bool = True if completed == 'True' else False
        due_date_val = due_date if due_date else None

        cursor.execute(
            '''UPDATE tasks SET task_title = %s, description = %s, employee_id = %s,
               priority = %s, status = %s, completed = %s, due_date = %s
               WHERE id = %s''',
            (task_title, description, int(employee_id), priority, status, completed_bool, due_date_val, id)
        )
        conn.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks.list'))
    except Exception as e:
        conn.rollback()
        flash('An error occurred while updating task.', 'error')
        return redirect(url_for('tasks.edit', id=id))
    finally:
        cursor.close()
        conn.close()


@tasks_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT id FROM tasks WHERE id = %s', (id,))
        if not cursor.fetchone():
            flash('Task not found.', 'error')
            return redirect(url_for('tasks.list'))

        cursor.execute('DELETE FROM tasks WHERE id = %s', (id,))
        conn.commit()
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash('An error occurred while deleting task.', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('tasks.list'))


@tasks_bp.route('/status/<int:id>', methods=['POST'])
@login_required
def update_status(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute('SELECT * FROM tasks WHERE id = %s', (id,))
        task = cursor.fetchone()

        if not task:
            flash('Task not found.', 'error')
            return redirect(request.referrer or url_for('tasks.my_tasks'))

        if session.get('role') == 'employee' and task['employee_id'] != session.get('employee_id'):
            flash('You can only update your own tasks.', 'error')
            return redirect(url_for('tasks.my_tasks'))

        new_status = request.form.get('status', 'Pending').strip()
        completed = True if new_status == 'Completed' else False

        cursor.execute(
            'UPDATE tasks SET status = %s, completed = %s WHERE id = %s',
            (new_status, completed, id)
        )
        conn.commit()
        flash('Task status updated!', 'success')
    except Exception as e:
        conn.rollback()
        flash('An error occurred while updating status.', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(request.referrer or url_for('tasks.my_tasks'))
