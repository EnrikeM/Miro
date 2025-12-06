from fastapi import APIRouter, Depends, HTTPException, Response, status

from core.security import get_current_user
from models.user_role import UserRole
from schema.role import BoardMember, InviteRequest, UpdateRoleRequest
from services.state import state
from .dashboards import _get_board_or_404, _require_member

router = APIRouter(prefix="/boards", tags=["Boards"])


@router.patch("/{board_id}/members/{user_id}", response_model=BoardMember)
async def update_member_role(
    board_id: str,
    user_id: str,
    data: UpdateRoleRequest,
    current_user: dict = Depends(get_current_user),
):
    board = _get_board_or_404(board_id)
    role = _require_member(board, current_user["id"])
    if role != UserRole.CREATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только creator может менять роли")
    if user_id not in board["members"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    board["members"][user_id] = data.role
    return BoardMember(user_id=user_id, role=data.role)


@router.post("/{board_id}/invite", status_code=status.HTTP_201_CREATED)
async def invite_user(
    board_id: str,
    data: InviteRequest,
    current_user: dict = Depends(get_current_user),
):
    board = _get_board_or_404(board_id)
    role = _require_member(board, current_user["id"])

    if role != UserRole.CREATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только creator может приглашать")

    user = state.get_user_by_email(data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь с таким email не найден")

    if user["id"] == current_user["id"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя пригласить самого себя")

    state.set_member_role(board_id, user["id"], data.role)
    return {"message": "Пользователь приглашен"}


@router.delete("/{board_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(board_id: str, user_id: str, current_user: dict = Depends(get_current_user)):
    board = _get_board_or_404(board_id)
    role = _require_member(board, current_user["id"])
    if role != UserRole.CREATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на удаление")
    if user_id == board["creator_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нельзя удалить создателя")
    removed = state.remove_member(board_id, user_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найден")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
