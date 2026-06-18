import sys
import os

# Force Python to find the backend folder
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime

from backend.config import Config
from backend.models import db, bcrypt
from backend.routes.auth import auth_bp
from backend.routes.user import user_bp
from backend.routes.renewal import renewal_bp
from backend.routes.integration import integration_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
CORS(app, origins=Config.CORS_ORIGINS)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(renewal_bp, url_prefix='/api/renewal')
app.register_blueprint(integration_bp, url_prefix='/api/integration')

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': Config.ENVIRONMENT
    })

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

with app.app_context():
    db.create_all()
    print("✅ Database tables ready!")

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=Config.DEBUG,
        threaded=True
    )