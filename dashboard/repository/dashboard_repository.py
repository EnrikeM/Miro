import uuid
from typing import List, Tuple, Optional

from kink import inject
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.models.user_role import UserRole
from dashboard.repository import db_helper
from dashboard.repository.dashboard_role_repository import DashboardRoleRepository
from dashboard.repository.dto.dashboad_information import DashboardInformation
from dashboard.repository.entities import Dashboard, DashboardRole
from dashboard.repository.exceptions.not_find_role_exception import NotFoundRoleException


@inject
class DashboardRepository:

    def __init__(self, dashboard_role_repository: DashboardRoleRepository):
        self.dashboard_role_repository = dashboard_role_repository

    async def create_dashboard( # noqa
        self,
        name: str,
        user_id: uuid.UUID
    ) -> Tuple[Dashboard, DashboardRole]:
        session: AsyncSession = db_helper.session_getter()
        async with session:
            dashboard = Dashboard(name=name, id = uuid.uuid4())
            dashboard_role = DashboardRole(
                dashboard_id = dashboard.id,
                user_id = user_id,
                user_role=UserRole.OWNER
            )
            session.add_all([dashboard, dashboard_role])
            await session.commit()
            await session.refresh(dashboard)
            return dashboard, dashboard_role

    async def get_user_dashboards(self, user_id: uuid.UUID) -> List[DashboardInformation]: # noqa
        session: AsyncSession = db_helper.session_getter()
        async with session:
            result = await session.execute(
                select(Dashboard, DashboardRole.user_role)
                .join(DashboardRole, Dashboard.id == DashboardRole.dashboard_id)
                .where(DashboardRole.user_id == user_id)
            )
            return [
                DashboardInformation(dashboard.id, dashboard.name, role.value)
                for dashboard, role in result.all()
            ]

    async def get_user_own_dashboards(self, user_id: uuid.UUID) -> List[DashboardInformation]: # noqa
        session: AsyncSession = db_helper.session_getter()
        async with session:
            result = await session.execute(
                select(Dashboard, DashboardRole.user_role)
                .join(DashboardRole, Dashboard.id == DashboardRole.dashboard_id)
                .where(DashboardRole.user_id == user_id and DashboardRole.user_role == UserRole.OWNER)
            )
            return [
                DashboardInformation(dashboard.id, dashboard.name, role.value)
                for dashboard, role in result.all()
            ]

    async def update_dashoard_name( # noqa
            self,
            dashboard_id: uuid.UUID,
            name: str,
            user_id: uuid.UUID,
    ) -> bool:
        session: AsyncSession = db_helper.session_getter()
        await self.dashboard_role_repository.check_is_user_owner(dashboard_id, user_id)
        async with session:
            result = await session.execute(
                select(Dashboard).where(Dashboard.id == dashboard_id)
            )
            dashboard = result.scalar_one_or_none()

            if not dashboard:
                return False

            dashboard.name = name

            await session.commit()
            return True

    async def delete_by_id(self, dashboard_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        await self.dashboard_role_repository.check_is_user_owner(dashboard_id, user_id)
        session: AsyncSession = db_helper.session_getter()
        async with session:
            result = await session.execute(
                delete(Dashboard)
                .where(Dashboard.id == dashboard_id)
                .returning(Dashboard.id)
            )
            await session.commit()
            return result.scalar_one_or_none() is not None

    async def get_dashboard(
            self,
            dashboard_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Optional[Dashboard]:
        session: AsyncSession = db_helper.session_getter()
        async with session:
            role = await self.dashboard_role_repository.get_user_role(
                session, dashboard_id, user_id
            )
            if not role:
                raise NotFoundRoleException(user_id=user_id, dashboard_id=dashboard_id)

            result = await session.execute(
                select(Dashboard)
                .where(Dashboard.id == dashboard_id)
            )
            return result.scalar_one_or_none()