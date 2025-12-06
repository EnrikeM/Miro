from enum import Enum


class UserRole(str, Enum):
    """Роли пользователя в дашборде"""
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"