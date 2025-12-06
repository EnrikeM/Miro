from fastapi import APIRouter, Depends, HTTPException, Response, status

from core.security import get_current_user
from models.user_role import UserRole
from schema.dashboard import BoardFull, BoardListItem, CreateBoardRequest, UpdateBoardRequest
from schema.role import BoardMember
from schema.sticker import Sticker
from services.state import state

router = APIRouter(prefix="/boards", tags=["Boards"])


def _get_board_or_404(board_id: str) -> dict:
    board = state.get_board(board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Доска не найдена")
    return board


def _require_member(board: dict, user_id: str) -> str:
    role = board["members"].get(user_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к доске")
    return role


@router.get("", response_model=list[BoardListItem])
async def list_boards(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    result = []
    for board in state.boards.values():
        role = board["members"].get(user_id)
        if role:
            result.append(BoardListItem(id=board["id"], name=board["name"], role=role))
    return result


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BoardFull)
async def create_board(data: CreateBoardRequest, current_user: dict = Depends(get_current_user)):
    board = state.add_board(name=data.name, creator_id=current_user["id"])
    return BoardFull(id=board["id"], name=board["name"], role="creator", stickers=[])


@router.get("/{board_id}", response_model=BoardFull)
async def get_board(board_id: str, current_user: dict = Depends(get_current_user)):
    board = _get_board_or_404(board_id)
    role = _require_member(board, current_user["id"])
    stickers = [Sticker(**state.stickers[sid]) for sid in board.get("stickers", [])]
    return BoardFull(id=board["id"], name=board["name"], role=role, stickers=stickers)


@router.put("/{board_id}", response_model=BoardFull)
async def update_board(board_id: str, data: UpdateBoardRequest, current_user: dict = Depends(get_current_user)):
    board = _get_board_or_404(board_id)
    role = _require_member(board, current_user["id"])
    if role == UserRole.VIEWER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав вносить изменения")
    board["name"] = data.name
    stickers = [Sticker(**state.stickers[sid]) for sid in board.get("stickers", [])]
    return BoardFull(id=board["id"], name=board["name"], role=role, stickers=stickers)


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(board_id: str, current_user: dict = Depends(get_current_user)):
    board = _get_board_or_404(board_id)
    if board["creator_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только creator может удалить доску")
    state.delete_board(board_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{board_id}/members", response_model=list[BoardMember])
async def list_members(board_id: str, current_user: dict = Depends(get_current_user)):
    board = _get_board_or_404(board_id)
    _require_member(board, current_user["id"])
    return [BoardMember(user_id=uid, role=role) for uid, role in board["members"].items()]
