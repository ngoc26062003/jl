"""add lesson content

Revision ID: 8d14c03f7a62
Revises: 4bb35b59ed32
Create Date: 2026-11-12 17:45:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "8d14c03f7a62"
down_revision: Union[str, Sequence[str], None] = "4bb35b59ed32"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "lessons",
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("lessons", "content")
