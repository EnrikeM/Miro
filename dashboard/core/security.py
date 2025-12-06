from fastapi import Header, HTTPException, status

from services.state import state


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    """Извлекает пользователя из токена Bearer."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется авторизация")

    token = authorization.split(" ", 1)[1]
    user = state.get_user_by_token(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен")
    return user
