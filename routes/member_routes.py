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
    PendingAction,
    ProductStatus,
    PriceUnit,
    OwnershipForm,
    LandUseType,
    TransactionMethod,
    VehicleType,
    FurnishedLevel,
    Orientation,
    rentPaymentCycle,
    rentPurpose,
    ElectricityCostType,
    WaterCostType,
)
from constants import UPLOAD_FOLDER

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
        "units": list(PriceUnit),
        "ownerships": list(OwnershipForm),
        "land_uses": list(LandUseType),
        "transaction_methods": list(TransactionMethod),
        "vehicle_accesses": list(VehicleType),
        "furnished_levels": list(FurnishedLevel),
        "orientations": list(Orientation),
        "statuses": list(ProductStatus),
        "rent_payment_cycles": list(rentPaymentCycle),
        "rent_purposes": list(rentPurpose),
        "electricity_costs": list(ElectricityCostType),
        "water_costs": list(WaterCostType),
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
        images = []

        # Hỗ trợ upload nhiều file ảnh
        uploaded_files = request.files.getlist("image_files")
        if not uploaded_files or (len(uploaded_files) == 1 and not uploaded_files[0].filename):
            if "image_file" in request.files:
                uploaded_files = [request.files["image_file"]]

        for file in uploaded_files:
            if file and file.filename and allowed_file(file.filename):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                ext = file.filename.rsplit(".", 1)[1].lower()
                filename = f"prop_{uuid.uuid4().hex[:10]}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                images.append(f"/static/uploads/{filename}")

        # Hỗ trợ nhập URL ảnh trực tuyến
        custom_url = request.form.get("image_url", "").strip()
        if custom_url and custom_url not in images:
            images.insert(0, custom_url)

        # Nếu không upload file mới, giữ images cũ từ form
        if not images:
            import json
            raw = request.form.get("existing_images", "[]")
            try:
                images = json.loads(raw)
            except Exception:
                images = []

        form_data = dict(request.form)
        success, msg, prop_id = property_service.create_property(user, form_data, images=images)

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
        new_images = []

        uploaded_files = request.files.getlist("image_files")
        if not uploaded_files or (len(uploaded_files) == 1 and not uploaded_files[0].filename):
            if "image_file" in request.files:
                uploaded_files = [request.files["image_file"]]

        for file in uploaded_files:
            if file and file.filename and allowed_file(file.filename):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                ext = file.filename.rsplit(".", 1)[1].lower()
                filename = f"prop_{uuid.uuid4().hex[:10]}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                new_images.append(f"/static/uploads/{filename}")

        custom_url = request.form.get("image_url", "").strip()
        if custom_url and custom_url not in new_images:
            new_images.insert(0, custom_url)

        if new_images:
            images = new_images
        else:
            images = None  # Giữ nguyên images cũ
            import json
            raw = request.form.get("existing_images", "")
            if raw:
                try:
                    images = json.loads(raw)
                except Exception:
                    images = None

        form_data = dict(request.form)
        success, msg = property_service.update_property(user, prop_id, form_data, images=images)

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
