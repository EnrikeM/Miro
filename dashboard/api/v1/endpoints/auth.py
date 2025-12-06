from fastapi import APIRouter, HTTPException, status

from schema.auth import AuthResponse, SigninRequest, SignupRequest
from services.state import state

router = APIRouter(tags=["Auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(data: SignupRequest):
    try:
        state.create_user(email=data.email, password=data.password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email уже зарегистрирован")
    return {"message": "Пользователь успешно создан"}


@router.post("/signin", response_model=AuthResponse)
async def signin(data: SigninRequest):
    token = state.authenticate(email=data.email, password=data.password)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверная пара email/пароль")
    return AuthResponse(token=token)
