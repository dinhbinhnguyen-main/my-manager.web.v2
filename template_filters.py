from property_enums import UserRole, ApprovalStatus, PendingAction, ProductStatus
from utils.i18n import tr_enum

ROLE_LABELS = {
    "admin": "Quản Trị Viên",
    "manager": "Trưởng Nhóm",
    "member": "Nhân Viên Chính Thức",
    "probation": "Thử Việc",
    "unknown": "Chưa xác định"
}

APPROVAL_STATUS_LABELS = {
    "draft": ("Bản Nháp", "secondary"),
    "pending": ("Chờ Duyệt", "warning"),
    "approved": ("Đã Duyệt", "success"),
    "rejected": ("Bị Từ Chối", "danger")
}

PENDING_ACTION_LABELS = {
    "none": ("Không", "light"),
    "create": ("Đề xuất Tạo Mới", "primary"),
    "update": ("Đề xuất Cập Nhật", "info"),
    "delete": ("Đề xuất Xóa", "danger")
}

PRODUCT_STATUS_LABELS = {
    "selling": ("Đang bán", "success"),
    "sold": ("Đã bán", "dark"),
    "hidden": ("Tạm ẩn", "secondary"),
    "inactive": ("Ngừng bán", "muted"),
    "available_date": ("Sắp mở bán", "info"),
    "unknown": ("Chưa rõ", "light")
}

def register_filters(app):
    @app.template_filter("tr_enum")
    def filter_tr_enum(val, lang="vi"):
        return tr_enum(val, lang=lang)

    @app.template_filter("role_label")
    def role_label(role):
        val = role.value if hasattr(role, "value") else str(role).lower()
        return ROLE_LABELS.get(val, tr_enum(val))

    @app.template_filter("approval_badge")
    def approval_badge(status):
        val = status.value if hasattr(status, "value") else str(status).lower()
        label, css_class = APPROVAL_STATUS_LABELS.get(val, (val, "secondary"))
        return f'<span class="badge badge-{css_class}">{label}</span>'

    @app.template_filter("pending_action_badge")
    def pending_action_badge(action):
        val = action.value if hasattr(action, "value") else str(action).lower()
        label, css_class = PENDING_ACTION_LABELS.get(val, (val, "secondary"))
        if val == "none":
            return ""
        return f'<span class="badge badge-{css_class}">{label}</span>'

    @app.template_filter("product_status_badge")
    def product_status_badge(status):
        val = status.value if hasattr(status, "value") else str(status).lower()
        label, css_class = PRODUCT_STATUS_LABELS.get(val, (val, "secondary"))
        return f'<span class="badge badge-{css_class}">{label}</span>'

    @app.template_filter("orientation_label")
    def orientation_label(ori):
        return tr_enum(ori)

    @app.template_filter("clean_title")
    def clean_title(title):
        if not title:
            return ""
        val = title.value if hasattr(title, "value") else str(title)
        return tr_enum(val)
