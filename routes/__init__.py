from routes.auth_routes import auth_bp
from routes.public_routes import public_bp
from routes.member_routes import member_bp
from routes.manager_routes import manager_bp
from routes.admin_routes import admin_bp

__all__ = ["auth_bp", "public_bp", "member_bp", "manager_bp", "admin_bp"]
