from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.security import login_required, roles_required, get_current_user
from services.user_service import UserService
from services.property_service import PropertyService
from property_enums import UserRole

admin_bp = Blueprint("admin", __name__, url_prefix="/dashboard/admin")
user_service = UserService()
property_service = PropertyService()

@admin_bp.route("/users")
@login_required
@roles_required(UserRole.ADMIN)
def user_management():
    current_user = get_current_user()
    role_filter = request.args.get("role")
    active_filter = request.args.get("is_active")
    
    is_active_bool = None
    if active_filter == "1":
        is_active_bool = True
    elif active_filter == "0":
        is_active_bool = False

    users = user_service.get_all_users(role=role_filter, is_active=is_active_bool)
    all_roles = [UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER, UserRole.PROBATION]
    
    return render_template(
        "admin/user_management.html",
        current_user=current_user,
        users=users,
        all_roles=all_roles,
        current_role_filter=role_filter,
        current_active_filter=active_filter
    )

@admin_bp.route("/users/<user_id>/toggle-active", methods=["POST"])
@login_required
@roles_required(UserRole.ADMIN)
def toggle_user_active(user_id: str):
    success, msg = user_service.toggle_user_active(user_id)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("admin.user_management"))

@admin_bp.route("/users/<user_id>/update", methods=["POST"])
@login_required
@roles_required(UserRole.ADMIN)
def update_user(user_id: str):
    role = request.form.get("role", "member")
    group_id = request.form.get("group_id", "")
    success, msg = user_service.change_role_and_group(user_id, role, group_id)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("admin.user_management"))

@admin_bp.route("/all-approvals")
@login_required
@roles_required(UserRole.ADMIN)
def all_approvals():
    user = get_current_user()
    pending_items = property_service.get_pending_list_for_reviewer(user)
    return render_template(
        "manager/approval_list.html",
        user=user,
        pending_items=pending_items,
        is_admin_view=True
    )
