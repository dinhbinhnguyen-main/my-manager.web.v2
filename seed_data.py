import os
import uuid
import datetime
from werkzeug.security import generate_password_hash
from repositories.database import get_db_connection, init_db

def seed():
    init_db()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Thêm Manager
        cursor.execute("SELECT id FROM users WHERE username = 'manager_lamvien'")
        mgr = cursor.fetchone()
        if not mgr:
            mgr_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO users (id, username, password_hash, role, phone_number, logo_url, is_active, group_id, created_at, updated_at)
                VALUES (?, ?, ?, 'manager', '0988111222', '', 1, 'GROUP_LAMVIEN', ?, ?)
            """, (mgr_id, "manager_lamvien", generate_password_hash("password123"), now_str, now_str))
        else:
            mgr_id = mgr[0]

        # Thêm Member
        cursor.execute("SELECT id FROM users WHERE username = 'member_an'")
        mbr = cursor.fetchone()
        if not mbr:
            mbr_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO users (id, username, password_hash, role, phone_number, logo_url, is_active, group_id, created_at, updated_at)
                VALUES (?, ?, ?, 'member', '0911333444', '/static/uploads/agent_an.jpg', 1, 'GROUP_LAMVIEN', ?, ?)
            """, (mbr_id, "member_an", generate_password_hash("password123"), now_str, now_str))
        else:
            mbr_id = mbr[0]
            cursor.execute("UPDATE users SET logo_url = '/static/uploads/agent_an.jpg' WHERE id = ?", (mbr_id,))

        # Thêm Probation (Thử việc)
        cursor.execute("SELECT id FROM users WHERE username = 'probation_binh'")
        prb = cursor.fetchone()
        if not prb:
            prb_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO users (id, username, password_hash, role, phone_number, logo_url, is_active, group_id, created_at, updated_at)
                VALUES (?, ?, ?, 'probation', '0933555666', '', 1, 'GROUP_LAMVIEN', ?, ?)
            """, (prb_id, "probation_binh", generate_password_hash("password123"), now_str, now_str))
        else:
            prb_id = prb[0]

        # Thêm tài khoản chờ kích hoạt (is_active = 0)
        cursor.execute("SELECT id FROM users WHERE username = 'ung_vien_moi'")
        if not cursor.fetchone():
            cand_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO users (id, username, password_hash, role, phone_number, logo_url, is_active, group_id, created_at, updated_at)
                VALUES (?, ?, ?, 'member', '0977888999', '', 0, 'GROUP_LAMVIEN', ?, ?)
            """, (cand_id, "ung_vien_moi", generate_password_hash("password123"), now_str, now_str))

        # Thêm sản phẩm mẫu 1: Đã Approved (Biệt thự)
        cursor.execute("SELECT id FROM properties WHERE title LIKE '%Biệt thự cổ điển Phường 10%'")
        row1 = cursor.fetchone()
        if not row1:
            prop1_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO properties (
                    id, pid, user_id, approval_status, pending_action, reject_reason,
                    title, image_url, status, transaction_type, province, district, ward, street,
                    category, area, price, unit, legal, structure, function,
                    building_line, furniture, description, created_at, updated_at
                ) VALUES (
                    ?, ?, ?, 'approved', 'none', '',
                    'Biệt thự cổ điển Phường 10 view đồi thông cực đẹp', '/static/uploads/villa_dalat.jpg', 'selling', 'sale', 'lam_dong', 'da_lat', 'phuong_10_xuan_huong', 'Đường Khe Sanh',
                    'villa', 250.0, 18.5, 'billion', 'private_construction_deed', 3.0, '5 phòng ngủ master, phòng gym, sân vườn BBQ',
                    'car_access_road', 'full_furniture', 'Biệt thự phong cách Pháp tọa lạc tại vị trí đắc địa, đường nhựa ô tô tránh nhau thoải mái, thích hợp nghỉ dưỡng hoặc kinh doanh lưu trú cao cấp.',
                    ?, ?
                )
            """, (prop1_id, prop1_id, mbr_id, now_str, now_str))
        else:
            cursor.execute("UPDATE properties SET image_url = '/static/uploads/villa_dalat.jpg' WHERE id = ?", (row1[0],))

        # Thêm sản phẩm mẫu 2: Đã Approved (Nhà phố)
        cursor.execute("SELECT id FROM properties WHERE title LIKE '%Nhà phố mặt tiền Phường 2%'")
        row2 = cursor.fetchone()
        if not row2:
            prop2_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO properties (
                    id, pid, user_id, approval_status, pending_action, reject_reason,
                    title, image_url, status, transaction_type, province, district, ward, street,
                    category, area, price, unit, legal, structure, function,
                    building_line, furniture, description, created_at, updated_at
                ) VALUES (
                    ?, ?, ?, 'approved', 'none', '',
                    'Nhà phố mặt tiền Phường 2 kinh doanh đắc địa trung tâm', '/static/uploads/townhouse_dalat.jpg', 'selling', 'sale', 'lam_dong', 'da_lat', 'phuong_2_xuan_huong', 'Đường Phan Đình Phùng',
                    'street_front_house', 110.0, 12.8, 'billion', 'private_construction_deed', 4.0, 'Tầng 1 kinh doanh, 6 phòng ngủ, thang máy',
                    'car_access_road', 'basic_furniture', 'Vị trí buôn bán sầm uất bậc nhất Đà Lạt, dòng tiền cho thuê 40 triệu/tháng ổn định.',
                    ?, ?
                )
            """, (prop2_id, prop2_id, mbr_id, now_str, now_str))
        else:
            cursor.execute("UPDATE properties SET image_url = '/static/uploads/townhouse_dalat.jpg' WHERE id = ?", (row2[0],))

        # Thêm sản phẩm mẫu 3: Chờ duyệt Tạo mới (pending, create) (Đất nền Tà Nung)
        cursor.execute("SELECT id FROM properties WHERE title LIKE '%Đất nền view thung lũng Tà Nung%'")
        row3 = cursor.fetchone()
        if not row3:
            prop3_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO properties (
                    id, pid, user_id, approval_status, pending_action, reject_reason,
                    title, image_url, status, transaction_type, province, district, ward, street,
                    category, area, price, unit, legal, structure, function,
                    building_line, furniture, description, created_at, updated_at
                ) VALUES (
                    ?, ?, ?, 'pending', 'create', '',
                    'Đất nền view thung lũng Tà Nung giá đầu tư sinh lời', '/static/uploads/land_tanung.jpg', 'hidden', 'sale', 'lam_dong', 'da_lat', 'xa_ta_nung', 'Trục đường DT725',
                    'land_plot', 500.0, 4.2, 'billion', 'private_agriculture_deed', 0.0, 'Đất vuông vắn, thích hợp làm homestay hoặc farmstay',
                    'car_access_road', 'no_furniture', 'Lô đất thế dương thoai thoải, view rừng thông bao la, pháp lý rõ ràng chờ cấp quản lý duyệt.',
                    ?, ?
                )
            """, (prop3_id, prop3_id, mbr_id, now_str, now_str))
        else:
            cursor.execute("UPDATE properties SET image_url = '/static/uploads/land_tanung.jpg' WHERE id = ?", (row3[0],))

        conn.commit()
    print("Seed data completed successfully!")

if __name__ == "__main__":
    seed()
