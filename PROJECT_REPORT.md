# Project Report - Task Management System

## Title
A Web-Based Task Management System Using Flask and MySQL

## Abstract
The Task Management System is a web-based application designed to streamline task assignment, tracking, and employee management within an organization. Built using a three-tier architecture with HTML5/CSS3/JavaScript as the frontend, Python Flask as the backend framework, and MySQL as the database, the system implements role-based authentication (Admin and Employee) with complete CRUD operations for employees and tasks. The application demonstrates key web development concepts including session management, password hashing, parameterized SQL queries, foreign key relationships, and responsive UI design.

## Introduction
Managing tasks manually through spreadsheets, emails, or verbal communication is inefficient for growing organizations. A centralized digital system ensures every task is tracked, assigned to the right person, and monitored until completion. This project addresses this need by providing a structured, role-based platform where administrators can manage employees and assign tasks, while employees can view their work and update progress.

## Problem Statement
Organizations face the following challenges in task management:
- No centralized system to track task status
- Difficulty in assigning tasks to specific employees
- No visibility into employee workload
- Inefficient status tracking leading to missed deadlines
- Lack of accountability for task completion

## Objectives
1. Develop a web-based task management platform
2. Implement role-based authentication (Admin and Employee)
3. Enable full CRUD operations for employee records
4. Enable task creation, assignment, tracking, and deletion
5. Enforce data security through password hashing and parameterized queries
6. Ensure employees can only access their assigned tasks
7. Provide a responsive and intuitive user interface

## Scope
- **In Scope**: User authentication, employee management, task CRUD, status tracking, filtering, search, responsive UI
- **Out of Scope**: Email notifications, file uploads, team-based task groups, real-time chat, mobile apps

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend  | HTML5, CSS3, Vanilla JavaScript | — |
| Backend   | Python (Flask) | 3.0.0 |
| Database  | MySQL | 8.x |
| Password Hashing | Werkzeug | 3.0.1 |
| DB Driver | mysql-connector-python | 8.3.0 |
| Env Config | python-dotenv | 1.0.0 |

## System Architecture
The system follows a three-tier client-server architecture:

```
┌──────────────┐      ┌──────────────────┐      ┌────────────┐
│  Browser     │─────▶│  Flask Server    │─────▶│   MySQL    │
│  (HTML/CSS/JS)│     │  (Python Routes)  │     │  Database  │
│              │◀─────│                  │◀─────│            │
└──────────────┘      └──────────────────┘      └────────────┘
   Presentation           Application             Data Layer
```

## Module Description

### 1. Authentication Module
Handles user login/logout using Flask sessions. Passwords are hashed using Werkzeug's PBKDF2 algorithm. Role-based redirects send admins to the admin dashboard and employees to their personal dashboard.

### 2. Employee Management Module
Admin-only module for managing employee records. Supports adding, editing, deleting, and searching employees. Validates unique employee codes and emails.

### 3. Task Management Module
Core module where admins create tasks, assign them to employees, set priority and due dates. Supports task editing, deletion, filtering, and search. Employees can view their assigned tasks and update the status.

### 4. Dashboard Module
Admin dashboard displays summary statistics (total employees, tasks by status), recent tasks, and upcoming deadlines. Employee dashboard shows only the logged-in employee's tasks.

## Database Design

### Entity Relationship Diagram
```
┌─────────────┐          ┌──────────────┐
│  employees  │ 1──────N │    tasks     │
│─────────────│          │──────────────│
│ id (PK)     │          │ id (PK)      │
│ emp_code    │          │ task_title   │
│ name        │          │ description  │
│ email       │          │ employee_id  │──▶ FK → employees.id
│ department  │          │ priority     │
│ designation │          │ status       │
└─────────────┘          │ completed    │
       │                 │ due_date     │
       │ 1               └──────────────┘
       │
       │ 0..1
       │
┌─────────────┐
│    users    │
│─────────────│
│ id (PK)     │
│ username    │
│ email       │
│ pass_hash   │
│ role        │
│ employee_id │──▶ FK → employees.id
└─────────────┘
```

### Table Descriptions

