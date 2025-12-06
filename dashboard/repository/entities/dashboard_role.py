import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum

from . import BaseModel
from ...models.user_role import UserRole


class DashboardRole(BaseModel):

    dashboard_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("dashboards.id", ondelete="CASCADE"),
        primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True
    )
    user_role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role_enum"), nullable=False)