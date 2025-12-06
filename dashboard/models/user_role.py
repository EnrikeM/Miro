from enum import Enum


class UserRole(str, Enum):
    """Роли пользователя в дашборде."""

    CREATOR = "creator"
    OWNER = "creator"
    EDITOR = "editor"
    VIEWER = "viewer"
