import os

# --- SYSTEM SETTINGS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "repositories", "database", "real_estate.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
DEFAULT_LOGO = "/static/uploads/default_logo.png"
