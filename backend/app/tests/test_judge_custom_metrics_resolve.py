"""Custom metric resolution needs a real DB session.

``app/tests/services/conftest.py`` overrides ``db`` for service unit tests; these
integration-style checks live at the ``tests`` package root next to the session
``db`` fixture.
"""

import uuid

import pytest
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import CustomMetricCreate, MetricTier, ScoreType
from app.models.schemas import JudgeConfig, MetricSelection
from app.services.judge_metrics import (
    custom_metric_row_to_definition,
    resolve_metrics,
)


def test_custom_metric_row_to_definition_matches_shape(db: Session) -> None:
    owner = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert owner is not None
    name = f"judge_shape_{uuid.uuid4().hex[:10]}"
    row = crud.create_custom_metric(
        session=db,
        metric_in=CustomMetricCreate(
            name=name,
            display_name="Shape",
            description="d",
            tier=MetricTier.EXECUTION,
            default_weight=0.3,
            score_type=ScoreType.SCORED,
            rubric="Measures: x.\n5: y.",
            include_in_defaults=True,
        ),
        owner_id=owner.id,
    )
    d = custom_metric_row_to_definition(row)
    assert d.name == name
    assert d.display_name == "Shape"
    assert d.tier == MetricTier.EXECUTION
    assert d.include_in_defaults is True


def test_resolve_metrics_custom_from_db(db: Session) -> None:
    owner = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert owner is not None
    name = f"custom_res_{uuid.uuid4().hex[:10]}"
    crud.create_custom_metric(
        session=db,
        metric_in=CustomMetricCreate(
            name=name,
            display_name="Custom",
            description="Custom desc",
            tier=MetricTier.PROCESS,
            default_weight=0.4,
            score_type=ScoreType.SCORED,
            rubric="Measures: flow.\n5: Smooth.\n   Example: Agent recovered.",
            include_in_defaults=False,
        ),
        owner_id=owner.id,
    )
    cfg = JudgeConfig(metrics=[MetricSelection(metric=name, weight=2.0)])
    resolved = resolve_metrics(cfg, session=db, owner_id=owner.id)
    assert len(resolved) == 1
    assert resolved[0][0].name == name
    assert abs(resolved[0][1] - 1.0) < 1e-9


def test_resolve_metrics_mixed_builtin_and_custom(db: Session) -> None:
    owner = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert owner is not None
    name = f"mixed_{uuid.uuid4().hex[:10]}"
    crud.create_custom_metric(
        session=db,
        metric_in=CustomMetricCreate(
            name=name,
            display_name="Mixed",
            description="d",
            tier=MetricTier.DELIVERY,
            default_weight=0.5,
            score_type=ScoreType.SCORED,
            rubric="Measures: tone.\n5: Good.\n   Example: Brief reply.",
            include_in_defaults=False,
        ),
        owner_id=owner.id,
    )
    cfg = JudgeConfig(
        metrics=[
            MetricSelection(metric="tool_routing", weight=1.0),
            MetricSelection(metric=name, weight=1.0),
        ]
    )
    resolved = resolve_metrics(cfg, session=db, owner_id=owner.id)
    names = {m.name for m, _ in resolved}
    assert names == {"tool_routing", name}
    assert abs(sum(w for _, w in resolved) - 1.0) < 1e-9


def test_resolve_metrics_custom_wrong_owner(db: Session) -> None:
    owner = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert owner is not None
    name = f"wrong_owner_{uuid.uuid4().hex[:10]}"
    crud.create_custom_metric(
        session=db,
        metric_in=CustomMetricCreate(
            name=name,
            display_name="X",
            description="d",
            tier=MetricTier.KNOWLEDGE,
            default_weight=0.1,
            score_type=ScoreType.BINARY,
            rubric="Measures: x.\n\nPass: a\nExample: b\nFail: c\nExample: d",
            include_in_defaults=False,
        ),
        owner_id=owner.id,
    )
    cfg = JudgeConfig(metrics=[MetricSelection(metric=name, weight=1.0)])
    wrong_id = uuid.uuid4()
    with pytest.raises(ValueError, match="Unknown metric"):
        resolve_metrics(cfg, session=db, owner_id=wrong_id)
