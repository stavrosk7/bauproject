from flask import Flask, render_template
import os
from dotenv import load_dotenv
from extensions import db, login_manager

# Load environment variables from .env file if it exists
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///project_management.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', os.path.join('static', 'uploads'))
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from api.auth_routes import auth_api
    from api.project_routes import project_api
    from api.admin_routes import admin_api

    app.register_blueprint(auth_api)
    app.register_blueprint(project_api)
    app.register_blueprint(admin_api)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

app = create_app()

# Initialize admin user and subscriptions
from model.user import User, Subscription
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=generate_password_hash('2017'),
                is_manager=False,
                is_admin=True
            )
            db.session.add(admin)
        
        # Create subscription plans if they don't exist
        if not Subscription.query.filter_by(name='Free').first():
            free_plan = Subscription(
                name='Free',
                price=0.0,
                max_projects=5,
                max_engineers=2
            )
            db.session.add(free_plan)
        
        if not Subscription.query.filter_by(name='Pro').first():
            pro_plan = Subscription(
                name='Pro',
                price=50.0,
                max_projects=-1,  # unlimited
                max_engineers=-1  # unlimited
            )
            db.session.add(pro_plan)
        
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    init_db()
    # Check if running in Docker
    if os.environ.get('DOCKER_ENV'):
        app.run(host='0.0.0.0', port=5000)
    else:
        app.run(debug=True) 