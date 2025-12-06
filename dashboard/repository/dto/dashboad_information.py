import uuid

from dataclasses import dataclass

from dashboard.models.user_role import UserRole

@dataclass
class DashboardInformation:
    id: uuid.UUID
    name: str
    role: UserRole