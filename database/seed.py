import mysql.connector
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config
from werkzeug.security import generate_password_hash

def seed():
    conn = mysql.connector.connect(**Config.DB_CONFIG)
    cursor = conn.cursor()

    try:
        # =============================================
        # Insert Employees
        # =============================================
        employees = [
            ('EMP001', 'Rajesh Kumar', 'rajesh@example.com', 'IT', 'Software Developer'),
            ('EMP002', 'Priya Sharma', 'priya@example.com', 'HR', 'HR Manager'),
            ('EMP003', 'Amit Patel', 'amit@example.com', 'Finance', 'Accountant'),
        ]

        for emp in employees:
            cursor.execute(
                '''INSERT IGNORE INTO employees (employee_code, name, email, department, designation)
                   VALUES (%s, %s, %s, %s, %s)''',
                emp
            )

        # Get employee IDs
        cursor.execute("SELECT id, employee_code FROM employees ORDER BY id")
        emp_ids = {code: eid for eid, code in cursor.fetchall()}

        # =============================================
        # Insert Users (passwords are hashed)
        # =============================================
        admin_password = generate_password_hash('admin123')
        emp1_password = generate_password_hash('emp123')
        emp2_password = generate_password_hash('emp123')
        emp3_password = generate_password_hash('emp123')

        cursor.execute(
            '''INSERT IGNORE INTO users (username, email, password_hash, role, employee_id)
               VALUES (%s, %s, %s, %s, %s)''',
            ('admin', 'admin@example.com', admin_password, 'admin', None)
        )

        cursor.execute(
            '''INSERT IGNORE INTO users (username, email, password_hash, role, employee_id)
               VALUES (%s, %s, %s, %s, %s)''',
            ('rajesh', 'rajesh@example.com', emp1_password, 'employee', emp_ids.get('EMP001'))
        )

        cursor.execute(
            '''INSERT IGNORE INTO users (username, email, password_hash, role, employee_id)
               VALUES (%s, %s, %s, %s, %s)''',
            ('priya', 'priya@example.com', emp2_password, 'employee', emp_ids.get('EMP002'))
        )

        cursor.execute(
            '''INSERT IGNORE INTO users (username, email, password_hash, role, employee_id)
               VALUES (%s, %s, %s, %s, %s)''',
            ('amit', 'amit@example.com', emp3_password, 'employee', emp_ids.get('EMP003'))
        )

        # =============================================
        # Insert Sample Tasks
        # =============================================
        tasks = [
            ('Build Login Module', 'Implement user authentication with Flask sessions.', emp_ids['EMP001'], 'High', 'In Progress', False, '2025-04-15'),
            ('Update Employee Records', 'Verify and update all employee data in the system.', emp_ids['EMP002'], 'Medium', 'Pending', False, '2025-04-20'),
            ('Generate Monthly Report', 'Prepare monthly financial summary report.', emp_ids['EMP003'], 'High', 'Pending', False, '2025-04-18'),
            ('Fix Dashboard Bug', 'Resolve the chart loading issue on admin dashboard.', emp_ids['EMP001'], 'High', 'Completed', True, '2025-04-10'),
            ('Conduct Training Session', 'Organize training for new software rollout.', emp_ids['EMP002'], 'Low', 'Pending', False, '2025-05-01'),
            ('Audit Expense Records', 'Review all expense claims for Q1.', emp_ids['EMP003'], 'Medium', 'In Progress', False, '2025-04-22'),
            ('Database Backup', 'Take full backup of production database.', emp_ids['EMP001'], 'Low', 'Completed', True, '2025-04-08'),
            ('Prepare Presentation', 'Create slides for client meeting next week.', emp_ids['EMP002'], 'Medium', 'Pending', False, '2025-04-17'),
        ]

        for task in tasks:
            cursor.execute(
                '''INSERT INTO tasks (task_title, description, employee_id, priority, status, completed, due_date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                task
            )

        conn.commit()
        print("Seed data inserted successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    seed()
