import uuid
from typing import Optional, List

from kink import inject
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.models.user_role import UserRole
from dashboard.repository.entities import DashboardRole
from dashboard.repository.exceptions.incorrect_role_exception import IncorrectRoleException
from dashboard.repository.exceptions.not_find_role_exception import NotFoundRoleException

@inject
class DashboardRoleRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_is_user_owner(self, dashboard_id: uuid.UUID, user_id: uuid.UUID):
        role = await self.get_user_role(dashboard_id, user_id)
        if role is None:
            raise NotFoundRoleException(user_id=user_id, dashboard_id=dashboard_id)
        if role != UserRole.CREATOR:
            raise IncorrectRoleException(required_roles=[UserRole.CREATOR], actual_role=role)

    async def get_user_role( # noqa
        self,
        dashboard_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[UserRole]:
        result = await self.session.execute(
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
        existing = await self.session.get(
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

        self.session.add(dashboard_role)
        await self.session.commit()
        await self.session.refresh(dashboard_role)
        return dashboard_role

    async def update_user_role(
        self,
        dashboard_id: uuid.UUID,
        owner_id: uuid.UUID,
        user_id: uuid.UUID,
        new_role: UserRole
    ) -> Optional[DashboardRole]:
        await self.check_is_user_owner(dashboard_id, owner_id)

        result = await self.session.execute(
            select(DashboardRole)
            .where(and_(
                DashboardRole.dashboard_id == dashboard_id,
                DashboardRole.user_id == user_id
            ))
        )
        dashboard_role = result.scalar_one_or_none()

        if dashboard_role:
            dashboard_role.user_role = new_role
            await self.session.commit()
            await self.session.refresh(dashboard_role)

        return dashboard_role

    async def remove_user_role(
        self,
        dashboard_id: uuid.UUID,
        owner_id: uuid.UUID,
        user_id_to_remove: uuid.UUID
    ) -> bool:
        await self.check_is_user_owner(dashboard_id, owner_id)
        result = await self.session.execute(
            delete(DashboardRole)
            .where(and_(
                DashboardRole.dashboard_id == dashboard_id,
                DashboardRole.user_id == user_id_to_remove
            ))
        )
        await self.session.commit()
        return result.scalar_one_or_none() is not None

    async def get_dashboard_users(
            self,
            dashboard_id: uuid.UUID,
            user_id: uuid.UUID,
            require_owner: bool = True,
    ) -> List[uuid.UUID]:
        if require_owner:
            await self.check_is_user_owner(dashboard_id, user_id)
        else:
            role = await self.get_user_role(dashboard_id, user_id)
            if role is None:
                raise NotFoundRoleException(user_id=user_id, dashboard_id=dashboard_id)

        result = await self.session.execute(
            select(DashboardRole)
            .where(DashboardRole.dashboard_id == dashboard_id)
        )
        return [
            dashboard_role.user_id
            for dashboard_role in result.scalars().all()
        ]