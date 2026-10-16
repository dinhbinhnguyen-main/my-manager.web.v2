from typing import List, Optional, Tuple
from repositories.user_repository import UserRepository
from base_entities import UserEntity
from property_enums import UserRole

class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    def get_all_users(self, role: Optional[str] = None, is_active: Optional[bool] = None) -> List[UserEntity]:
        return self.user_repo.get_all(role=role, is_active=is_active)

    def toggle_user_active(self, user_id: str) -> Tuple[bool, str]:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False, "Không tìm thấy người dùng."
        new_status = not user.is_active
        self.user_repo.set_active_status(user_id, new_status)
        status_text = "kích hoạt" if new_status else "vô hiệu hóa"
        return True, f"Đã {status_text} tài khoản {user.username} thành công."

    def change_role_and_group(self, user_id: str, new_role: str, new_group: str) -> Tuple[bool, str]:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False, "Không tìm thấy người dùng."
        try:
            role_enum = UserRole(new_role.lower())
        except ValueError:
            return False, "Vai trò không hợp lệ."

        self.user_repo.update_role_and_group(user_id, role_enum.value, new_group.strip().upper())
        return True, f"Đã cập nhật vai trò và nhóm cho {user.username}."