**employees**: Stores employee details — code, name, email, department, designation. Serves as the parent table for both users (login accounts) and tasks (assignments).

**users**: Stores login credentials. Contains hashed passwords and role information. Links to employees via a nullable foreign key — admins have no employee link.

**tasks**: Central table storing task details. Each task belongs to exactly one employee (foreign key enforced). Tracks status, priority, completion state, and due date.

## Data Flow
1. User submits login form → Flask validates credentials against users table
2. Session created with role info → redirected to appropriate dashboard
3. Admin creates a task → selects employee from dropdown → task inserted into tasks table with employee_id foreign key
4. Employee logs in → dashboard queries tasks WHERE employee_id = session.employee_id
5. Employee updates status → tasks table updated → dashboard reflects changes

## Functional Requirements
- FR1: User login with username/email and password
- FR2: Role-based dashboard redirection
- FR3: Admin can add, edit, delete, and search employees
- FR4: Admin can create, assign, edit, delete tasks
- FR5: Admin can filter tasks by status, priority, and employee
- FR6: Admin can search tasks by title or description
- FR7: Employee can view only their assigned tasks
- FR8: Employee can update task status (Pending → In Progress → Completed)
- FR9: Status and Completed fields remain synchronized
- FR10: Logout clears the session

## Non-Functional Requirements
- NFR1: Passwords stored as salted hashes (not plaintext)
- NFR2: All SQL queries use parameterized statements (no SQL injection)
- NFR3: Session-protected routes with role verification
- NFR4: Responsive UI (works on desktop and tablet)
- NFR5: Form validation on both client and server side
- NFR6: User-friendly error messages
- NFR7: Clean separation of concerns (routes, templates, static files)

## Security Features
1. **Password Hashing**: Werkzeug's `generate_password_hash()` / `check_password_hash()`
2. **Session Authentication**: Flask signed sessions with SECRET_KEY
3. **Role-Based Authorization**: Custom decorators (`@admin_required`, `@login_required`)
4. **SQL Injection Prevention**: Parameterized queries with `%s` placeholders
5. **Input Validation**: Server-side validation of all form inputs
6. **XSS Prevention**: Jinja2 auto-escapes all output
7. **POST for Destructive Actions**: Delete operations use POST method
8. **Task Ownership**: Employees cannot access other employees' tasks

## Testing
- **Login Testing**: Verified admin and employee login with correct/incorrect credentials
- **Session Testing**: Confirmed protected routes redirect to login when not authenticated
- **CRUD Testing**: Created, viewed, updated, and deleted employees and tasks
- **Role Testing**: Verified employees cannot access admin routes and vice versa
- **Task Ownership**: Confirmed employees see only their tasks
- **Status Sync**: Verified status/completed field synchronization
- **Form Validation**: Tested empty required fields, duplicate emails, duplicate employee codes
- **Filter Testing**: Tested all filter combinations on the task list page
- **Delete Confirmation**: Tested modal confirmation for delete operations

## Screenshots
[Place screenshots here of the following pages after running the application:]
- Login Page
- Admin Dashboard
- Employee Dashboard
- Employee List Page
- Add Employee Form
- Task List Page (with filters)
- Create Task Form
- Task Detail View

## Limitations
1. No email notification system for task assignments
2. No file attachment support on tasks
3. No pagination — all records load on a single page
4. No password reset functionality
5. Single admin account — no multi-admin support
6. No activity audit log
7. No REST API for external integrations

## Future Scope
1. Email notifications on task assignment and deadline reminders
2. File upload and attachment support for tasks
3. Task comments and discussion threads
4. Dashboard analytics with charts (task completion rate, workload distribution)
5. Multi-admin support with granular permissions
6. Password reset via email
7. RESTful API endpoints for mobile integration
8. Activity logging and audit trail
9. Department-based task groups
10. Calendar view for task deadlines

## Conclusion
The Task Management System successfully demonstrates the implementation of a full-stack web application using industry-standard technologies. The project covers key software engineering concepts: three-tier architecture, relational database design with foreign key constraints, role-based authentication and authorization, CRUD operations, session management, input validation, and responsive frontend design. The clean modular code structure makes it easy to understand, maintain, and extend with additional features in the future.
