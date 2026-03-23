import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.eval import create_test_scenario


def test_create_scenario(
    client: TestClient, superuser_auth_cookies: dict[str, str]
) -> None:
    data = {
        "name": "Route Scenario",
        "tags": ["billing"],
        "difficulty": "hard",
    }
    r = client.post(
        f"{settings.API_V1_STR}/scenarios/",
        json=data,
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200
    result = r.json()
    assert result["name"] == "Route Scenario"
    assert result["tags"] == ["billing"]
    assert result["difficulty"] == "hard"


def test_list_scenarios(
    client: TestClient, superuser_auth_cookies: dict[str, str], db: Session
) -> None:
    create_test_scenario(db)
    r = client.get(
        f"{settings.API_V1_STR}/scenarios/",
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200
    assert r.json()["count"] >= 1


def test_list_scenarios_filter_by_tag(
    client: TestClient, superuser_auth_cookies: dict[str, str], db: Session
) -> None:
    tag = "route-tag-filter"
    create_test_scenario(db, tags=[tag])
    r = client.get(
        f"{settings.API_V1_STR}/scenarios/",
        params={"tag": tag},
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    assert all(tag in s["tags"] for s in data["data"])


def test_list_scenarios_filter_by_difficulty(
    client: TestClient, superuser_auth_cookies: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/scenarios/",
        params={"difficulty": "hard"},
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200


def test_get_scenario(
    client: TestClient, superuser_auth_cookies: dict[str, str], db: Session
) -> None:
    scenario = create_test_scenario(db)
    r = client.get(
        f"{settings.API_V1_STR}/scenarios/{scenario.id}",
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200
    assert r.json()["id"] == str(scenario.id)


def test_get_scenario_not_found(
    client: TestClient, superuser_auth_cookies: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/scenarios/{uuid.uuid4()}",
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 404


def test_update_scenario(
    client: TestClient, superuser_auth_cookies: dict[str, str], db: Session
) -> None:
    scenario = create_test_scenario(db)
    r = client.patch(
        f"{settings.API_V1_STR}/scenarios/{scenario.id}",
        json={"name": "Patched Scenario"},
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Patched Scenario"


def test_delete_scenario(
    client: TestClient, superuser_auth_cookies: dict[str, str], db: Session
) -> None:
    scenario = create_test_scenario(db)
    r = client.delete(
        f"{settings.API_V1_STR}/scenarios/{scenario.id}",
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200


def test_create_scenario_with_full_schema(
    client: TestClient, superuser_auth_cookies: dict[str, str]
) -> None:
    data = {
        "name": "Full Schema Route Test",
        "persona": {
            "type": "polite-customer",
            "description": "A polite customer",
            "instructions": "Be cooperative.",
        },
        "initial_message": "Hello, I need help.",
        "user_context": {"order_id": "ORD-99999"},
        "max_turns": 10,
        "expected_outcomes": {"issue_resolved": True},
        "expected_tool_calls": [
            {"tool": "lookup_order", "expected_params": {"order_id": "ORD-99999"}},
        ],
    }
    r = client.post(
        f"{settings.API_V1_STR}/scenarios/",
        json=data,
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200
    result = r.json()
    assert result["persona"]["type"] == "polite-customer"
    assert result["user_context"]["order_id"] == "ORD-99999"
    assert result["expected_outcomes"]["issue_resolved"] is True
    assert result["expected_tool_calls"][0]["tool"] == "lookup_order"
    assert result["max_turns"] == 10


def test_update_scenario_with_new_fields(
    client: TestClient, superuser_auth_cookies: dict[str, str], db: Session
) -> None:
    scenario = create_test_scenario(db)
    r = client.patch(
        f"{settings.API_V1_STR}/scenarios/{scenario.id}",
        json={
            "persona": {
                "type": "angry-customer",
                "description": "An angry customer",
                "instructions": "Express frustration.",
            },
            "expected_outcomes": {"escalated": True},
        },
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200
    result = r.json()
    assert result["persona"]["type"] == "angry-customer"
    assert result["expected_outcomes"]["escalated"] is True


def test_list_scenarios_search(
    client: TestClient, superuser_auth_cookies: dict[str, str], db: Session
) -> None:
    unique = "xyzzy-route-search-unique"
    create_test_scenario(db, name=f"Scenario {unique}")
    r = client.get(
        f"{settings.API_V1_STR}/scenarios/",
        params={"search": unique},
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    assert any(unique in s["name"] for s in data["data"])


def test_list_scenarios_sort(
    client: TestClient, superuser_auth_cookies: dict[str, str], db: Session
) -> None:
    create_test_scenario(db, name="aaa-route-sort")
    create_test_scenario(db, name="zzz-route-sort")
    r = client.get(
        f"{settings.API_V1_STR}/scenarios/",
        params={"sort_by": "name", "sort_dir": "desc"},
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200
    names = [s["name"] for s in r.json()["data"]]
    assert names == sorted(names, reverse=True)


def test_list_scenarios_filter_by_status(
    client: TestClient, superuser_auth_cookies: dict[str, str], db: Session
) -> None:
    create_test_scenario(db, status="archived")
    r = client.get(
        f"{settings.API_V1_STR}/scenarios/",
        params={"status": "archived"},
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    assert all(s["status"] == "archived" for s in data["data"])


def test_replace_scenario(
    client: TestClient, superuser_auth_cookies: dict[str, str], db: Session
) -> None:
    scenario = create_test_scenario(db, name="Original Replace", tags=["old"])
    r = client.put(
        f"{settings.API_V1_STR}/scenarios/{scenario.id}",
        json={
            "name": "Fully Replaced",
            "tags": ["new"],
            "difficulty": "hard",
        },
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200
    result = r.json()
    assert result["name"] == "Fully Replaced"
    assert result["tags"] == ["new"]
    assert result["difficulty"] == "hard"
    assert result["id"] == str(scenario.id)


def test_replace_scenario_not_found(
    client: TestClient, superuser_auth_cookies: dict[str, str]
) -> None:
    r = client.put(
        f"{settings.API_V1_STR}/scenarios/{uuid.uuid4()}",
        json={"name": "Ghost"},
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 404


def test_replace_scenario_resets_defaults(
    client: TestClient, superuser_auth_cookies: dict[str, str], db: Session
) -> None:
    scenario = create_test_scenario(
        db,
        name="Has Persona",
        persona={
            "type": "test",
            "description": "test",
            "instructions": "test",
        },
        max_turns=10,
    )
    r = client.put(
        f"{settings.API_V1_STR}/scenarios/{scenario.id}",
        json={"name": "Minimal Replace"},
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 200
    result = r.json()
    assert result["persona"] is None
    assert result["max_turns"] is None


def test_create_scenario_invalid_persona(
    client: TestClient, superuser_auth_cookies: dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/scenarios/",
        json={
            "name": "Bad Persona",
            "persona": {"description": "missing type and instructions"},
        },
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 422


def test_create_scenario_invalid_expected_tool_calls(
    client: TestClient, superuser_auth_cookies: dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/scenarios/",
        json={
            "name": "Bad Tool Calls",
            "expected_tool_calls": [{"wrong_key": "value"}],
        },
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 422


def test_update_scenario_invalid_persona(
    client: TestClient, superuser_auth_cookies: dict[str, str], db: Session
) -> None:
    scenario = create_test_scenario(db)
    r = client.patch(
        f"{settings.API_V1_STR}/scenarios/{scenario.id}",
        json={"persona": {"description": "missing type"}},
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 422
