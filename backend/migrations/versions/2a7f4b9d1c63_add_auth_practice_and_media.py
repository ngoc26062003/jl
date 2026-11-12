"""add auth, practice history, and media

Revision ID: 2a7f4b9d1c63
Revises: 8d14c03f7a62
Create Date: 2026-11-12 18:20:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "2a7f4b9d1c63"
down_revision: Union[str, Sequence[str], None] = "8d14c03f7a62"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("google_subject", sa.String(255), nullable=True))
    op.add_column(
        "users",
        sa.Column("total_stars", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("current_streak", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column("users", sa.Column("last_practiced_on", sa.Date(), nullable=True))
    op.alter_column("users", "password_hash", existing_type=sa.String(255), nullable=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_google_subject", "users", ["google_subject"], unique=True)

    op.create_table(
        "practice_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("direction", sa.String(32), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_practice_runs_user_id", "practice_runs", ["user_id"])
    op.create_index("ix_practice_runs_created_at", "practice_runs", ["created_at"])

    op.create_table(
        "practice_answers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("practice_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "study_item_id",
            sa.Integer(),
            sa.ForeignKey("study_items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("given", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
    )
    op.create_index("ix_practice_answers_run_id", "practice_answers", ["run_id"])
    op.create_index("ix_practice_answers_study_item_id", "practice_answers", ["study_item_id"])

    op.create_table(
        "media_assets",
        sa.Column("slot", sa.String(64), primary_key=True),
        sa.Column("content_type", sa.String(64), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("media_assets")
    op.drop_index("ix_practice_answers_study_item_id", table_name="practice_answers")
    op.drop_index("ix_practice_answers_run_id", table_name="practice_answers")
    op.drop_table("practice_answers")
    op.drop_index("ix_practice_runs_created_at", table_name="practice_runs")
    op.drop_index("ix_practice_runs_user_id", table_name="practice_runs")
    op.drop_table("practice_runs")
    op.drop_index("ix_users_google_subject", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_column("users", "last_practiced_on")
    op.drop_column("users", "current_streak")
    op.drop_column("users", "total_stars")
    op.drop_column("users", "google_subject")
    op.drop_column("users", "username")
    op.alter_column("users", "password_hash", existing_type=sa.String(255), nullable=False)
