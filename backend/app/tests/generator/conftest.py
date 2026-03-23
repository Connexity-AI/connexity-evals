"""Generator tests are pure unit tests — no DB required."""

import json
from collections.abc import Generator

import pytest


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[None, None, None]:
    yield


MOCK_SCENARIOS_RAW: list[dict] = [
    {
        "name": f"Test Scenario {i}",
        "description": f"Test scenario description {i}",
        "difficulty": "normal" if i % 3 != 0 else "hard",
        "tags": [
            ["normal", "happy-path"],
            ["edge-case", "boundary"],
            ["red-team", "adversarial"],
        ][i % 3],
        "status": "draft",
        "persona": {
            "type": f"test-persona-{i}",
            "description": f"A test persona for scenario {i}",
            "instructions": f"Behave as persona {i} would.",
        },
        "initial_message": f"Hello, this is test message {i}.",
        "user_context": {"scenario_index": i, "test": True},
        "max_turns": 10,
        "expected_outcomes": {"success": True, "scenario_index": i},
        "expected_tool_calls": [
            {"tool": "test_tool", "expected_params": {"id": str(i)}}
        ],
    }
    for i in range(10)
]

MOCK_LLM_RESPONSE = json.dumps(MOCK_SCENARIOS_RAW)


@pytest.fixture()
def mock_llm_response() -> str:
    return MOCK_LLM_RESPONSE


@pytest.fixture()
def mock_scenarios_raw() -> list[dict]:
    return list(MOCK_SCENARIOS_RAW)
