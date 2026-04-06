"""scenario agent_id, set/member repetitions, result repetition indices

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-04-06 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "e4f5a6b7c8d9"
down_revision = "d3e4f5a6b7c8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "scenario",
        sa.Column("agent_id", sa.Uuid(), nullable=True),
    )
    op.create_index("ix_scenario_agent_id", "scenario", ["agent_id"], unique=False)
    op.create_foreign_key(
        "fk_scenario_agent_id_agent",
        "scenario",
        "agent",
        ["agent_id"],
        ["id"],
    )

    op.add_column(
        "scenario_set_member",
        sa.Column(
            "repetitions",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )
    op.create_check_constraint(
        "ck_scenario_set_member_repetitions_ge_1",
        "scenario_set_member",
        "repetitions >= 1",
    )

    op.add_column(
        "scenario_set",
        sa.Column(
            "set_repetitions",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )
    op.create_check_constraint(
        "ck_scenario_set_set_repetitions_ge_1",
        "scenario_set",
        "set_repetitions >= 1",
    )

    op.add_column(
        "scenario_result",
        sa.Column(
            "repetition_index",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "scenario_result",
        sa.Column(
            "set_repetition_index",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("scenario_result", "set_repetition_index")
    op.drop_column("scenario_result", "repetition_index")

    op.drop_constraint(
        "ck_scenario_set_set_repetitions_ge_1",
        "scenario_set",
        type_="check",
    )
    op.drop_column("scenario_set", "set_repetitions")

    op.drop_constraint(
        "ck_scenario_set_member_repetitions_ge_1",
        "scenario_set_member",
        type_="check",
    )
    op.drop_column("scenario_set_member", "repetitions")

    op.drop_constraint("fk_scenario_agent_id_agent", "scenario", type_="foreignkey")
    op.drop_index("ix_scenario_agent_id", table_name="scenario")
    op.drop_column("scenario", "agent_id")
