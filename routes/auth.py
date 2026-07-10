from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from routes.db import get_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            if session.get('role') == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('tasks.my_tasks'))
        return render_template('login.html')

    # POST
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        flash('Username and password are required.', 'error')
        return render_template('login.html')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            'SELECT * FROM users WHERE username = %s OR email = %s',
            (username, username)
        )
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['employee_id'] = user['employee_id']

            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('tasks.my_tasks'))
        else:
            flash('Invalid username or password.', 'error')
            return render_template('login.html')
    except Exception as e:
        flash(f'An error occurred. Please try again.', 'error')
        return render_template('login.html')
    finally:
        cursor.close()
        conn.close()


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
