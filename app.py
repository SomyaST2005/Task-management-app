from flask import Flask
from config import Config


def create_app():
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.employees import employees_bp
    from routes.tasks import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(tasks_bp)

    @app.route('/')
    def index():
        from flask import redirect, url_for, session
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('tasks.my_tasks'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
