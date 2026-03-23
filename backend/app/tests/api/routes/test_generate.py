from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.tests.generator.conftest import MOCK_LLM_RESPONSE


async def _mock_generate(request):  # type: ignore[no-untyped-def]
    """Return pre-built ScenarioCreate objects from mock data."""
    from app.generator.core import _parse_scenarios

    scenarios = _parse_scenarios(MOCK_LLM_RESPONSE, expected_count=request.count)
    return scenarios, "gpt-4o", 1500


def test_generate_scenarios_endpoint_success(
    client: TestClient, superuser_auth_cookies: dict[str, str]
) -> None:
    with patch(
        "app.api.routes.scenarios.generate_scenarios",
        new_callable=AsyncMock,
        side_effect=_mock_generate,
    ):
        r = client.post(
            f"{settings.API_V1_STR}/scenarios/generate",
            json={"agent_prompt": "You are a helpful agent.", "count": 10},
            cookies=superuser_auth_cookies,
        )
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 10
    assert data["model_used"] == "gpt-4o"
    assert data["generation_time_ms"] == 1500
    assert len(data["scenarios"]) == 10


def test_generate_scenarios_persists_drafts(
    client: TestClient, superuser_auth_cookies: dict[str, str]
) -> None:
    with patch(
        "app.api.routes.scenarios.generate_scenarios",
        new_callable=AsyncMock,
        side_effect=_mock_generate,
    ):
        r = client.post(
            f"{settings.API_V1_STR}/scenarios/generate",
            json={"agent_prompt": "You are a helpful agent.", "persist": True},
            cookies=superuser_auth_cookies,
        )
    assert r.status_code == 200
    data = r.json()
    for scenario in data["scenarios"]:
        assert scenario["status"] == "draft"
        assert scenario["id"] is not None


def test_generate_scenarios_no_persist(
    client: TestClient, superuser_auth_cookies: dict[str, str]
) -> None:
    with patch(
        "app.api.routes.scenarios.generate_scenarios",
        new_callable=AsyncMock,
        side_effect=_mock_generate,
    ):
        r = client.post(
            f"{settings.API_V1_STR}/scenarios/generate",
            json={
                "agent_prompt": "You are a helpful agent.",
                "persist": False,
            },
            cookies=superuser_auth_cookies,
        )
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 10


def test_generate_scenarios_unauthenticated(client: TestClient) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/scenarios/generate",
        json={"agent_prompt": "You are a helpful agent."},
    )
    assert r.status_code in (401, 403)


def test_generate_scenarios_llm_error(
    client: TestClient, superuser_auth_cookies: dict[str, str]
) -> None:
    with patch(
        "app.api.routes.scenarios.generate_scenarios",
        new_callable=AsyncMock,
        side_effect=Exception("LLM unavailable"),
    ):
        r = client.post(
            f"{settings.API_V1_STR}/scenarios/generate",
            json={"agent_prompt": "You are a helpful agent."},
            cookies=superuser_auth_cookies,
        )
    assert r.status_code == 502


def test_generate_scenarios_invalid_request(
    client: TestClient, superuser_auth_cookies: dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/scenarios/generate",
        json={},
        cookies=superuser_auth_cookies,
    )
    assert r.status_code == 422
