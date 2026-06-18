# This file makes 'routes' a Python package
from .auth import auth_bp
from .user import user_bp
from .renewal import renewal_bp
from .integration import integration_bp

__all__ = ['auth_bp', 'user_bp', 'renewal_bp', 'integration_bp']