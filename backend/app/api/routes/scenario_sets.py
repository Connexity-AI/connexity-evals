import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from app import crud
from app.api.deps import SessionDep, get_current_user
from app.models import (
    Message,
    ScenarioSet,
    ScenarioSetCreate,
    ScenarioSetMembersPublic,
    ScenarioSetMembersUpdate,
    ScenarioSetPublic,
    ScenarioSetsPublic,
    ScenarioSetUpdate,
)


def _to_public(
    session: SessionDep,
    scenario_set: ScenarioSet,
    *,
    scenario_count: int | None = None,
    sum_member_repetitions: int | None = None,
) -> ScenarioSetPublic:
    """Convert a ScenarioSet ORM object to ScenarioSetPublic with counts.

    When listing sets, pass ``scenario_count`` and ``sum_member_repetitions`` from
    batched queries to avoid N+1 round-trips.
    """
    count = (
        scenario_count
        if scenario_count is not None
        else crud.count_scenarios_in_set(
            session=session, scenario_set_id=scenario_set.id
        )
    )
    sum_rep = (
        sum_member_repetitions
        if sum_member_repetitions is not None
        else crud.sum_member_repetitions_in_set(
            session=session, scenario_set_id=scenario_set.id
        )
    )
    effective = sum_rep * scenario_set.set_repetitions
    return ScenarioSetPublic.model_validate(
        scenario_set,
        update={
            "scenario_count": count,
            "effective_scenario_count": effective,
        },
    )


router = APIRouter(
    prefix="/scenario-sets",
    tags=["scenario-sets"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=ScenarioSetPublic)
def create_scenario_set(
    session: SessionDep, scenario_set_in: ScenarioSetCreate
) -> ScenarioSetPublic:
    try:
        scenario_set = crud.create_scenario_set(
            session=session, scenario_set_in=scenario_set_in
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_public(session, scenario_set)


@router.get("/", response_model=ScenarioSetsPublic)
def list_scenario_sets(
    session: SessionDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> ScenarioSetsPublic:
    items, count = crud.list_scenario_sets(session=session, skip=skip, limit=limit)
    ids = [s.id for s in items]
    counts = crud.count_scenarios_in_sets(session=session, scenario_set_ids=ids)
    sum_reps = crud.sum_member_repetitions_in_sets(
        session=session, scenario_set_ids=ids
    )
    public_items = [
        _to_public(
            session,
            item,
            scenario_count=counts.get(item.id, 0),
            sum_member_repetitions=sum_reps.get(item.id, 0),
        )
        for item in items
    ]
    return ScenarioSetsPublic(data=public_items, count=count)


@router.get("/{scenario_set_id}", response_model=ScenarioSetPublic)
def get_scenario_set(
    session: SessionDep, scenario_set_id: uuid.UUID
) -> ScenarioSetPublic:
    scenario_set = crud.get_scenario_set(
        session=session, scenario_set_id=scenario_set_id
    )
    if not scenario_set:
        raise HTTPException(status_code=404, detail="Scenario set not found")
    return _to_public(session, scenario_set)


@router.patch("/{scenario_set_id}", response_model=ScenarioSetPublic)
def update_scenario_set(
    session: SessionDep,
    scenario_set_id: uuid.UUID,
    scenario_set_in: ScenarioSetUpdate,
) -> ScenarioSetPublic:
    scenario_set = crud.get_scenario_set(
        session=session, scenario_set_id=scenario_set_id
    )
    if not scenario_set:
        raise HTTPException(status_code=404, detail="Scenario set not found")
    updated = crud.update_scenario_set(
        session=session,
        db_scenario_set=scenario_set,
        scenario_set_in=scenario_set_in,
    )
    return _to_public(session, updated)


@router.delete("/{scenario_set_id}", response_model=Message)
def delete_scenario_set(session: SessionDep, scenario_set_id: uuid.UUID) -> Message:
    scenario_set = crud.get_scenario_set(
        session=session, scenario_set_id=scenario_set_id
    )
    if not scenario_set:
        raise HTTPException(status_code=404, detail="Scenario set not found")
    crud.delete_scenario_set(session=session, db_scenario_set=scenario_set)
    return Message(message="Scenario set deleted successfully")


# ── Member management ─────────────────────────────────────────────────


@router.get("/{scenario_set_id}/scenarios", response_model=ScenarioSetMembersPublic)
def list_scenarios_in_set(
    session: SessionDep,
    scenario_set_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> ScenarioSetMembersPublic:
    scenario_set = crud.get_scenario_set(
        session=session, scenario_set_id=scenario_set_id
    )
    if not scenario_set:
        raise HTTPException(status_code=404, detail="Scenario set not found")
    members, count = crud.list_scenarios_in_set(
        session=session, scenario_set_id=scenario_set_id, skip=skip, limit=limit
    )
    return ScenarioSetMembersPublic(data=members, count=count)


@router.post("/{scenario_set_id}/scenarios", response_model=ScenarioSetPublic)
def add_scenarios_to_set(
    session: SessionDep,
    scenario_set_id: uuid.UUID,
    body: ScenarioSetMembersUpdate,
) -> ScenarioSetPublic:
    scenario_set = crud.get_scenario_set(
        session=session, scenario_set_id=scenario_set_id
    )
    if not scenario_set:
        raise HTTPException(status_code=404, detail="Scenario set not found")
    try:
        updated = crud.add_scenarios_to_set(
            session=session,
            db_scenario_set=scenario_set,
            members=body.members,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_public(session, updated)


@router.put("/{scenario_set_id}/scenarios", response_model=ScenarioSetPublic)
def replace_scenarios_in_set(
    session: SessionDep,
    scenario_set_id: uuid.UUID,
    body: ScenarioSetMembersUpdate,
) -> ScenarioSetPublic:
    scenario_set = crud.get_scenario_set(
        session=session, scenario_set_id=scenario_set_id
    )
    if not scenario_set:
        raise HTTPException(status_code=404, detail="Scenario set not found")
    try:
        updated = crud.replace_scenarios_in_set(
            session=session,
            db_scenario_set=scenario_set,
            members=body.members,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _to_public(session, updated)


@router.delete(
    "/{scenario_set_id}/scenarios/{scenario_id}", response_model=ScenarioSetPublic
)
def remove_scenario_from_set(
    session: SessionDep,
    scenario_set_id: uuid.UUID,
    scenario_id: uuid.UUID,
) -> ScenarioSetPublic:
    scenario_set = crud.get_scenario_set(
        session=session, scenario_set_id=scenario_set_id
    )
    if not scenario_set:
        raise HTTPException(status_code=404, detail="Scenario set not found")
    updated = crud.remove_scenario_from_set(
        session=session,
        db_scenario_set=scenario_set,
        scenario_id=scenario_id,
    )
    return _to_public(session, updated)
