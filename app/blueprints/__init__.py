from sanic import Blueprint

from .admin import admin_bp
from .auth import auth_bp
from .data import data_bp
from .user import user_bp
from .webhook import webhook_bp

api = Blueprint.group(
    admin_bp, auth_bp, user_bp, data_bp, webhook_bp, url_prefix="/api"
)
