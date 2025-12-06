import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status

from core.dependencies import get_dashboard_repo, get_sticker_repo
from core.security import get_current_user
from models.user_role import UserRole
from repository.dashboard_repository import DashboardRepository
from repository.entities import Sticker as StickerEntity
from repository.exceptions.incorrect_role_exception import IncorrectRoleException
from repository.exceptions.not_find_role_exception import NotFoundRoleException
from repository.sticker_repository import StickerRepository
from schema.sticker import CreateStickerRequest, Sticker, UpdateStickerRequest

router = APIRouter(prefix="/stickers", tags=["Stickers"])


def _parse_uuid(raw_id: str) -> uuid.UUID:
    try:
        return uuid.UUID(raw_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный идентификатор")


def _serialize_sticker(sticker: StickerEntity) -> Sticker:
    return Sticker(
        id=str(sticker.id),
        dashboard_id=str(sticker.dashboard_id),
        x=sticker.x,
        y=sticker.y,
        text=sticker.text,
        width=sticker.width,
        height=sticker.height,
        color=sticker.color,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Sticker)
async def create_sticker(
    data: CreateStickerRequest,
    current_user: dict = Depends(get_current_user),
    dashboard_repo: DashboardRepository = Depends(get_dashboard_repo),
    sticker_repo: StickerRepository = Depends(get_sticker_repo),
):
    dashboard_uuid = _parse_uuid(data.dashboard_id)
    user_id = _parse_uuid(current_user["id"])

    try:
        dashboard = await dashboard_repo.get_dashboard(dashboard_uuid, user_id)
    except NotFoundRoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к доске")

    if dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Доска не найдена")

    try:
        sticker = await sticker_repo.create_sticker(
            dashboard_id=dashboard_uuid,
            user_id=user_id,
            x=int(data.x),
            y=int(data.y),
            text=data.text,
            width=int(data.width),
            height=int(data.height),
            color=data.color,
        )
    except IncorrectRoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав редактировать доску")

    if sticker is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не удалось создать стикер")

    return _serialize_sticker(sticker)


@router.get("/{sticker_id}", response_model=Sticker)
async def get_sticker(
    sticker_id: str,
    current_user: dict = Depends(get_current_user),
    sticker_repo: StickerRepository = Depends(get_sticker_repo),
):
    sticker_uuid = _parse_uuid(sticker_id)
    user_id = _parse_uuid(current_user["id"])

    sticker = await sticker_repo.session.get(StickerEntity, sticker_uuid)
    if sticker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найден")

    try:
        sticker = await sticker_repo.get_sticker(sticker_uuid, sticker.dashboard_id, user_id)
    except NotFoundRoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к доске")

    if sticker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найден")

    return _serialize_sticker(sticker)


@router.put("/{sticker_id}", response_model=Sticker)
async def update_sticker(
    sticker_id: str,
    data: UpdateStickerRequest,
    current_user: dict = Depends(get_current_user),
    sticker_repo: StickerRepository = Depends(get_sticker_repo),
):
    sticker_uuid = _parse_uuid(sticker_id)
    user_id = _parse_uuid(current_user["id"])

    existing = await sticker_repo.session.get(StickerEntity, sticker_uuid)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найден")

    updated = await sticker_repo.update_sticker(
        sticker_id=sticker_uuid,
        user_id=user_id,
        dashboard_id=existing.dashboard_id,
        x=int(data.x),
        y=int(data.y),
        text=data.text,
        width=int(data.width),
        height=int(data.height),
        color=data.color,
    )
    if updated is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав редактировать")

    return _serialize_sticker(updated)


@router.delete("/{sticker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sticker(
    sticker_id: str,
    current_user: dict = Depends(get_current_user),
    sticker_repo: StickerRepository = Depends(get_sticker_repo),
):
    sticker_uuid = _parse_uuid(sticker_id)
    user_id = _parse_uuid(current_user["id"])

    sticker = await sticker_repo.session.get(StickerEntity, sticker_uuid)
    if sticker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найден")

    deleted = await sticker_repo.delete_sticker(sticker_uuid, sticker.dashboard_id, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
