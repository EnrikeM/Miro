import base64
import jwt
import re
import hashlib
import status
import uuid

from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel, SecuritySchemeType, APIKey
from fastapi.openapi.utils import get_openapi
# from jwt.exceptions import JWTError
from pydantic import BaseModel, ValidationError, EmailStr, Field
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import List, Optional
import uvicorn
from uuid import UUID, uuid4
from passlib.context import CryptContext
from pydantic import constr

# Configuration (replace with your actual config loading)
class Settings:
    SECRET_KEY: str = "your_secret_key_here"  # Load from config or env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ISSUER: str = "AuthService"
    AUDIENCE: str = "AuthServiceUsers"
    SQLALCHEMY_DATABASE_URL: str = "mssql+pyodbc://username:password@server/db?driver=ODBC+Driver+17+for+SQL+Server"

settings = Settings()

# Database setup
engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OAuth2 scheme for JWT Bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    title="Auth Service API",
    description="API для регистрации, аутентификации и авторизации пользователей с использованием JWT токенов",
    version="v1",
    contact={
        "name": "Auth Service",
        "email": "support@authservice.com",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom OpenAPI to add JWT Bearer auth
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        contact=app.contact,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": SecuritySchemeType.apiKey,
            "name": "Authorization",
            "in": "header",
            "description": 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"',
        }
    }
    openapi_schema["security"] = [{"Bearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Example token validation dependency
def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.AUDIENCE,
            issuer=settings.ISSUER,
        )
        # You can add more validation or user loading here
        return payload
    except Exception:
        raise credentials_exception

# Example route that requires authentication
@app.get("/protected-route")
def protected_route(token_data=Depends(verify_token)):
    return {"message": "You are authenticated", "token_data": token_data}

# Models
class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="Email обязателен")
    password: constr(min_length=6) = Field(..., description="Пароль должен содержать минимум 6 символов")

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email обязателен")
    password: str = Field(..., description="Пароль обязателен")

# Entity
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Auth service interface and implementation
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

class AuthResult:
    def __init__(self, success: bool, error_message: Optional[str] = None, user_id: Optional[UUID] = None):
        self.success = success
        self.error_message = error_message
        self.user_id = user_id

class LoginResult:
    def __init__(self, success: bool, token: Optional[str] = None, expires_at: Optional[datetime] = None):
        self.success = success
        self.token = token
        self.expires_at = expires_at

class IAuthService:
    async def register_async(self, email: str, password: str) -> AuthResult:
        raise NotImplementedError

    async def login_async(self, email: str, password: str) -> LoginResult:
        raise NotImplementedError

# Dependency placeholder for auth service
def get_auth_service() -> IAuthService:
    # This should return an instance of a class implementing IAuthService
    pass

# Routes
@app.post("/api/auth/register", name="Register", tags=["Authentication"], summary="Регистрация нового пользователя", description="Создает нового пользователя с указанным email и паролем. Пароль хранится в захэшированном виде.")
async def register(request: RegisterRequest, auth_service: IAuthService = Depends(get_auth_service)):
    result = await auth_service.register_async(request.email, request.password)
    if not result.success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": result.error_message})
    return {"message": "Пользователь успешно зарегистрирован", "userId": str(result.user_id)}

@app.post("/api/auth/login", name="Login", tags=["Authentication"], summary="Вход пользователя в систему", description="Аутентифицирует пользователя и возвращает JWT токен, действительный в течение 24 часов.")
async def login(request: LoginRequest, auth_service: IAuthService = Depends(get_auth_service)):
    result = await auth_service.login_async(request.email, request.password)
    if not result.success:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {"token": result.token, "expiresAt": result.expires_at.isoformat()}

class UserFields:
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

class AuthService:
    def __init__(self, context, configuration):
        self._context = context
        self._configuration = configuration

    async def register_async(self, email, password):
        # Валидация email
        if not self.is_valid_email(email):
            return AuthResult(success=False, error_message="Некорректный формат email")

        # Валидация пароля
        if not password or len(password) < 6:
            return AuthResult(success=False, error_message="Пароль должен содержать минимум 6 символов")

        # Проверка существования пользователя
        email_lower = email.lower()
        if await self._context.users_any_async(lambda u: u.email == email_lower):
            return AuthResult(success=False, error_message="Пользователь с таким email уже существует")

        # Хэширование пароля
        password_hash = self.hash_password(password)

        # Создание пользователя
        user = UserFields(
            id=uuid.uuid4(),
            email=email_lower,
            password_hash=password_hash
        )

        self._context.users_add(user)
        await self._context.save_changes_async()

        return AuthResult(success=True, user_id=user.id)

    async def login_async(self, email, password):
        email_lower = email.lower()
        user = await self._context.users_first_or_default_async(lambda u: u.email == email_lower)

        if user is None or not self.verify_password(password, user.password_hash):
            return LoginResult(success=False)

        token = self.generate_jwt_token(user)
        expires_at = datetime.utcnow() + timedelta(hours=24)

        return LoginResult(success=True, token=token, expires_at=expires_at)

    def is_valid_email(self, email):
        if not email or email.isspace():
            return False
        email_regex = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', re.IGNORECASE)
        return bool(email_regex.match(email))

    def hash_password(self, password):
        sha256 = hashlib.sha256()
        sha256.update(password.encode('utf-8'))
        hashed_bytes = sha256.digest()
        return base64.b64encode(hashed_bytes).decode('utf-8')

    def verify_password(self, password, password_hash):
        hash = self.hash_password(password)
        return hash == password_hash

    def generate_jwt_token(self, user):
        jwt_settings = self._configuration.get("JwtSettings", {})
        secret_key = jwt_settings.get("SecretKey")
        if not secret_key:
            raise Exception("JWT SecretKey не настроен")
        issuer = jwt_settings.get("Issuer", "AuthService")
        audience = jwt_settings.get("Audience", "AuthServiceUsers")

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "jti": str(uuid.uuid4()),
            "iss": issuer,
            "aud": audience,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }

        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token
