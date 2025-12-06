from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4


class State:
    """Простое in-memory хранилище для моков API."""

    def __init__(self) -> None:
        self.users: Dict[str, dict] = {}
        self.tokens: Dict[str, dict] = {}

    # -----------------
    # USERS & AUTH
    # -----------------
    def create_user(self, email: str, password: str) -> dict:
        if email in self.users:
            raise ValueError("Email already exists")
        user = {"id": str(uuid4()), "email": email, "password": password}
        self.users[email] = user
        return user

    def authenticate(self, email: str, password: str) -> Optional[str]:
        user = self.users.get(email)
        if not user or user["password"] != password:
            return None
        token = str(uuid4())
        self.tokens[token] = user
        return token

    def get_user_by_token(self, token: str) -> Optional[dict]:
        return self.tokens.get(token)

    def get_user_by_email(self, email: str) -> Optional[dict]:
        return self.users.get(email)

state = State()
