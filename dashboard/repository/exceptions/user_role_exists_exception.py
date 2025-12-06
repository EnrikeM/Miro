import uuid


class UserRoleExistsException(Exception):

    def __init__(
        self,
        user_id: uuid.UUID,
        dashboard_id: uuid.UUID,
        role: str = None
    ):
        self.user_id = user_id
        self.dashboard_id = dashboard_id
        self.role = role
        
        message = f"Роль пользователя {user_id} для доски {dashboard_id} уже существует"
        if role:
            message += f" с ролью {role}"
            
        self.message = message
        super().__init__(self.message)
