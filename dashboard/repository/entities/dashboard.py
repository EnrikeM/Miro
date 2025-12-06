from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from . import BaseModel
from .mixins.uuid_id_pk import UUIDIdPkMixin


class Dashboard(BaseModel, UUIDIdPkMixin):
    name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
