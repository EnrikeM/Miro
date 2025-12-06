"""Initial schema for dashboards and stickers"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

from dashboard.models.user_role import UserRole

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dashboards",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "dashboard_roles",
        sa.Column("dashboard_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_role", sa.Enum(UserRole, name="user_role_enum"), nullable=False),
        sa.ForeignKeyConstraint(["dashboard_id"], ["dashboards.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("dashboard_id", "user_id", name="pk_dashboard_roles"),
    )
    op.create_index("idx_dashboard_roles_dashboard_user", "dashboard_roles", ["dashboard_id", "user_id"], unique=False)
    op.create_index("idx_dashboard_roles_dashboard_id", "dashboard_roles", ["dashboard_id"], unique=False)
    op.create_index("idx_dashboard_roles_user_id", "dashboard_roles", ["user_id"], unique=False)

    op.create_table(
        "stickers",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dashboard_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("color", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["dashboard_id"], ["dashboards.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_stickers_dashboard_id", "stickers", ["dashboard_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_stickers_dashboard_id", table_name="stickers")
    op.drop_table("stickers")
    op.drop_index("idx_dashboard_roles_user_id", table_name="dashboard_roles")
    op.drop_index("idx_dashboard_roles_dashboard_id", table_name="dashboard_roles")
    op.drop_index("idx_dashboard_roles_dashboard_user", table_name="dashboard_roles")
    op.drop_table("dashboard_roles")
    op.drop_table("dashboards")
    op.execute("DROP TYPE IF EXISTS user_role_enum")
