import uuid
from typing import List, Optional

from kink import inject
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.models.user_role import UserRole
from dashboard.repository import db_helper
from dashboard.repository.dashboard_role_repository import DashboardRoleRepository
from dashboard.repository.entities import Sticker, DashboardRole
from dashboard.repository.exceptions.incorrect_role_exception import IncorrectRoleException
from dashboard.repository.exceptions.not_find_role_exception import NotFoundRoleException


@inject
class StickerRepository:

    def __init__(self, dashboard_role_repository: DashboardRoleRepository):
        self.dashboard_role_repository = dashboard_role_repository

    async def create_sticker(
            self,
            dashboard_id: uuid.UUID,
            user_id: uuid.UUID,
            x: int,
            y: int,
            text: str,
            width: int,
            height: int,
            color: str
    ) -> Optional[Sticker]:
        session: AsyncSession = db_helper.session_getter()
        async with session:
            role = await self.dashboard_role_repository.get_user_role(session, dashboard_id, user_id)
            if role not in [UserRole.EDITOR, UserRole.OWNER]:
                raise IncorrectRoleException(required_roles=[UserRole.EDITOR, UserRole.OWNER], actual_role=role)

            sticker = Sticker(
                dashboard_id=dashboard_id,
                x=x,
                y=y,
                text=text,
                width=width,
                height=height,
                color=color
            )
            session.add(sticker)
            await session.commit()
            await session.refresh(sticker)
            return sticker

    async def update_sticker(
            self,
            sticker_id: uuid.UUID,
            user_id: uuid.UUID,
            dashboard_id: uuid.UUID,
            **updates
    ) -> Optional[Sticker]:
        session: AsyncSession = db_helper.session_getter()
        async with session:
            role = await self.dashboard_role_repository.get_user_role(session, dashboard_id, user_id)
            if role not in [UserRole.EDITOR, UserRole.OWNER]:
                return None

            result = await session.execute(
                update(Sticker)
                .where(Sticker.id == sticker_id)
                .values(**updates)
                .returning(Sticker)
            )

            sticker = result.scalar_one_or_none()
            if sticker:
                await session.commit()
            return sticker

    async def delete_sticker(
            self,
            sticker_id: uuid.UUID,
            dashboard_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> bool:
        session: AsyncSession = db_helper.session_getter()
        async with session:
            role = await self.dashboard_role_repository.get_user_role(session, dashboard_id, user_id)
            if role not in [UserRole.EDITOR, UserRole.OWNER]:
                return False

            result = await session.execute(
                delete(Sticker)
                .where(Sticker.id == sticker_id,)
            )

            await session.commit()
            return result.scalar_one_or_none() is not None

    async def get_stickers_by_dashboard(
            self,
            dashboard_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> List[Sticker]:
        session: AsyncSession = db_helper.session_getter()
        async with session:
            role = await self.dashboard_role_repository.get_user_role(session, dashboard_id, user_id)
            if not role:
                return []
            result = await session.execute(
                select(Sticker)
                .where(Sticker.dashboard_id == dashboard_id)
            )
            return list(result.scalars().all())

    async def get_sticker(
            self,
            sticker_id: uuid.UUID,
            dashboard_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Optional[Sticker]:
        session: AsyncSession = db_helper.session_getter()
        async with session:
            role = await self.dashboard_role_repository.get_user_role(
                session, dashboard_id, user_id
            )
            if not role:
                raise NotFoundRoleException(user_id=user_id, dashboard_id=dashboard_id)

            result = await session.execute(
                select(Sticker)
                .where(and_(
                    Sticker.id == sticker_id,
                    Sticker.dashboard_id == dashboard_id
                ))
            )
            return result.scalar_one_or_none()
