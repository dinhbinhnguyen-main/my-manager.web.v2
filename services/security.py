from functools import wraps
from flask import session, redirect, url_for, flash, request, abort
from typing import Optional, List
from base_entities import UserEntity
from property_enums import UserRole
from repositories.user_repository import UserRepository

user_repo = UserRepository()

def get_current_user() -> Optional[UserEntity]:
    """
    Lấy thông tin thực thể UserEntity của phiên đăng nhập hiện tại từ SQLite.
    """
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        session.clear()
        return None
    return user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash("Vui lòng đăng nhập để tiếp tục.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*allowed_roles):
    """
    Decorator kiểm soát quyền truy cập dựa trên UserRole (RBAC).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                flash("Vui lòng đăng nhập để tiếp tục.", "warning")
                return redirect(url_for("auth.login", next=request.url))
            
            user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
            allowed_role_values = [
                r.value if hasattr(r, 'value') else str(r) for r in allowed_roles
            ]
            
            if user_role not in allowed_role_values:
                flash("Bạn không có quyền thực hiện thao tác này.", "danger")
                return redirect(url_for("public.index"))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
