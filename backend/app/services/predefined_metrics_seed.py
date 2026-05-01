"""Idempotent seeding of the nine built-in (predefined) metrics into the
``custom_metric`` table.

The Alembic migration that introduced ``is_predefined`` / ``is_draft`` only
seeds when a user already exists at migration time, so a brand-new DB started
without any users would end up with zero predefined metrics. This module
provides a runtime safety net: the metrics list endpoints call
``ensure_predefined_metrics_seeded`` with the current request's user and
inserts any missing rows on first access.
"""

from __future__ import annotations

import uuid

from sqlmodel import Session, col, select

from app.models.custom_metric import CustomMetric
from app.models.enums import MetricTier, ScoreType
from app.services.judge_metrics import METRIC_REGISTRY


def ensure_predefined_metrics_seeded(
    *, session: Session, owner_id: uuid.UUID
) -> None:
    """Insert any missing predefined metric rows. Safe to call on every list."""
    existing_names = set(
        session.exec(
            select(CustomMetric.name).where(
                col(CustomMetric.is_predefined).is_(True),
                col(CustomMetric.deleted_at).is_(None),
            )
        ).all()
    )

    missing = [m for m in METRIC_REGISTRY.values() if m.name not in existing_names]
    if not missing:
        return

    for definition in missing:
        row = CustomMetric(
            name=definition.name,
            display_name=definition.display_name,
            description=definition.description,
            tier=MetricTier(definition.tier),
            default_weight=definition.default_weight,
            score_type=ScoreType(definition.score_type),
            rubric=definition.rubric,
            include_in_defaults=definition.include_in_defaults,
            is_predefined=True,
            is_draft=False,
            created_by=owner_id,
        )
        session.add(row)
    session.commit()
