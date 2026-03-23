import uuid

from sqlalchemy import func
from sqlmodel import Session, col, select

from app.models import (
    Difficulty,
    OnConflict,
    Scenario,
    ScenarioCreate,
    ScenarioImportItem,
    ScenarioImportResult,
    ScenarioStatus,
    ScenarioUpdate,
)


def create_scenario(*, session: Session, scenario_in: ScenarioCreate) -> Scenario:
    db_obj = Scenario.model_validate(scenario_in.model_dump())
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_scenario(*, session: Session, scenario_id: uuid.UUID) -> Scenario | None:
    return session.get(Scenario, scenario_id)


def list_scenarios(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    tag: str | None = None,
    difficulty: Difficulty | None = None,
    status: ScenarioStatus | None = None,
) -> tuple[list[Scenario], int]:
    statement = select(Scenario)
    count_statement = select(func.count()).select_from(Scenario)

    if tag is not None:
        statement = statement.where(col(Scenario.tags).any(tag))
        count_statement = count_statement.where(col(Scenario.tags).any(tag))
    if difficulty is not None:
        statement = statement.where(Scenario.difficulty == difficulty)
        count_statement = count_statement.where(Scenario.difficulty == difficulty)
    if status is not None:
        statement = statement.where(Scenario.status == status)
        count_statement = count_statement.where(Scenario.status == status)

    count = session.exec(count_statement).one()
    items = list(session.exec(statement.offset(skip).limit(limit)).all())
    return items, count


def update_scenario(
    *, session: Session, db_scenario: Scenario, scenario_in: ScenarioUpdate
) -> Scenario:
    update_data = scenario_in.model_dump(exclude_unset=True)
    db_scenario.sqlmodel_update(update_data)
    session.add(db_scenario)
    session.commit()
    session.refresh(db_scenario)
    return db_scenario


def delete_scenario(*, session: Session, db_scenario: Scenario) -> None:
    session.delete(db_scenario)
    session.commit()


def export_scenarios(
    *,
    session: Session,
    tag: str | None = None,
    difficulty: Difficulty | None = None,
    status: ScenarioStatus | None = None,
) -> list[Scenario]:
    """Export all scenarios matching optional filters (no pagination)."""
    statement = select(Scenario)

    if tag is not None:
        statement = statement.where(col(Scenario.tags).any(tag))
    if difficulty is not None:
        statement = statement.where(Scenario.difficulty == difficulty)
    if status is not None:
        statement = statement.where(Scenario.status == status)

    return list(session.exec(statement).all())


def bulk_import_scenarios(
    *,
    session: Session,
    scenarios_in: list[ScenarioImportItem],
    on_conflict: OnConflict,
) -> ScenarioImportResult:
    """Import scenarios in bulk. Handles ID conflicts via on_conflict strategy."""
    created = 0
    skipped = 0
    overwritten = 0

    # Batch-fetch existing scenarios for items that provide an id
    incoming_ids = [item.id for item in scenarios_in if item.id is not None]
    existing: dict[uuid.UUID, Scenario] = {}
    if incoming_ids:
        rows = session.exec(
            select(Scenario).where(col(Scenario.id).in_(incoming_ids))
        ).all()
        existing = {row.id: row for row in rows}

    for item in scenarios_in:
        data = item.model_dump(exclude={"id"})

        if item.id is None:
            # No id provided — always create new
            db_obj = Scenario.model_validate(data)
            session.add(db_obj)
            created += 1
        elif item.id in existing:
            # Id exists in DB — apply conflict strategy
            if on_conflict == OnConflict.SKIP:
                skipped += 1
            else:
                existing[item.id].sqlmodel_update(data)
                session.add(existing[item.id])
                overwritten += 1
        else:
            # Id provided but not in DB — create with that id
            db_obj = Scenario.model_validate({**data, "id": item.id})
            session.add(db_obj)
            created += 1

    session.commit()

    return ScenarioImportResult(
        created=created,
        skipped=skipped,
        overwritten=overwritten,
        total=len(scenarios_in),
    )
