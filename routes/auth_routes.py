import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from services.auth_service import AuthService
from services.security import login_required, get_current_user
from constants import UPLOAD_FOLDER

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("public.index"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        
        user, msg = auth_service.authenticate(username, password)
        if not user:
            flash(msg, "danger")
            return render_template("auth/login.html")

        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role.value if hasattr(user.role, "value") else str(user.role)
        session["group_id"] = user.group_id
        session["logo_url"] = user.logo_url
        session["phone_number"] = user.phone_number

        flash(f"Chào mừng trở lại, {user.username}!", "success")
        next_url = request.args.get("next")
        return redirect(next_url or url_for("member.my_properties"))

    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("public.index"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        phone_number = request.form.get("phone_number", "")
        role_str = request.form.get("role", "member")
        group_id = request.form.get("group_id", "")

        success, msg = auth_service.register(
            username=username,
            password=password,
            phone_number=phone_number,
            role_str=role_str,
            group_id=group_id
        )

        if success:
            flash(msg, "success")
            return redirect(url_for("auth.login"))
        else:
            flash(msg, "danger")
            return render_template("auth/register.html")

    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Đã đăng xuất an toàn khỏi hệ thống.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = get_current_user()
    if request.method == "POST":
        phone_number = request.form.get("phone_number", "")
        logo_url = None

        if "logo_file" in request.files:
            file = request.files["logo_file"]
            if file and file.filename and allowed_file(file.filename):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                ext = file.filename.rsplit(".", 1)[1].lower()
                filename = f"logo_{user.id}_{uuid.uuid4().hex[:6]}.{ext}"
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                logo_url = f"/static/uploads/{filename}"

        success, msg = auth_service.update_profile(user.id, phone_number, logo_url)
        if success:
            session["phone_number"] = phone_number
            if logo_url:
                session["logo_url"] = logo_url
            flash(msg, "success")
        else:
            flash(msg, "danger")
        return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html", user=user)
