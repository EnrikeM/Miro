from fastapi import APIRouter, Depends, HTTPException, Response, status

from core.security import get_current_user
from models.user_role import UserRole
from schema.sticker import CreateStickerRequest, Sticker, UpdateStickerRequest
from services.state import state
from .dashboards import _get_board_or_404, _require_member

router = APIRouter(prefix="/stickers", tags=["Stickers"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Sticker)
async def create_sticker(data: CreateStickerRequest, current_user: dict = Depends(get_current_user)):
    board = _get_board_or_404(data.dashboard_id)
    role = _require_member(board, current_user["id"])
    if role == UserRole.VIEWER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав редактировать доску")
    sticker = state.add_sticker(data.dashboard_id, data.model_dump())
    return Sticker(**sticker)


@router.get("/{sticker_id}", response_model=Sticker)
async def get_sticker(sticker_id: str, current_user: dict = Depends(get_current_user)):
    sticker = state.stickers.get(sticker_id)
    if sticker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найден")
    board = _get_board_or_404(sticker["dashboard_id"])
    _require_member(board, current_user["id"])
    return Sticker(**sticker)


@router.put("/{sticker_id}", response_model=Sticker)
async def update_sticker(sticker_id: str, data: UpdateStickerRequest, current_user: dict = Depends(get_current_user)):
    sticker = state.stickers.get(sticker_id)
    if sticker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найден")
    board = _get_board_or_404(sticker["dashboard_id"])
    role = _require_member(board, current_user["id"])
    if role == UserRole.VIEWER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав редактировать")
    updated = state.update_sticker(sticker_id, data.model_dump())
    return Sticker(**updated)


@router.delete("/{sticker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sticker(sticker_id: str, current_user: dict = Depends(get_current_user)):
    sticker = state.stickers.get(sticker_id)
    if sticker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найден")
    board = _get_board_or_404(sticker["dashboard_id"])
    role = _require_member(board, current_user["id"])
    if role == UserRole.VIEWER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
    state.remove_sticker(sticker_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
