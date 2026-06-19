from backend.routes.auth import auth_bp
from backend.routes.user import user_bp
from backend.routes.renewal import renewal_bp
from backend.routes.integration import integration_bp

__all__ = ['auth_bp', 'user_bp', 'renewal_bp', 'integration_bp']
