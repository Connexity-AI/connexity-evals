import uuid

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import (
    Scenario,
    ScenarioSet,
    ScenarioSetCreate,
    ScenarioSetMember,
    ScenarioSetUpdate,
)


def create_scenario_set(
    *, session: Session, scenario_set_in: ScenarioSetCreate
) -> ScenarioSet:
    create_data = scenario_set_in.model_dump(exclude={"scenario_ids"})
    db_obj = ScenarioSet.model_validate(create_data)
    session.add(db_obj)
    session.flush()  # generate id without committing — members use the same transaction

    if scenario_set_in.scenario_ids:
        for position, scenario_id in enumerate(scenario_set_in.scenario_ids):
            member = ScenarioSetMember(
                scenario_set_id=db_obj.id,
                scenario_id=scenario_id,
                position=position,
            )
            session.add(member)

    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_scenario_set(
    *, session: Session, scenario_set_id: uuid.UUID
) -> ScenarioSet | None:
    return session.get(ScenarioSet, scenario_set_id)


def list_scenario_sets(
    *, session: Session, skip: int = 0, limit: int = 100
) -> tuple[list[ScenarioSet], int]:
    count = session.exec(select(func.count()).select_from(ScenarioSet)).one()
    items = list(session.exec(select(ScenarioSet).offset(skip).limit(limit)).all())
    return items, count


def update_scenario_set(
    *,
    session: Session,
    db_scenario_set: ScenarioSet,
    scenario_set_in: ScenarioSetUpdate,
) -> ScenarioSet:
    update_data = scenario_set_in.model_dump(exclude_unset=True)
    db_scenario_set.sqlmodel_update(update_data)
    session.add(db_scenario_set)
    session.commit()
    session.refresh(db_scenario_set)
    return db_scenario_set


def delete_scenario_set(*, session: Session, db_scenario_set: ScenarioSet) -> None:
    session.delete(db_scenario_set)
    session.commit()


def _bump_version(*, scenario_set: ScenarioSet) -> None:
    """Increment the version of a scenario set in place."""
    scenario_set.version += 1


def _next_position(*, session: Session, scenario_set_id: uuid.UUID) -> int:
    """Return max(position) + 1 for existing members, or 0 if empty."""
    result = session.exec(
        select(func.max(ScenarioSetMember.position)).where(
            ScenarioSetMember.scenario_set_id == scenario_set_id
        )
    ).one()
    return (result + 1) if result is not None else 0


def add_scenarios_to_set(
    *,
    session: Session,
    db_scenario_set: ScenarioSet,
    scenario_ids: list[uuid.UUID],
) -> ScenarioSet:
    next_pos = _next_position(session=session, scenario_set_id=db_scenario_set.id)
    for i, scenario_id in enumerate(scenario_ids):
        member = ScenarioSetMember(
            scenario_set_id=db_scenario_set.id,
            scenario_id=scenario_id,
            position=next_pos + i,
        )
        session.add(member)
    _bump_version(scenario_set=db_scenario_set)
    session.commit()
    session.refresh(db_scenario_set)
    return db_scenario_set


def remove_scenario_from_set(
    *,
    session: Session,
    db_scenario_set: ScenarioSet,
    scenario_id: uuid.UUID,
) -> ScenarioSet:
    member = session.exec(
        select(ScenarioSetMember).where(
            ScenarioSetMember.scenario_set_id == db_scenario_set.id,
            ScenarioSetMember.scenario_id == scenario_id,
        )
    ).first()
    if member:
        session.delete(member)
        _bump_version(scenario_set=db_scenario_set)
    session.commit()
    session.refresh(db_scenario_set)
    return db_scenario_set


def replace_scenarios_in_set(
    *,
    session: Session,
    db_scenario_set: ScenarioSet,
    scenario_ids: list[uuid.UUID],
) -> ScenarioSet:
    # Delete existing members
    existing = session.exec(
        select(ScenarioSetMember).where(
            ScenarioSetMember.scenario_set_id == db_scenario_set.id
        )
    ).all()
    for member in existing:
        session.delete(member)
    session.flush()

    # Insert new members
    for position, scenario_id in enumerate(scenario_ids):
        member = ScenarioSetMember(
            scenario_set_id=db_scenario_set.id,
            scenario_id=scenario_id,
            position=position,
        )
        session.add(member)

    _bump_version(scenario_set=db_scenario_set)
    session.commit()
    session.refresh(db_scenario_set)
    return db_scenario_set


def count_scenarios_in_set(*, session: Session, scenario_set_id: uuid.UUID) -> int:
    return session.exec(
        select(func.count()).where(ScenarioSetMember.scenario_set_id == scenario_set_id)
    ).one()


def list_scenarios_in_set(
    *, session: Session, scenario_set_id: uuid.UUID
) -> list[Scenario]:
    statement = (
        select(Scenario)
        .join(ScenarioSetMember, Scenario.id == ScenarioSetMember.scenario_id)
        .where(ScenarioSetMember.scenario_set_id == scenario_set_id)
        .order_by(ScenarioSetMember.position)
    )
    return list(session.exec(statement).all())
