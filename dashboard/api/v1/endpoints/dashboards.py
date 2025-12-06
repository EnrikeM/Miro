import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from core.dependencies import get_dashboard_repo, get_dashboard_role_repo, get_sticker_repo
from core.security import get_current_user
from models.user_role import UserRole
from repository.dashboard_repository import DashboardRepository
from repository.dashboard_role_repository import DashboardRoleRepository
from repository.entities import Dashboard
from repository.exceptions.not_find_role_exception import NotFoundRoleException
from repository.sticker_repository import StickerRepository
from schema.dashboard import BoardFull, BoardListItem, CreateBoardRequest, UpdateBoardRequest
from schema.role import BoardMember
from schema.sticker import Sticker

router = APIRouter(prefix="/boards", tags=["Boards"])


def _parse_uuid(raw_id: str) -> uuid.UUID:
    try:
        return uuid.UUID(raw_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный идентификатор")


def _serialize_sticker(sticker) -> Sticker:
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


@router.get("", response_model=list[BoardListItem])
async def list_boards(
    current_user: dict = Depends(get_current_user),
    dashboard_repo: DashboardRepository = Depends(get_dashboard_repo),
):
    user_id = _parse_uuid(current_user["id"])
    dashboards = await dashboard_repo.get_user_dashboards(user_id)
    return [BoardListItem(id=str(item.id), name=item.name, role=item.role) for item in dashboards]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BoardFull)
async def create_board(
    data: CreateBoardRequest,
    current_user: dict = Depends(get_current_user),
    dashboard_repo: DashboardRepository = Depends(get_dashboard_repo),
):
    user_id = _parse_uuid(current_user["id"])
    try:
        dashboard, _ = await dashboard_repo.create_dashboard(name=data.name, user_id=user_id)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не удалось создать доску")
    return BoardFull(id=str(dashboard.id), name=dashboard.name, role=UserRole.CREATOR, stickers=[])


@router.get("/{board_id}", response_model=BoardFull)
async def get_board(
    board_id: str,
    current_user: dict = Depends(get_current_user),
    dashboard_repo: DashboardRepository = Depends(get_dashboard_repo),
    dashboard_role_repo: DashboardRoleRepository = Depends(get_dashboard_role_repo),
    sticker_repo: StickerRepository = Depends(get_sticker_repo),
):
    dashboard_uuid = _parse_uuid(board_id)
    user_id = _parse_uuid(current_user["id"])
    try:
        dashboard = await dashboard_repo.get_dashboard(dashboard_uuid, user_id)
    except NotFoundRoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к доске")

    if dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Доска не найдена")

    role = await dashboard_role_repo.get_user_role(dashboard_uuid, user_id)
    stickers = await sticker_repo.get_stickers_by_dashboard(dashboard_uuid, user_id)
    return BoardFull(
        id=str(dashboard.id),
        name=dashboard.name,
        role=role or UserRole.VIEWER,
        stickers=[_serialize_sticker(sticker) for sticker in stickers],
    )


@router.put("/{board_id}", response_model=BoardFull)
async def update_board(
    board_id: str,
    data: UpdateBoardRequest,
    current_user: dict = Depends(get_current_user),
    dashboard_repo: DashboardRepository = Depends(get_dashboard_repo),
    dashboard_role_repo: DashboardRoleRepository = Depends(get_dashboard_role_repo),
    sticker_repo: StickerRepository = Depends(get_sticker_repo),
):
    dashboard_uuid = _parse_uuid(board_id)
    user_id = _parse_uuid(current_user["id"])

    dashboard = await dashboard_repo.session.get(Dashboard, dashboard_uuid)
    if dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Доска не найдена")

    role = await dashboard_role_repo.get_user_role(dashboard_uuid, user_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к доске")
    if role == UserRole.VIEWER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав вносить изменения")

    dashboard.name = data.name
    await dashboard_repo.session.commit()

    stickers = await sticker_repo.get_stickers_by_dashboard(dashboard_uuid, user_id)
    return BoardFull(
        id=str(dashboard.id),
        name=dashboard.name,
        role=role,
        stickers=[_serialize_sticker(sticker) for sticker in stickers],
    )


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: str,
    current_user: dict = Depends(get_current_user),
    dashboard_repo: DashboardRepository = Depends(get_dashboard_repo),
):
    dashboard_uuid = _parse_uuid(board_id)
    user_id = _parse_uuid(current_user["id"])

    dashboard = await dashboard_repo.session.get(Dashboard, dashboard_uuid)
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Доска не найдена")

    try:
        deleted = await dashboard_repo.delete_by_id(dashboard_uuid, user_id)
    except NotFoundRoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только creator может удалить доску")

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Доска не найдена")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{board_id}/members", response_model=list[BoardMember])
async def list_members(
    board_id: str,
    current_user: dict = Depends(get_current_user),
    dashboard_repo: DashboardRepository = Depends(get_dashboard_repo),
    dashboard_role_repo: DashboardRoleRepository = Depends(get_dashboard_role_repo),
):
    dashboard_uuid = _parse_uuid(board_id)
    user_id = _parse_uuid(current_user["id"])

    dashboard = await dashboard_repo.session.get(Dashboard, dashboard_uuid)
    if dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Доска не найдена")

    role = await dashboard_role_repo.get_user_role(dashboard_uuid, user_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к доске")

    try:
        roles = await dashboard_role_repo.get_dashboard_users(dashboard_uuid, user_id, require_owner=False)
    except NotFoundRoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к доске")

    return [
        BoardMember(user_id=str(uid), role=await dashboard_role_repo.get_user_role(dashboard_uuid, uid))
        for uid in roles
    ]
