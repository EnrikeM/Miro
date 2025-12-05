from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from . import BaseModel
from .mixins.uuid_id_pk import UUIDIdPkMixin


class Dashboard(BaseModel, UUIDIdPkMixin):
    name: Mapped[str] = mapped_column(nullable=False)
