import os
import sqlite3
from contextlib import contextmanager
from constants import DB_PATH

def init_db():
    """
    Khởi tạo cấu trúc bảng SQLite và tạo sẵn tài khoản Admin mặc định nếu chưa có.
    """
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Bảng Người dùng
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'member',
                phone_number TEXT DEFAULT '',
                logo_url TEXT DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 0,
                group_id TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)

        # Bảng Bất động sản
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id TEXT PRIMARY KEY,
                pid TEXT NOT NULL,
                user_id TEXT NOT NULL,
                approval_status TEXT NOT NULL DEFAULT 'draft',
                pending_action TEXT NOT NULL DEFAULT 'none',
                reject_reason TEXT DEFAULT '',
                images TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'hidden',
                transaction_type TEXT NOT NULL DEFAULT 'sale',
                province TEXT NOT NULL DEFAULT 'lam_dong',
                district TEXT NOT NULL DEFAULT 'da_lat',
                ward TEXT NOT NULL DEFAULT 'phuong_1_xuan_huong',
                street TEXT DEFAULT '',
                category TEXT NOT NULL DEFAULT 'townhouse',
                area REAL NOT NULL DEFAULT 0.0,
                price REAL NOT NULL DEFAULT 0.0,
                unit TEXT NOT NULL DEFAULT 'billion',
                owner_name TEXT DEFAULT '',
                owner_phone TEXT DEFAULT '',
                map_url TEXT DEFAULT '',
                ownership TEXT NOT NULL DEFAULT 'private',
                land_use TEXT NOT NULL DEFAULT 'residential_land',
                transaction_method TEXT NOT NULL DEFAULT 'notarized_contract',
                orientation TEXT NOT NULL DEFAULT 'unknown',
                structure REAL NOT NULL DEFAULT 0.0,
                function TEXT DEFAULT '',
                vehicle_access TEXT NOT NULL DEFAULT 'motorbike',
                furnished_level TEXT NOT NULL DEFAULT 'none',
                deposit REAL NOT NULL DEFAULT 0.0,
                payment_cycle TEXT NOT NULL DEFAULT 'monthly',
                rent_purpose TEXT NOT NULL DEFAULT 'residential',
                lease_term INTEGER NOT NULL DEFAULT 12,
                electricity_cost TEXT NOT NULL DEFAULT 'state_rate',
                water_cost TEXT NOT NULL DEFAULT 'state_rate',
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)

        # Tự động cập nhật các cột mới và loại bỏ cột cũ nếu DB đã tồn tại
        cursor.execute("PRAGMA table_info(properties);")
        existing_cols = {row[1] for row in cursor.fetchall()}

        if "title" in existing_cols:
            try:
                cursor.execute("ALTER TABLE properties DROP COLUMN title;")
            except Exception:
                pass

        needed_cols = {
            "orientation": "TEXT NOT NULL DEFAULT 'unknown'",
            "ownership": "TEXT NOT NULL DEFAULT 'private'",
            "land_use": "TEXT NOT NULL DEFAULT 'residential_land'",
            "transaction_method": "TEXT NOT NULL DEFAULT 'notarized_contract'",
            "vehicle_access": "TEXT NOT NULL DEFAULT 'motorbike'",
            "furnished_level": "TEXT NOT NULL DEFAULT 'none'",
            "images": "TEXT NOT NULL DEFAULT '[]'",
            "owner_name": "TEXT DEFAULT ''",
            "owner_phone": "TEXT DEFAULT ''",
            "map_url": "TEXT DEFAULT ''",
            "deposit": "REAL NOT NULL DEFAULT 0.0",
            "payment_cycle": "TEXT NOT NULL DEFAULT 'monthly'",
            "rent_purpose": "TEXT NOT NULL DEFAULT 'residential'",
            "lease_term": "INTEGER NOT NULL DEFAULT 12",
            "electricity_cost": "TEXT NOT NULL DEFAULT 'state_rate'",
            "water_cost": "TEXT NOT NULL DEFAULT 'state_rate'",
        }
        for col_name, col_def in needed_cols.items():
            if col_name not in existing_cols:
                try:
                    cursor.execute(f"ALTER TABLE properties ADD COLUMN {col_name} {col_def};")
                except Exception:
                    pass

        # Tạo chỉ mục tối ưu truy vấn
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_properties_pid ON properties(pid);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_properties_approval ON properties(approval_status, pending_action);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_properties_user_id ON properties(user_id);")

        # Kiểm tra và tạo tài khoản Admin mặc định
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            from werkzeug.security import generate_password_hash
            import uuid
            import datetime
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            admin_id = str(uuid.uuid4())
            admin_pwd = generate_password_hash("admin123")
            cursor.execute("""
                INSERT INTO users (id, username, password_hash, role, phone_number, logo_url, is_active, group_id, created_at, updated_at)
                VALUES (?, ?, ?, 'admin', '0901234567', '', 1, 'GROUP_HQ', ?, ?)
            """, (admin_id, "admin", admin_pwd, now_str, now_str))

        conn.commit()


@contextmanager
def get_db_connection():
    """
    Context manager cung cấp kết nối SQLite với row_factory và bật foreign keys.
    """
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    try:
        yield conn
    finally:
        conn.close()
