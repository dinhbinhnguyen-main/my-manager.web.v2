from typing import Tuple, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from repositories.user_repository import UserRepository
from base_entities import UserEntity
from property_enums import UserRole

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def register(
        self,
        username: str,
        password: str,
        phone_number: str = "",
        role_str: str = "member",
        group_id: str = ""
    ) -> Tuple[bool, str]:
        """
        Đăng ký tài khoản nhân sự mới.
        Mặc định is_active = False theo đúng quy trình để Admin phê duyệt kích hoạt.
        """
        username = username.strip()
        if not username:
            return False, "Tên đăng nhập không được để trống."
        if len(password) < 6:
            return False, "Mật khẩu phải có tối thiểu 6 ký tự."

        existing = self.user_repo.get_by_username(username)
        if existing:
            return False, f"Tên đăng nhập '{username}' đã tồn tại trong hệ thống."

        try:
            role = UserRole(role_str.lower())
            if role == UserRole.ADMIN:
                role = UserRole.MEMBER  # Không được tự đăng ký làm ADMIN
        except ValueError:
            role = UserRole.MEMBER

        user = UserEntity(
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            phone_number=phone_number.strip(),
            logo_url="",
            is_active=False,  # Bắt buộc Admin duyệt kích hoạt
            group_id=group_id.strip().upper()
        )
        self.user_repo.create(user)
        return True, "Đăng ký thành công! Tài khoản đang chờ Quản trị viên (Admin) kích hoạt trước khi có thể đăng nhập."

    def authenticate(self, username: str, password: str) -> Tuple[Optional[UserEntity], str]:
        """
        Xác thực đăng nhập người dùng.
        """
        username = username.strip()
        user = self.user_repo.get_by_username(username)
        if not user:
            return None, "Tên đăng nhập hoặc mật khẩu không chính xác."

        if not check_password_hash(user.password_hash, password):
            return None, "Tên đăng nhập hoặc mật khẩu không chính xác."

        if not user.is_active:
            return None, "Tài khoản của bạn hiện đang bị khóa hoặc CHƯA được Admin kích hoạt."

        return user, "Đăng nhập thành công."

    def update_profile(self, user_id: str, phone_number: str, logo_url: Optional[str] = None) -> Tuple[bool, str]:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False, "Người dùng không tồn tại."
        user.phone_number = phone_number.strip()
        if logo_url is not None:
            user.logo_url = logo_url
        self.user_repo.update(user)
        return True, "Cập nhật thông tin cá nhân thành công."
