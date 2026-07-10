from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.db import get_db
from routes.decorators import admin_required

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')


@employees_bp.route('/')
@admin_required
def list():
    search = request.args.get('search', '').strip()
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        if search:
            cursor.execute(
                '''SELECT * FROM employees
                   WHERE name LIKE %s OR employee_code LIKE %s OR email LIKE %s
                      OR department LIKE %s OR designation LIKE %s
                   ORDER BY id DESC''',
                (f'%{search}%', f'%{search}%', f'%{search}%',
                 f'%{search}%', f'%{search}%')
            )
        else:
            cursor.execute('SELECT * FROM employees ORDER BY id DESC')

        employees = cursor.fetchall()
        return render_template('employees/list.html', employees=employees, search=search)
    finally:
        cursor.close()
        conn.close()


@employees_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    if request.method == 'GET':
        return render_template('employees/add.html')

    # POST
    employee_code = request.form.get('employee_code', '').strip()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    department = request.form.get('department', '').strip()
    designation = request.form.get('designation', '').strip()

    errors = []
    if not employee_code:
        errors.append('Employee code is required.')
    if not name:
        errors.append('Name is required.')
    if not email:
        errors.append('Email is required.')
    if not department:
        errors.append('Department is required.')

    if errors:
        for err in errors:
            flash(err, 'error')
        return render_template('employees/add.html', form=request.form)

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            'SELECT id FROM employees WHERE employee_code = %s',
            (employee_code,)
        )
        if cursor.fetchone():
            flash('Employee code already exists.', 'error')
            return render_template('employees/add.html', form=request.form)

        cursor.execute(
            'SELECT id FROM employees WHERE email = %s',
            (email,)
        )
        if cursor.fetchone():
            flash('Email already exists.', 'error')
            return render_template('employees/add.html', form=request.form)

        cursor.execute(
            '''INSERT INTO employees (employee_code, name, email, department, designation)
               VALUES (%s, %s, %s, %s, %s)''',
            (employee_code, name, email, department, designation)
        )
        conn.commit()
        flash('Employee added successfully!', 'success')
        return redirect(url_for('employees.list'))
    except Exception as e:
        conn.rollback()
        flash('An error occurred while adding employee.', 'error')
        return render_template('employees/add.html', form=request.form)
    finally:
        cursor.close()
        conn.close()


@employees_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'GET':
            cursor.execute('SELECT * FROM employees WHERE id = %s', (id,))
            employee = cursor.fetchone()
            if not employee:
                flash('Employee not found.', 'error')
                return redirect(url_for('employees.list'))
            return render_template('employees/edit.html', employee=employee)

        # POST
        employee_code = request.form.get('employee_code', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        department = request.form.get('department', '').strip()
        designation = request.form.get('designation', '').strip()

        errors = []
        if not employee_code:
            errors.append('Employee code is required.')
        if not name:
            errors.append('Name is required.')
        if not email:
            errors.append('Email is required.')

        if errors:
            for err in errors:
                flash(err, 'error')
            cursor.execute('SELECT * FROM employees WHERE id = %s', (id,))
            employee = cursor.fetchone()
            return render_template('employees/edit.html', employee=employee)

        cursor.execute(
            'SELECT id FROM employees WHERE employee_code = %s AND id != %s',
            (employee_code, id)
        )
        if cursor.fetchone():
            flash('Employee code already exists.', 'error')
            cursor.execute('SELECT * FROM employees WHERE id = %s', (id,))
            return render_template('employees/edit.html', employee=cursor.fetchone())

        cursor.execute(
            'SELECT id FROM employees WHERE email = %s AND id != %s',
            (email, id)
        )
        if cursor.fetchone():
            flash('Email already exists.', 'error')
            cursor.execute('SELECT * FROM employees WHERE id = %s', (id,))
            return render_template('employees/edit.html', employee=cursor.fetchone())

        cursor.execute(
            '''UPDATE employees
               SET employee_code = %s, name = %s, email = %s,
                   department = %s, designation = %s
               WHERE id = %s''',
            (employee_code, name, email, department, designation, id)
        )
        conn.commit()
        flash('Employee updated successfully!', 'success')
        return redirect(url_for('employees.list'))
    except Exception as e:
        conn.rollback()
        flash('An error occurred while updating employee.', 'error')
        return redirect(url_for('employees.edit', id=id))
    finally:
        cursor.close()
        conn.close()


@employees_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT id FROM employees WHERE id = %s', (id,))
        if not cursor.fetchone():
            flash('Employee not found.', 'error')
            return redirect(url_for('employees.list'))

        cursor.execute('DELETE FROM employees WHERE id = %s', (id,))
        conn.commit()
        flash('Employee deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash('Cannot delete employee. They may have assigned tasks.', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('employees.list'))
