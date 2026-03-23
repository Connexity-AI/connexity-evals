from sqlmodel import Session

from app import crud
from app.models import (
    Difficulty,
    ScenarioCreate,
    ScenarioStatus,
    ScenarioUpdate,
)
from app.tests.utils.eval import create_test_scenario


def test_create_scenario(db: Session) -> None:
    scenario_in = ScenarioCreate(
        name="CRUD Test Scenario",
        tags=["billing", "refund"],
        difficulty=Difficulty.HARD,
    )
    scenario = crud.create_scenario(session=db, scenario_in=scenario_in)
    assert scenario.name == "CRUD Test Scenario"
    assert scenario.tags == ["billing", "refund"]
    assert scenario.difficulty == Difficulty.HARD
    assert scenario.id is not None


def test_get_scenario(db: Session) -> None:
    scenario = create_test_scenario(db)
    fetched = crud.get_scenario(session=db, scenario_id=scenario.id)
    assert fetched is not None
    assert fetched.id == scenario.id


def test_list_scenarios(db: Session) -> None:
    create_test_scenario(db, tags=["list-test"])
    items, count = crud.list_scenarios(session=db)
    assert count >= 1
    assert len(items) >= 1


def test_list_scenarios_filter_by_tag(db: Session) -> None:
    tag = "unique-tag-filter-test"
    create_test_scenario(db, tags=[tag])
    items, count = crud.list_scenarios(session=db, tag=tag)
    assert count >= 1
    assert all(tag in s.tags for s in items)


def test_list_scenarios_filter_by_difficulty(db: Session) -> None:
    create_test_scenario(db, difficulty=Difficulty.HARD)
    items, count = crud.list_scenarios(session=db, difficulty=Difficulty.HARD)
    assert count >= 1
    assert all(s.difficulty == Difficulty.HARD for s in items)


def test_list_scenarios_filter_by_status(db: Session) -> None:
    create_test_scenario(db, status=ScenarioStatus.ARCHIVED)
    items, count = crud.list_scenarios(session=db, status=ScenarioStatus.ARCHIVED)
    assert count >= 1
    assert all(s.status == ScenarioStatus.ARCHIVED for s in items)


def test_list_scenarios_combined_filters(db: Session) -> None:
    tag = "combined-filter-test"
    create_test_scenario(
        db,
        tags=[tag],
        difficulty=Difficulty.HARD,
        status=ScenarioStatus.ACTIVE,
    )
    items, count = crud.list_scenarios(
        session=db,
        tag=tag,
        difficulty=Difficulty.HARD,
        status=ScenarioStatus.ACTIVE,
    )
    assert count >= 1


def test_update_scenario(db: Session) -> None:
    scenario = create_test_scenario(db)
    updated = crud.update_scenario(
        session=db,
        db_scenario=scenario,
        scenario_in=ScenarioUpdate(name="Updated Scenario", tags=["updated"]),
    )
    assert updated.name == "Updated Scenario"
    assert updated.tags == ["updated"]


def test_delete_scenario(db: Session) -> None:
    scenario = create_test_scenario(db)
    scenario_id = scenario.id
    crud.delete_scenario(session=db, db_scenario=scenario)
    fetched = crud.get_scenario(session=db, scenario_id=scenario_id)
    assert fetched is None
