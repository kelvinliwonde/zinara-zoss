# This file makes 'routes' a Python package
# It imports all routes so app.py can import them from one place

from .auth import auth_bp
from .user import user_bp
from .renewal import renewal_bp
from .integration import integration_bp

__all__ = ['auth_bp', 'user_bp', 'renewal_bp', 'integration_bp']