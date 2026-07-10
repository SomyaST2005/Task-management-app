# VIVA Questions & Answers - Task Management System

---

### Q1. Why did you choose Flask for this project?
Flask is a lightweight, beginner-friendly Python web framework. It doesn't enforce a specific project structure, which makes it easy for college students to understand the complete request-response flow. It has built-in support for Jinja2 templating, session management, and integrates well with MySQL using mysql-connector-python.

### Q2. Why MySQL instead of SQLite or PostgreSQL?
MySQL is one of the most widely used relational databases in the industry. It supports foreign key constraints, indexes, and proper data types like ENUM. For a multi-user task management system, MySQL provides better concurrency and is more realistic for real-world applications compared to SQLite.

### Q3. What is middleware in this context?
In web applications, middleware sits between the request and the route handler. In this project, the Flask decorators (`@login_required`, `@admin_required`) act as middleware — they intercept requests before the route function executes and check authentication/authorization.

### Q4. What is CRUD?
CRUD stands for Create, Read, Update, Delete — the four basic operations of persistent storage. This project implements full CRUD for both Employees and Tasks using Flask routes and MySQL queries.

### Q5. What is a primary key?
A primary key is a column that uniquely identifies each row in a database table. In our schema, `id INT AUTO_INCREMENT PRIMARY KEY` ensures every employee, user, and task record has a unique identifier.

### Q6. What is a foreign key and how is it used here?
A foreign key is a column that references the primary key of another table, establishing a relationship. In this project:
- `tasks.employee_id` references `employees.id` — each task is assigned to one employee
- `users.employee_id` references `employees.id` — links a user account to an employee profile

### Q7. Why do we store employee_id in the tasks table?
This creates a One-to-Many relationship: one employee can have many tasks assigned to them. The foreign key constraint also ensures data integrity — you cannot assign a task to an employee that doesn't exist.

### Q8. How does authentication work in this project?
1. User submits username/email and password on the login form
2. The backend queries the `users` table for a matching record
3. Werkzeug's `check_password_hash()` compares the entered password with the stored hash
4. If valid, Flask session stores `user_id`, `username`, `role`, and `employee_id`
5. Protected routes check the session via decorators before allowing access

### Q9. Why hash passwords? Why not store plain text?
Storing plain-text passwords is a major security risk. If the database is compromised, all passwords are exposed. Hashing converts passwords into irreversible strings using cryptographic algorithms. Werkzeug uses salted hashes (PBKDF2), making them resistant to rainbow table attacks.

### Q10. What are Flask sessions?
Flask sessions are a way to store user-specific data across multiple requests. The session is stored as a signed cookie on the client side (encrypted with SECRET_KEY). In this project, we store user authentication state in the session — `user_id`, `role`, etc.

### Q11. How does role-based access control work?
After login, the user's role (`admin` or `employee`) is stored in the session. Custom decorators check this role:
- `@admin_required` — redirects non-admin users away
- `@login_required` — redirects unauthenticated users to login
- Templates also conditionally render navigation links based on role

### Q12. How do parameterized queries prevent SQL injection?
Instead of concatenating user input directly into SQL strings (which is dangerous), we use `%s` placeholders with parameter tuples. Example:
```python
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```
The database driver treats the parameter as data, not executable SQL. Even if a user types `'; DROP TABLE users; --`, it's treated as a literal string value, not code.

### Q13. What is the difference between frontend and backend?
- **Frontend**: Runs in the browser (HTML, CSS, JavaScript). Handles UI rendering, form validation, animations, and user interaction.
- **Backend**: Runs on the server (Python/Flask). Handles business logic, database operations, authentication, and data processing.

### Q14. How does JavaScript improve the UI in this project?
JavaScript adds interactivity beyond what HTML/CSS alone can do:
- Delete confirmation modals prevent accidental deletions
- Form validation provides instant feedback before submission
- Flash messages auto-dismiss after a few seconds
- Status/Completed dropdown sync on the task form
- Login button shows a loading state during submission

