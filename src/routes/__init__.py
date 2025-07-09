from flask import Flask, jsonify, g
from flask_cors import CORS

from src.database import SessionLocal
from .users import users_bp
from .tasks import tasks_bp
from .auth import auth_bp
from .health import health_bp

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app, origins='*')
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

    # Register blueprints
    app.register_blueprint(users_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)

    @app.teardown_appcontext
    def close_db(error):
        """Close database session after request."""
        db = g.pop('db', None)
        if db is not None:
            db.close()

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app