import json

import pytest
from pydantic import ValidationError

from app.models.agent_contract import (
    AgentResponse,
    ChatMessage,
    TokenUsage,
)
from app.models.enums import TurnRole
from app.models.schemas import ToolCall, ToolCallFunction


def _round_trip(model_class, instance):
    data = instance.model_dump()
    restored = model_class.model_validate(data)
    assert restored == instance
    return restored


def test_agent_response_single_assistant_message():
    resp = AgentResponse(
        messages=[
            ChatMessage(
                role=TurnRole.ASSISTANT,
                content="Hello, how can I help?",
            ),
        ],
        model="gpt-4o",
        provider="openai",
        usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        metadata={"run_id": "r1"},
    )
    restored = _round_trip(AgentResponse, resp)
    assert len(restored.messages) == 1
    assert restored.messages[0].role == TurnRole.ASSISTANT
    assert restored.model == "gpt-4o"
    assert restored.provider == "openai"
    assert restored.usage is not None
    assert restored.usage.prompt_tokens == 10
    assert restored.metadata == {"run_id": "r1"}


def test_agent_response_tool_flow():
    resp = AgentResponse(
        messages=[
            ChatMessage(
                role=TurnRole.ASSISTANT,
                content="Checking…",
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        function=ToolCallFunction(
                            name="check_service_area",
                            arguments='{"zone": "V4T0A7"}',
                        ),
                    ),
                ],
            ),
            ChatMessage(
                role=TurnRole.TOOL,
                tool_call_id="call_1",
                name="check_service_area",
                content='{"serviced": true}',
            ),
            ChatMessage(
                role=TurnRole.ASSISTANT,
                content="We service that area.",
            ),
        ],
        model="gpt-4o-mini",
        provider="openai",
        usage=TokenUsage(prompt_tokens=100, completion_tokens=40),
        metadata={},
    )
    restored = _round_trip(AgentResponse, resp)
    assert len(restored.messages) == 3
    assert restored.messages[1].role == TurnRole.TOOL
    assert restored.messages[1].tool_call_id == "call_1"
    assert restored.messages[0].tool_calls is not None
    assert restored.messages[0].tool_calls[0].function.name == "check_service_area"


def test_agent_response_optional_fields_omitted():
    resp = AgentResponse(
        messages=[ChatMessage(role=TurnRole.ASSISTANT, content="Hi")],
    )
    restored = _round_trip(AgentResponse, resp)
    assert restored.model is None
    assert restored.provider is None
    assert restored.usage is None
    assert restored.metadata is None


def test_agent_response_json_round_trip():
    """Simulate JSON wire: model → dict → JSON string → dict → model."""
    resp = AgentResponse(
        messages=[
            ChatMessage(role=TurnRole.ASSISTANT, content="Refused."),
        ],
        model="gpt-4o",
        provider="openai",
        metadata={},
    )
    json_str = json.dumps(resp.model_dump(), default=str)
    raw = json.loads(json_str)
    restored = AgentResponse.model_validate(raw)
    assert restored.messages[0].content == "Refused."
    assert restored.provider == "openai"


def test_agent_response_rejects_non_assistant_last_message():
    with pytest.raises(ValidationError, match="must end with an assistant message"):
        AgentResponse(
            messages=[
                ChatMessage(role=TurnRole.ASSISTANT, content="Checking…"),
                ChatMessage(
                    role=TurnRole.TOOL,
                    tool_call_id="call_1",
                    name="search",
                    content="result",
                ),
            ],
        )
