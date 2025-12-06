import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status

from core.dependencies import get_dashboard_repo, get_dashboard_role_repo
from core.security import get_current_user
from models.user_role import UserRole
from repository.dashboard_repository import DashboardRepository
from repository.dashboard_role_repository import DashboardRoleRepository
from repository.entities import Dashboard
from repository.exceptions.incorrect_role_exception import IncorrectRoleException
from repository.exceptions.not_find_role_exception import NotFoundRoleException
from schema.role import BoardMember, InviteRequest, UpdateRoleRequest
from services.state import state
from .dashboards import _parse_uuid

router = APIRouter(prefix="/boards", tags=["Boards"])


@router.patch("/{board_id}/members/{user_id}", response_model=BoardMember)
async def update_member_role(
    board_id: str,
    user_id: str,
    data: UpdateRoleRequest,
    current_user: dict = Depends(get_current_user),
    dashboard_role_repo: DashboardRoleRepository = Depends(get_dashboard_role_repo),
    dashboard_repo: DashboardRepository = Depends(get_dashboard_repo),
):
    board_uuid = _parse_uuid(board_id)
    target_user_uuid = _parse_uuid(user_id)
    current_user_uuid = _parse_uuid(current_user["id"])

    dashboard = await dashboard_repo.session.get(Dashboard, board_uuid)
    if dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Доска не найдена")

    try:
        updated_role = await dashboard_role_repo.update_user_role(
            dashboard_id=board_uuid,
            owner_id=current_user_uuid,
            user_id=target_user_uuid,
            new_role=UserRole(data.role),
        )
    except IncorrectRoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только creator может менять роли")
    except NotFoundRoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к доске")

    if updated_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    return BoardMember(user_id=str(target_user_uuid), role=updated_role.user_role)


@router.post("/{board_id}/invite", status_code=status.HTTP_201_CREATED)
async def invite_user(
    board_id: str,
    data: InviteRequest,
    current_user: dict = Depends(get_current_user),
    dashboard_role_repo: DashboardRoleRepository = Depends(get_dashboard_role_repo),
    dashboard_repo: DashboardRepository = Depends(get_dashboard_repo),
):
    board_uuid = _parse_uuid(board_id)
    current_user_uuid = _parse_uuid(current_user["id"])

    dashboard = await dashboard_repo.session.get(Dashboard, board_uuid)
    if dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Доска не найдена")

    user = state.get_user_by_email(data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь с таким email не найден")

    if user["id"] == current_user["id"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя пригласить самого себя")

    try:
        added = await dashboard_role_repo.invite_user(
            dashboard_id=board_uuid,
            inviter_id=current_user_uuid,
            user_id=_parse_uuid(user["id"]),
            role=UserRole(data.role),
        )
    except IncorrectRoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только creator может приглашать")
    except NotFoundRoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к доске")

    if added is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь уже добавлен")

    return {"message": "Пользователь приглашен"}


@router.delete("/{board_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    board_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_user),
    dashboard_role_repo: DashboardRoleRepository = Depends(get_dashboard_role_repo),
    dashboard_repo: DashboardRepository = Depends(get_dashboard_repo),
):
    board_uuid = _parse_uuid(board_id)
    target_user_uuid = _parse_uuid(user_id)
    current_user_uuid = _parse_uuid(current_user["id"])

    dashboard = await dashboard_repo.session.get(Dashboard, board_uuid)
    if dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Доска не найдена")

    target_role = await dashboard_role_repo.get_user_role(board_uuid, target_user_uuid)
    if target_role == UserRole.CREATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нельзя удалить создателя")

    try:
        removed = await dashboard_role_repo.remove_user_role(board_uuid, current_user_uuid, target_user_uuid)
    except IncorrectRoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на удаление")
    except NotFoundRoleException:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к доске")

    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найден")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
