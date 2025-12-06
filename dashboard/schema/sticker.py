from typing import Literal
from pydantic import BaseModel


class Sticker(BaseModel):
    id: str
    dashboard_id: str
    x: float
    y: float
    text: str
    width: float
    height: float
    color: str


class CreateStickerRequest(BaseModel):
    dashboard_id: str
    x: float
    y: float
    text: str
    width: float
    height: float
    color: str


class UpdateStickerRequest(BaseModel):
    x: float
    y: float
    text: str
    width: float
    height: float
    color: str
