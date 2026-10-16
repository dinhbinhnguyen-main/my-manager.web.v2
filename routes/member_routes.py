import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.security import login_required, get_current_user
from services.property_service import PropertyService
from property_enums import (
    PropertyType,
    TransactionType,
    WardType,
    ProvinceType,
    DistrictType,
    UserRole,
    ApprovalStatus,
    PendingAction
)
from constants import (
    RealEstateProduct__Unit,
    RealEstateProduct__Legal,
    RealEstateProduct__BuildingLine,
    RealEstateProduct__Furniture,
    UPLOAD_FOLDER
)

member_bp = Blueprint("member", __name__, url_prefix="/dashboard")
property_service = PropertyService()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def _get_form_enums():
    return {
        "categories": list(PropertyType),
        "transaction_types": list(TransactionType),
        "wards": list(WardType),
        "provinces": list(ProvinceType),
        "districts": list(DistrictType),
        "units": list(RealEstateProduct__Unit),
        "legals": list(RealEstateProduct__Legal),
        "building_lines": list(RealEstateProduct__BuildingLine),
        "furnitures": list(RealEstateProduct__Furniture),
    }

@member_bp.route("/properties")
@login_required
def my_properties():
    user = get_current_user()
    properties = property_service.get_user_properties(user.id)
    return render_template(
        "member/my_properties.html",
        user=user,
        properties=properties
    )

@member_bp.route("/properties/new", methods=["GET", "POST"])
@login_required
def create_property():
    user = get_current_user()

    if request.method == "POST":
        image_url = request.form.get("image_url", "").strip()

        if "image_file" in request.files:
            file = request.files["image_file"]
            if file and file.filename and allowed_file(file.filename):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                ext = file.filename.rsplit(".", 1)[1].lower()
                filename = f"prop_{uuid.uuid4().hex[:10]}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                image_url = f"/static/uploads/{filename}"

        form_data = dict(request.form)
        success, msg, prop_id = property_service.create_property(user, form_data, image_url=image_url)

        if success:
            flash(msg, "success")
            return redirect(url_for("member.my_properties"))
        else:
            flash(msg, "danger")

    enums = _get_form_enums()
    return render_template("member/property_form.html", user=user, property=None, **enums)

@member_bp.route("/properties/<prop_id>/edit", methods=["GET", "POST"])
@login_required
def edit_property(prop_id: str):
    user = get_current_user()
    prop = property_service.property_repo.get_by_id(prop_id)

    if not prop:
        flash("Không tìm thấy sản phẩm.", "danger")
        return redirect(url_for("member.my_properties"))

    if prop.user_id != user.id and user.role != UserRole.ADMIN:
        flash("Bạn không có quyền chỉnh sửa sản phẩm này.", "danger")
        return redirect(url_for("member.my_properties"))

    if request.method == "POST":
        image_url = None
        if "image_file" in request.files:
            file = request.files["image_file"]
            if file and file.filename and allowed_file(file.filename):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                ext = file.filename.rsplit(".", 1)[1].lower()
                filename = f"prop_{uuid.uuid4().hex[:10]}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                image_url = f"/static/uploads/{filename}"

        form_data = dict(request.form)
        success, msg = property_service.update_property(user, prop_id, form_data, image_url=image_url)

        if success:
            flash(msg, "success")
            return redirect(url_for("member.my_properties"))
        else:
            flash(msg, "danger")

    enums = _get_form_enums()
    return render_template("member/property_form.html", user=user, property=prop, **enums)

@member_bp.route("/properties/<prop_id>/delete", methods=["POST"])
@login_required
def delete_property(prop_id: str):
    user = get_current_user()
    success, msg = property_service.delete_property(user, prop_id)
    if success:
        flash(msg, "info")
    else:
        flash(msg, "danger")
    return redirect(url_for("member.my_properties"))
