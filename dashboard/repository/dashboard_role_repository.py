import uuid
from typing import Optional, List

from kink import inject
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.models.user_role import UserRole
from dashboard.repository import db_helper
from dashboard.repository.entities import DashboardRole
from dashboard.repository.exceptions.incorrect_role_exception import IncorrectRoleException
from dashboard.repository.exceptions.not_find_role_exception import NotFoundRoleException

@inject
class DashboardRoleRepository:

    async def check_is_user_owner(self, dashboard_id: uuid.UUID, user_id: uuid.UUID):
        session: AsyncSession = db_helper.session_getter()
        async with session:
            role = await self.get_user_role(session, dashboard_id, user_id)
            if role is None:
                raise NotFoundRoleException(user_id=user_id, dashboard_id=dashboard_id)
            if role != UserRole.OWNER:
                raise IncorrectRoleException(required_roles=[UserRole.OWNER], actual_role=role)

    async def get_user_role( # noqa
        self,
        session: AsyncSession,
        dashboard_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[UserRole]:
        result = await session.execute(
            select(DashboardRole.user_role)
            .where(and_(
                DashboardRole.dashboard_id == dashboard_id,
                DashboardRole.user_id == user_id
            ))
        )
        return result.scalar_one_or_none()

    async def invite_user(
        self,
        dashboard_id: uuid.UUID,
        inviter_id: uuid.UUID,
        user_id: uuid.UUID,
        role: UserRole
    ) -> Optional[DashboardRole]:
        await self.check_is_user_owner(dashboard_id, inviter_id)
        session: AsyncSession = db_helper.session_getter()
        async with session:
            existing = await session.get(
                DashboardRole,
                {"dashboard_id": dashboard_id, "user_id": user_id}
            )
            if existing:
                return None

            dashboard_role = DashboardRole(
                dashboard_id=dashboard_id,
                user_id=user_id,
                user_role=role
            )
            
            session.add(dashboard_role)
            await session.commit()
            await session.refresh(dashboard_role)
            return dashboard_role

    async def update_user_role(
        self,
        dashboard_id: uuid.UUID,
        owner_id: uuid.UUID,
        user_id: uuid.UUID,
        new_role: UserRole
    ) -> Optional[DashboardRole]:
        await self.check_is_user_owner(dashboard_id, owner_id)

        session: AsyncSession = db_helper.session_getter()
        async with session:
            result = await session.execute(
                select(DashboardRole)
                .where(and_(
                    DashboardRole.dashboard_id == dashboard_id,
                    DashboardRole.user_id == user_id
                ))
            )
            dashboard_role = result.scalar_one_or_none()
            
            if dashboard_role:
                dashboard_role.user_role = new_role
                await session.commit()
                await session.refresh(dashboard_role)
                
            return dashboard_role

    async def remove_user_role(
        self,
        dashboard_id: uuid.UUID,
        owner_id: uuid.UUID,
        user_id_to_remove: uuid.UUID
    ) -> bool:
        await self.check_is_user_owner(dashboard_id, owner_id)
        session: AsyncSession = db_helper.session_getter()
        async with session:
            result = await session.execute(
                delete(DashboardRole)
                .where(and_(
                    DashboardRole.dashboard_id == dashboard_id,
                    DashboardRole.user_id == user_id_to_remove
                ))
            )
            await session.commit()
            return result.scalar_one_or_none() is not None

    async def get_dashboard_users(
            self,
            dashboard_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> List[uuid.UUID]:
        await self.check_is_user_owner(dashboard_id, user_id)
        session: AsyncSession = db_helper.session_getter()
        async with session:
            result = await session.execute(
                select(DashboardRole)
                .where(DashboardRole.dashboard_id == dashboard_id)
            )
            return [
                dashboard_role.user_id
                for dashboard_role in result.all()
            ]