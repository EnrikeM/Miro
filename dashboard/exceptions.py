class DashboardException(Exception):
    """Базовое исключение для ошибок, связанных с досками."""
    status_code: int = 400
    message: str = "Произошла ошибка при работе с доской"

    def __init__(self, message: str = None, status_code: int = None):
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.message)


class AccessDeniedException(DashboardException):
    """Исключение, возникающее при отказе в доступе."""
    status_code = 403
    message = "Доступ запрещен. Недостаточно прав для выполнения операции"


class NotFoundException(DashboardException):
    """Исключение, возникающее при отсутствии запрашиваемого ресурса."""
    status_code = 404
    message = "Запрашиваемый ресурс не найден"


class ValidationException(DashboardException):
    """Исключение, возникающее при ошибках валидации данных."""
    status_code = 400
    message = "Ошибка валидации данных"


class DatabaseException(DashboardException):
    """Исключение, возникающее при ошибках работы с базой данных."""
    status_code = 500
    message = "Ошибка при работе с базой данных"
