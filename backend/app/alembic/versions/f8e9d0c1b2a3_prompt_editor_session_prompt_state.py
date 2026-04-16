"""prompt editor: session prompt state, tool_calls on message; drop suggestion cols

Revision ID: f8e9d0c1b2a3
Revises: e5f6a7b8c9d0
Create Date: 2026-04-14 00:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision = "f8e9d0c1b2a3"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("prompt_editor_message", "suggestion_status")
    op.drop_column("prompt_editor_message", "prompt_suggestion")
    op.add_column(
        "prompt_editor_session",
        sa.Column("base_prompt", sa.Text(), nullable=True),
    )
    op.add_column(
        "prompt_editor_session",
        sa.Column("edited_prompt", sa.Text(), nullable=True),
    )
    op.add_column(
        "prompt_editor_message",
        sa.Column("tool_calls", JSONB, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("prompt_editor_message", "tool_calls")
    op.drop_column("prompt_editor_session", "edited_prompt")
    op.drop_column("prompt_editor_session", "base_prompt")
    op.add_column(
        "prompt_editor_message",
        sa.Column("prompt_suggestion", sa.Text(), nullable=True),
    )
    op.add_column(
        "prompt_editor_message",
        sa.Column("suggestion_status", sa.String(length=32), nullable=True),
    )
