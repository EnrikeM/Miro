from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4


class State:
    """Простое in-memory хранилище для моков API."""

    def __init__(self) -> None:
        self.users: Dict[str, dict] = {}
        self.tokens: Dict[str, dict] = {}
        self.boards: Dict[str, dict] = {}
        self.stickers: Dict[str, dict] = {}

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

    # -----------------
    # BOARDS
    # -----------------
    def add_board(self, name: str, creator_id: str) -> dict:
        board_id = str(uuid4())
        board = {
            "id": board_id,
            "name": name,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "members": {creator_id: "creator"},
            "stickers": [],
            "creator_id": creator_id,
        }
        self.boards[board_id] = board
        return board

    def get_board(self, board_id: str) -> Optional[dict]:
        return self.boards.get(board_id)

    def delete_board(self, board_id: str) -> None:
        board = self.boards.pop(board_id, None)
        if board:
            for sticker_id in board.get("stickers", []):
                self.stickers.pop(sticker_id, None)

    # -----------------
    # MEMBERS
    # -----------------
    def set_member_role(self, board_id: str, user_id: str, role: str) -> None:
        board = self.get_board(board_id)
        if board is None:
            raise KeyError("Board not found")
        board["members"][user_id] = role

    def remove_member(self, board_id: str, user_id: str) -> bool:
        board = self.get_board(board_id)
        if board is None:
            return False
        if user_id in board["members"]:
            board["members"].pop(user_id)
            return True
        return False

    # -----------------
    # STICKERS
    # -----------------
    def add_sticker(self, board_id: str, data: dict) -> dict:
        sticker_id = str(uuid4())
        sticker = {**data, "id": sticker_id}
        self.stickers[sticker_id] = sticker
        board = self.get_board(board_id)
        if board:
            board.setdefault("stickers", []).append(sticker_id)
        return sticker

    def update_sticker(self, sticker_id: str, data: dict) -> Optional[dict]:
        if sticker_id not in self.stickers:
            return None
        self.stickers[sticker_id].update(data)
        return self.stickers[sticker_id]

    def remove_sticker(self, sticker_id: str) -> bool:
        sticker = self.stickers.pop(sticker_id, None)
        if not sticker:
            return False
        board = self.boards.get(sticker["dashboard_id"])
        if board:
            board["stickers"] = [sid for sid in board.get("stickers", []) if sid != sticker_id]
        return True


state = State()
