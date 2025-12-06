from typing import Literal
from pydantic import BaseModel

RoleEnum = Literal["creator", "editor", "viewer"]
EditableRoleEnum = Literal["editor", "viewer"]


class BoardMember(BaseModel):
    user_id: str
    role: RoleEnum


class UpdateRoleRequest(BaseModel):
    role: EditableRoleEnum
