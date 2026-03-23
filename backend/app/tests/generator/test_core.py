import json
from unittest.mock import AsyncMock, patch

import pytest

from app.generator.core import _parse_scenarios, generate_scenarios
from app.generator.schemas import GenerateRequest
from app.models.scenario import ScenarioCreate
from app.services.llm import LLMResponse

from .conftest import MOCK_LLM_RESPONSE, MOCK_SCENARIOS_RAW


def _fake_llm_response(content: str = MOCK_LLM_RESPONSE) -> LLMResponse:
    return LLMResponse(
        content=content,
        model="gpt-4o",
        usage={"prompt_tokens": 100, "completion_tokens": 500, "total_tokens": 600},
        latency_ms=1500,
    )


def test_parse_scenarios_valid_json(mock_llm_response: str) -> None:
    scenarios = _parse_scenarios(mock_llm_response, expected_count=10)
    assert len(scenarios) == 10
    assert all(isinstance(s, ScenarioCreate) for s in scenarios)


def test_parse_scenarios_forces_draft_status() -> None:
    data = [
        {
            "name": "Test",
            "status": "active",
            "tags": ["normal"],
            "persona": {
                "type": "user",
                "description": "A user",
                "instructions": "Be a user",
            },
            "initial_message": "Hello",
        }
    ]
    scenarios = _parse_scenarios(json.dumps(data), expected_count=1)
    assert scenarios[0].status.value == "draft"


def test_parse_scenarios_strips_markdown_fences() -> None:
    wrapped = f"```json\n{MOCK_LLM_RESPONSE}\n```"
    scenarios = _parse_scenarios(wrapped, expected_count=10)
    assert len(scenarios) == 10


def test_parse_scenarios_invalid_json_raises() -> None:
    with pytest.raises(json.JSONDecodeError):
        _parse_scenarios("not valid json at all", expected_count=1)


def test_parse_scenarios_not_array_raises() -> None:
    with pytest.raises(ValueError, match="not a JSON array"):
        _parse_scenarios('{"key": "value"}', expected_count=1)


def test_parse_scenarios_partial_results_logs_warning() -> None:
    # Only 1 scenario but expecting 5
    data = [MOCK_SCENARIOS_RAW[0]]
    with patch("app.generator.core.logger") as mock_logger:
        scenarios = _parse_scenarios(json.dumps(data), expected_count=5)
        assert len(scenarios) == 1
        mock_logger.warning.assert_called_once()


@pytest.mark.asyncio
async def test_generate_scenarios_calls_llm() -> None:
    request = GenerateRequest(
        agent_prompt="You are a test agent.",
        tools=[],
        count=10,
    )
    with patch(
        "app.generator.core.call_llm",
        new_callable=AsyncMock,
        return_value=_fake_llm_response(),
    ) as mock_call:
        scenarios, model_used, latency_ms = await generate_scenarios(request)

    assert len(scenarios) == 10
    assert latency_ms == 1500
    assert model_used == "gpt-4o"
    mock_call.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_scenarios_uses_config_default_model() -> None:
    request = GenerateRequest(
        agent_prompt="You are a test agent.",
        tools=[],
        count=10,
    )
    with (
        patch(
            "app.generator.core.call_llm",
            new_callable=AsyncMock,
            return_value=_fake_llm_response(),
        ),
        patch("app.generator.core.settings") as mock_settings,
    ):
        mock_settings.LLM_DEFAULT_MODEL = "gpt-4o"
        mock_settings.GENERATOR_MAX_TOKENS = 16_000
        _, model_used, _ = await generate_scenarios(request)

    assert model_used == "gpt-4o"


@pytest.mark.asyncio
async def test_generate_scenarios_respects_model_override() -> None:
    request = GenerateRequest(
        agent_prompt="You are a test agent.",
        tools=[],
        count=10,
        model="gpt-4o-mini",
    )
    resp = _fake_llm_response()
    resp.model = "gpt-4o-mini"
    with (
        patch(
            "app.generator.core.call_llm",
            new_callable=AsyncMock,
            return_value=resp,
        ) as mock_call,
        patch("app.generator.core.settings") as mock_settings,
    ):
        mock_settings.LLM_DEFAULT_MODEL = "gpt-4o"
        mock_settings.GENERATOR_MAX_TOKENS = 16_000
        _, model_used, _ = await generate_scenarios(request)

    assert model_used == "gpt-4o-mini"
    # Verify the config passed to call_llm has the override model
    call_config = mock_call.await_args.kwargs.get("config") or mock_call.await_args[1]
    assert call_config.model == "gpt-4o-mini"
