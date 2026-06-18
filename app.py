import sys
import os

# Force Python to find the backend folder
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime

# Try to import config, but if it fails, use defaults
try:
    from backend.config import Config
except ImportError:
    class Config:
        SECRET_KEY = 'dev-key'
        DEBUG = True
        ENVIRONMENT = 'development'
        CORS_ORIGINS = ['*']

# Try to import models and routes
try:
    from backend.models import db, bcrypt
    from backend.routes.auth import auth_bp
    from backend.routes.user import user_bp
    from backend.routes.renewal import renewal_bp
    from backend.routes.integration import integration_bp
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Create a dummy app that shows the error
    app = Flask(__name__)
    @app.route('/')
    def error_page():
        return f"<h1>Import Error</h1><pre>{e}</pre>"
    @app.route('/api/health')
    def health_error():
        return jsonify({"error": str(e), "status": "failed"})
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    sys.exit(0)

# Create the app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
CORS(app, origins=Config.CORS_ORIGINS)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(renewal_bp, url_prefix='/api/renewal')
app.register_blueprint(integration_bp, url_prefix='/api/integration')

# Health check route
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': getattr(Config, 'ENVIRONMENT', 'unknown')
    })

# Serve frontend files
FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    try:
        return send_from_directory(FRONTEND_FOLDER, path)
    except FileNotFoundError:
        return send_from_directory(FRONTEND_FOLDER, 'index.html')

# Create tables
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables ready!")
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True,
        threaded=True
    )