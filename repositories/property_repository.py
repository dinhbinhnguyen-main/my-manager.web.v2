from typing import Optional, List, Dict, Any
from repositories.database import get_db_connection
from base_entities import PropertyEntity
from property_enums import ApprovalStatus, PendingAction, ProductStatus

class PropertyRepository:
    """
    Tầng Repository giao tiếp trực tiếp với bảng properties bằng SQL thuần.
    """

    @staticmethod
    def _row_to_entity(row) -> Optional[PropertyEntity]:
        if not row:
            return None
        data = dict(row)
        return PropertyEntity.from_dict(data)

    def create(self, prop: PropertyEntity) -> str:
        prop.mark_created()
        if not prop.pid:
            prop.pid = prop.id

        data = prop.to_dict()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO properties (
                    id, pid, user_id, approval_status, pending_action, reject_reason,
                    images, status, transaction_type, province, district, ward, street,
                    category, area, price, unit,
                    owner_name, owner_phone, map_url,
                    ownership, land_use, transaction_method,
                    orientation, structure, function, vehicle_access, furnished_level,
                    deposit, payment_cycle, rent_purpose, lease_term, electricity_cost, water_cost,
                    description, created_at, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?
                )
            """, (
                data["id"], data["pid"], data["user_id"], data["approval_status"], data["pending_action"], data["reject_reason"],
                data["images"], data["status"], data["transaction_type"], data["province"], data["district"], data["ward"], data["street"],
                data["category"], data["area"], data["price"], data["unit"],
                data["owner_name"], data["owner_phone"], data["map_url"],
                data["ownership"], data["land_use"], data["transaction_method"],
                data["orientation"], data["structure"], data["function"], data["vehicle_access"], data["furnished_level"],
                data.get("deposit", 0.0), data.get("payment_cycle", "monthly"), data.get("rent_purpose", "residential"),
                data.get("lease_term", 12), data.get("electricity_cost", "state_rate"), data.get("water_cost", "state_rate"),
                data["description"], data["created_at"], data["updated_at"]
            ))
            conn.commit()
            return prop.id

    def update(self, prop: PropertyEntity) -> None:
        prop.touch()
        data = prop.to_dict()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE properties SET
                    pid = ?, user_id = ?, approval_status = ?, pending_action = ?, reject_reason = ?,
                    images = ?, status = ?, transaction_type = ?, province = ?, district = ?, ward = ?, street = ?,
                    category = ?, area = ?, price = ?, unit = ?,
                    owner_name = ?, owner_phone = ?, map_url = ?,
                    ownership = ?, land_use = ?, transaction_method = ?,
                    orientation = ?, structure = ?, function = ?, vehicle_access = ?, furnished_level = ?,
                    deposit = ?, payment_cycle = ?, rent_purpose = ?, lease_term = ?, electricity_cost = ?, water_cost = ?,
                    description = ?, updated_at = ?
                WHERE id = ?
            """, (
                data["pid"], data["user_id"], data["approval_status"], data["pending_action"], data["reject_reason"],
                data["images"], data["status"], data["transaction_type"], data["province"], data["district"], data["ward"], data["street"],
                data["category"], data["area"], data["price"], data["unit"],
                data["owner_name"], data["owner_phone"], data["map_url"],
                data["ownership"], data["land_use"], data["transaction_method"],
                data["orientation"], data["structure"], data["function"], data["vehicle_access"], data["furnished_level"],
                data.get("deposit", 0.0), data.get("payment_cycle", "monthly"), data.get("rent_purpose", "residential"),
                data.get("lease_term", 12), data.get("electricity_cost", "state_rate"), data.get("water_cost", "state_rate"),
                data["description"], data["updated_at"],
                data["id"]
            ))
            conn.commit()

    def delete(self, prop_id: str) -> None:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM properties WHERE id = ?", (prop_id,))
            conn.commit()

    def get_by_id(self, prop_id: str) -> Optional[PropertyEntity]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM properties WHERE id = ?", (prop_id,))
            row = cursor.fetchone()
            return self._row_to_entity(row)

    def get_by_pid(self, pid: str) -> List[PropertyEntity]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM properties WHERE pid = ? ORDER BY created_at DESC", (pid,))
            rows = cursor.fetchall()
            return [self._row_to_entity(r) for r in rows if r]

    def get_active_approved_by_pid(self, pid: str) -> Optional[PropertyEntity]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM properties 
                WHERE pid = ? AND approval_status = 'approved' AND status != 'inactive'
                LIMIT 1
            """, (pid,))
            row = cursor.fetchone()
            return self._row_to_entity(row)

    def get_by_user_id(self, user_id: str) -> List[PropertyEntity]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM properties 
                WHERE user_id = ? 
                ORDER BY updated_at DESC
            """, (user_id,))
            rows = cursor.fetchall()
            return [self._row_to_entity(r) for r in rows if r]

    def count_by_user_id(self, user_id: str) -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM properties WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return row[0] if row else 0

    def get_public_approved_list(
        self,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        ward: Optional[str] = None,
        orientation: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_area: Optional[float] = None,
        max_area: Optional[float] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lấy danh sách BĐS đã duyệt kèm thông tin người đăng (phone, logo) để bảo vệ quyền khai thác khách hàng.
        """
        query = """
            SELECT 
                p.*,
                u.username AS author_name,
                u.phone_number AS author_phone,
                u.logo_url AS author_logo,
                u.group_id AS author_group
            FROM properties p
            JOIN users u ON p.user_id = u.id
            WHERE p.approval_status = 'approved' AND p.status IN ('selling', 'available_date')
        """
        params = []
        if category:
            query += " AND p.category = ?"
            params.append(category)
        if transaction_type:
            query += " AND p.transaction_type = ?"
            params.append(transaction_type)
        if ward:
            query += " AND p.ward = ?"
            params.append(ward)
        if orientation:
            query += " AND p.orientation = ?"
            params.append(orientation)
        if min_price is not None:
            query += " AND p.price >= ?"
            params.append(min_price)
        if max_price is not None:
            query += " AND p.price <= ?"
            params.append(max_price)
        if min_area is not None:
            query += " AND p.area >= ?"
            params.append(min_area)
        if max_area is not None:
            query += " AND p.area <= ?"
            params.append(max_area)
        if search:
            query += " AND (p.street LIKE ? OR p.description LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term])

        # Sắp xếp
        if sort_by == "price_asc":
            query += " ORDER BY p.price ASC, p.updated_at DESC"
        elif sort_by == "price_desc":
            query += " ORDER BY p.price DESC, p.updated_at DESC"
        elif sort_by == "area_desc":
            query += " ORDER BY p.area DESC, p.updated_at DESC"
        elif sort_by == "area_asc":
            query += " ORDER BY p.area ASC, p.updated_at DESC"
        else:
            query += " ORDER BY p.updated_at DESC"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_public_approved_by_id(self, prop_id: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT 
                p.*,
                u.username AS author_name,
                u.phone_number AS author_phone,
                u.logo_url AS author_logo,
                u.group_id AS author_group
            FROM properties p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = ? AND p.approval_status = 'approved'
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (prop_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_pending_approvals(self, group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lấy danh sách các bài đăng đang ở trạng thái pending chờ duyệt.
        Nếu truyền group_id thì chỉ lấy các bài của nhân sự thuộc group_id đó.
        """
        query = """
            SELECT 
                p.*,
                u.username AS author_name,
                u.phone_number AS author_phone,
                u.role AS author_role,
                u.group_id AS author_group
            FROM properties p
            JOIN users u ON p.user_id = u.id
            WHERE p.approval_status = 'pending'
        """
        params = []
        if group_id:
            query += " AND u.group_id = ?"
            params.append(group_id)

        query += " ORDER BY p.updated_at DESC"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
