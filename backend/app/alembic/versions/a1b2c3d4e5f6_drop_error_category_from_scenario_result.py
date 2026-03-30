"""drop error_category from scenario_result

Revision ID: a1b2c3d4e5f6
Revises: 8c3fbf455988
Create Date: 2026-03-30 00:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "8c3fbf455988"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_scenario_result_error_category", table_name="scenario_result")
    op.drop_column("scenario_result", "error_category")
    sa.Enum(name="errorcategory").drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    error_category_enum = sa.Enum(
        "NONE",
        "OFF_TOPIC",
        "HALLUCINATION",
        "REFUSAL",
        "TOOL_MISUSE",
        "SAFETY_VIOLATION",
        "PROMPT_VIOLATION",
        "INCOMPLETE",
        "LATENCY_TIMEOUT",
        "AGENT_ERROR",
        "OTHER",
        name="errorcategory",
    )
    error_category_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "scenario_result",
        sa.Column(
            "error_category",
            error_category_enum,
            nullable=False,
            server_default="NONE",
        ),
    )
    op.create_index(
        "ix_scenario_result_error_category",
        "scenario_result",
        ["error_category"],
    )
