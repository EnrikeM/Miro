from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.repository import db_helper
from dashboard.repository.dashboard_repository import DashboardRepository
from dashboard.repository.dashboard_role_repository import DashboardRoleRepository
from dashboard.repository.sticker_repository import StickerRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_helper.session_factory() as session:  # type: ignore[attr-defined]
        yield session


def get_dashboard_role_repo(
    session: AsyncSession = Depends(get_db_session),
) -> DashboardRoleRepository:
    return DashboardRoleRepository(session)


def get_dashboard_repo(
    session: AsyncSession = Depends(get_db_session),
    dashboard_role_repo: DashboardRoleRepository = Depends(get_dashboard_role_repo),
) -> DashboardRepository:
    return DashboardRepository(session=session, dashboard_role_repository=dashboard_role_repo)


def get_sticker_repo(
    session: AsyncSession = Depends(get_db_session),
    dashboard_role_repo: DashboardRoleRepository = Depends(get_dashboard_role_repo),
) -> StickerRepository:
    return StickerRepository(session=session, dashboard_role_repository=dashboard_role_repo)
