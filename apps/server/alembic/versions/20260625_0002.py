"""Add is_deleted to resources and collections.

Revision ID: 20260625_0002
Revises: 20260619_0001
Create Date: 2026-06-25
"""

from alembic import op
import sqlalchemy as sa


revision = "20260625_0002"
down_revision = "20260619_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "resources",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "collections",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    # Optional: remove the server default after existing rows have been populated.
    op.alter_column("resources", "is_deleted", server_default=None)
    op.alter_column("collections", "is_deleted", server_default=None)


def downgrade() -> None:
    op.drop_column("collections", "is_deleted")
    op.drop_column("resources", "is_deleted")