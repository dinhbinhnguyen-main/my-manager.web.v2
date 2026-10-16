from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.security import login_required, roles_required, get_current_user
from services.property_service import PropertyService
from property_enums import UserRole, PendingAction

manager_bp = Blueprint("manager", __name__, url_prefix="/dashboard/manager")
property_service = PropertyService()

@manager_bp.route("/approvals")
@login_required
@roles_required(UserRole.MANAGER, UserRole.ADMIN)
def approval_list():
    user = get_current_user()
    pending_items = property_service.get_pending_list_for_reviewer(user)
    return render_template(
        "manager/approval_list.html",
        user=user,
        pending_items=pending_items
    )

@manager_bp.route("/approvals/<pending_id>/diff")
@login_required
@roles_required(UserRole.MANAGER, UserRole.ADMIN)
def review_diff(pending_id: str):
    user = get_current_user()
    diff_data = property_service.get_comparison_data(pending_id)
    if not diff_data:
        flash("Không tìm thấy thông tin bản nháp cần duyệt.", "danger")
        return redirect(url_for("manager.approval_list"))

    return render_template(
        "manager/review_diff.html",
        user=user,
        pending=diff_data["pending"],
        original=diff_data["original"],
        author=diff_data["author"]
    )

@manager_bp.route("/approvals/<pending_id>/approve", methods=["POST"])
@login_required
@roles_required(UserRole.MANAGER, UserRole.ADMIN)
def approve(pending_id: str):
    user = get_current_user()
    success, msg = property_service.approve(user, pending_id)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("manager.approval_list"))

@manager_bp.route("/approvals/<pending_id>/reject", methods=["POST"])
@login_required
@roles_required(UserRole.MANAGER, UserRole.ADMIN)
def reject(pending_id: str):
    user = get_current_user()
    reason = request.form.get("reject_reason", "").strip()
    success, msg = property_service.reject(user, pending_id, reason)
    if success:
        flash(msg, "warning")
    else:
        flash(msg, "danger")
    return redirect(url_for("manager.approval_list"))
