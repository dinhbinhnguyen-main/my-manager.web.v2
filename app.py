import os
from flask import Flask
from config import Config
from repositories.database import init_db
from services.security import get_current_user
from template_filters import register_filters

from routes.auth_routes import auth_bp
from routes.public_routes import public_bp
from routes.member_routes import member_bp
from routes.manager_routes import manager_bp
from routes.admin_routes import admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Đảm bảo thư mục uploads tồn tại
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Khởi tạo CSDL SQLite & tài khoản Admin ban đầu
    init_db()

    # Đăng ký Blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(admin_bp)

    # Đăng ký template filters
    register_filters(app)

    # Context processor toàn cục cho Jinja2
    @app.context_processor
    def inject_user():
        return {
            "current_user": get_current_user()
        }

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
