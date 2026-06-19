"""
ZINARA ZOSS — backend/app.py
Fixed: use absolute package imports so Gunicorn (run from project root) can find all modules.
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime
import os

# ── Absolute imports (required when Gunicorn runs as `gunicorn backend.app:app`) ──
from backend.config import Config
from backend.models import db, bcrypt

from backend.routes.auth import auth_bp
from backend.routes.user import user_bp
from backend.routes.renewal import renewal_bp
from backend.routes.integration import integration_bp

# ── App factory ───────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
CORS(app, origins=Config.CORS_ORIGINS)

# ── Register blueprints ───────────────────────────────────────
app.register_blueprint(auth_bp,        url_prefix='/api/auth')
app.register_blueprint(user_bp,        url_prefix='/api/user')
app.register_blueprint(renewal_bp,     url_prefix='/api/renewal')
app.register_blueprint(integration_bp, url_prefix='/api/integration')

# ── Health check ──────────────────────────────────────────────
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': Config.ENVIRONMENT,
    })

# ── Serve frontend static files ───────────────────────────────
FRONTEND_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'frontend'
)

# Debug: print the path so we can see it in Render logs
print(f"✅ Frontend folder: {FRONTEND_FOLDER}")
print(f"✅ Exists: {os.path.exists(FRONTEND_FOLDER)}")
print(f"✅ Files: {os.listdir(FRONTEND_FOLDER) if os.path.exists(FRONTEND_FOLDER) else 'NOT FOUND'}")

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    file_path = os.path.join(FRONTEND_FOLDER, path)
    if os.path.isfile(file_path):
        return send_from_directory(FRONTEND_FOLDER, path)
    # SPA fallback — let the frontend router handle unknown paths
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

# ── Database init ─────────────────────────────────────────────
with app.app_context():
    db.create_all()
    print("✅ Database tables ready!")

# ── Local dev server ──────────────────────────────────────────
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=Config.DEBUG,
        threaded=True,
    )
