from __future__ import annotations

from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field


RoleEnum = Literal["creator", "editor", "viewer"]


class Board(BaseModel):
    id: str
    name: str
    created_at: datetime


class BoardListItem(BaseModel):
    id: str
    name: str
    role: RoleEnum


class BoardFull(BaseModel):
    id: str
    name: str
    role: RoleEnum
    stickers: List["Sticker"] = Field(default_factory=list)


class CreateBoardRequest(BaseModel):
    name: str


class UpdateBoardRequest(BaseModel):
    name: str


from schema.sticker import Sticker  # noqa: E402  pylint: disable=wrong-import-position
