from typing import Optional, List, Dict, Any
from repositories.database import get_db_connection
from base_entities import UserEntity
from property_enums import UserRole

class UserRepository:
    """
    Tầng Repository giao tiếp trực tiếp với bảng users bằng SQL thuần.
    """

    @staticmethod
    def _row_to_entity(row) -> Optional[UserEntity]:
        if not row:
            return None
        data = dict(row)
        return UserEntity.from_dict(data)

    def get_by_id(self, user_id: str) -> Optional[UserEntity]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return self._row_to_entity(row)

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,))
            row = cursor.fetchone()
            return self._row_to_entity(row)

    def create(self, user: UserEntity) -> str:
        user.mark_created()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (id, username, password_hash, role, phone_number, logo_url, is_active, group_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user.id,
                user.username,
                user.password_hash,
                user.role.value if hasattr(user.role, 'value') else str(user.role),
                user.phone_number,
                user.logo_url,
                1 if user.is_active else 0,
                user.group_id,
                user.created_at,
                user.updated_at
            ))
            conn.commit()
            return user.id

    def update(self, user: UserEntity) -> None:
        user.touch()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET username = ?, password_hash = ?, role = ?, phone_number = ?, logo_url = ?, is_active = ?, group_id = ?, updated_at = ?
                WHERE id = ?
            """, (
                user.username,
                user.password_hash,
                user.role.value if hasattr(user.role, 'value') else str(user.role),
                user.phone_number,
                user.logo_url,
                1 if user.is_active else 0,
                user.group_id,
                user.updated_at,
                user.id
            ))
            conn.commit()

    def set_active_status(self, user_id: str, is_active: bool) -> None:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET is_active = ?, updated_at = datetime('now', 'localtime')
                WHERE id = ?
            """, (1 if is_active else 0, user_id))
            conn.commit()

    def update_role_and_group(self, user_id: str, role: str, group_id: str) -> None:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET role = ?, group_id = ?, updated_at = datetime('now', 'localtime')
                WHERE id = ?
            """, (role, group_id, user_id))
            conn.commit()

    def get_all(self, role: Optional[str] = None, is_active: Optional[bool] = None, group_id: Optional[str] = None) -> List[UserEntity]:
        query = "SELECT * FROM users WHERE 1=1"
        params = []
        if role:
            query += " AND role = ?"
            params.append(role)
        if is_active is not None:
            query += " AND is_active = ?"
            params.append(1 if is_active else 0)
        if group_id:
            query += " AND group_id = ?"
            params.append(group_id)
        query += " ORDER BY created_at DESC"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [self._row_to_entity(r) for r in rows if r]

    def get_all_group_ids(self) -> List[str]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT group_id FROM users WHERE group_id IS NOT NULL AND group_id != '' ORDER BY group_id ASC")
            rows = cursor.fetchall()
            return [r[0] for r in rows]