### Q15. Explain the complete request flow when a user creates a task.
1. Admin fills the task form (Browser → HTML form)
2. JavaScript validates required fields client-side
3. Form submits via POST to `/tasks/add` (Browser → Flask server)
4. `@admin_required` decorator checks the session
5. Route handler extracts form data, validates it server-side
6. Route syncs status/completed fields
7. Parameterized INSERT query runs on MySQL
8. Connection commits → success flash message set
9. Flask redirects to `/tasks` (task list page)
10. Task list loads all tasks with a JOIN query to get employee names

### Q16. Explain the database relationships in this project.
- **employees (1) — (N) tasks**: One-to-Many. `tasks.employee_id` → `employees.id`
- **employees (1) — (0..1) users**: One-to-Zero-or-One. `users.employee_id` → `employees.id`

The admin user has no linked employee record (employee_id is NULL). Employee users are linked to their employee profile.

### Q17. What is the difference between GET and POST?
- **GET**: Requests data from the server. Parameters appear in the URL. Used for viewing pages, searching, filtering. Idempotent and bookmarkable.
- **POST**: Submits data to the server. Parameters are in the request body. Used for login, creating/updating/deleting records. Not idempotent.

### Q18. Why should delete operations use POST instead of GET?
GET requests can be cached, bookmarked, and triggered by search engine crawlers. A delete via GET could accidentally delete data if a link is clicked or crawled. POST (and ideally DELETE method) prevents this — browsers warn before resubmitting POST forms and they aren't cached/bookmarked.

### Q19. What is Jinja2?
Jinja2 is Flask's built-in templating engine. It lets us write dynamic HTML with Python-like syntax. Features used in this project:
- `{{ variable }}` for output escaping (prevents XSS)
- `{% if %}` / `{% for %}` for control flow
- `{% extends %}` and `{% block %}` for template inheritance
- `url_for()` for dynamic route URL generation

### Q20. What is a template? Why use template inheritance?
A template is an HTML file with dynamic placeholders. Template inheritance (via `base.html`) avoids code duplication — the base template defines the common layout (sidebar, top bar, flash messages) and child templates only define page-specific content using `{% block %}` sections.

### Q21. How does task filtering work?
The tasks list page supports filtering by status, priority, and employee. The form uses GET method, so filters appear in the URL. The backend dynamically builds a SQL query by appending WHERE clauses based on which filters are provided, all using parameterized queries.

### Q22. How is task ownership enforced?
When an employee views or updates a task, the backend checks:
```python
if task['employee_id'] != session.get('employee_id'):
    flash('You can only view your own tasks.', 'error')
```
This prevents Employee A from accessing Employee B's tasks by manipulating URL IDs.

### Q23. What happens when a task is marked as completed?
Two things happen simultaneously:
1. `status` is set to `'Completed'`
2. `completed` is set to `TRUE`
These fields are kept synchronized both on the form (JavaScript syncs the dropdowns) and on the server (backend forces consistency before saving).

### Q24. What future improvements are possible?
- Email notifications when a task is assigned
- File attachments for tasks
- Task comments/discussions
- Dashboard analytics with charts
- Password reset via email
- REST API for mobile integration
- Employee self-registration
- Activity/audit logs

### Q25. Explain the complete architecture of this project.
The project follows a classic 3-tier architecture:
1. **Presentation Layer**: HTML5 + CSS3 + JavaScript in the browser. Renders the UI, handles form validation, and provides interactivity.
2. **Application Layer**: Python Flask server. Handles routing, authentication, session management, business logic, and coordinates data flow.
3. **Data Layer**: MySQL database. Stores employees, users, and tasks with proper relationships and constraints.

Data flows: Browser → Flask Route → MySQL Query → Result → Jinja2 Template → Browser
