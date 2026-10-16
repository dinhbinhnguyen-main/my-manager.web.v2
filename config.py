import os
from constants import BASE_DIR, DB_PATH, UPLOAD_FOLDER

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "bds-dalat-secret-key-2026-secure-session")
    DB_PATH = DB_PATH
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
