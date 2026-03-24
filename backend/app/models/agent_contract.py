"""HTTP contract for agent endpoints (POST /agent/respond).

OpenAI-compatible chat message and tool-call shapes. Reuses :class:`ToolCall`
from :mod:`app.models.schemas` so transcripts and wire payloads share one model.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.models.enums import TurnRole
from app.models.schemas import ToolCall


class AgentRequestMetadata(BaseModel):
    scenario_id: str | None = Field(
        default=None, description="Scenario identifier from the eval platform"
    )
    turn_index: int | None = Field(
        default=None, description="Zero-based turn index in the scenario conversation"
    )


class ChatMessage(BaseModel):
    role: TurnRole = Field(description="Message role: system, user, assistant, or tool")
    content: str | None = Field(
        default=None, description="Text content; null when only tool_calls are sent"
    )
    tool_calls: list[ToolCall] | None = Field(
        default=None, description="Assistant tool calls (OpenAI shape)"
    )
    tool_call_id: str | None = Field(
        default=None,
        description="For role=tool, id of the tool call this message responds to",
    )
    name: str | None = Field(
        default=None,
        description="Optional tool name for role=tool (OpenAI convention)",
    )


class AgentRequest(BaseModel):
    messages: list[ChatMessage] = Field(
        description="Full conversation history in OpenAI chat order"
    )
    metadata: AgentRequestMetadata | None = Field(
        default=None, description="Platform context for logging and evaluation"
    )


class TokenUsage(BaseModel):
    prompt_tokens: int | None = Field(
        default=None, description="Tokens in the prompt context"
    )
    completion_tokens: int | None = Field(
        default=None, description="Tokens in the completion"
    )
    total_tokens: int | None = Field(
        default=None, description="Total tokens if reported by the agent"
    )


class AgentResponse(BaseModel):
    role: Literal["assistant"] = Field(
        default="assistant", description="Always assistant for this contract"
    )
    content: str | None = Field(
        default=None, description="Assistant text reply; may be null if only tool_calls"
    )
    tool_calls: list[ToolCall] | None = Field(
        default=None, description="Optional function calls (OpenAI shape)"
    )
    usage: TokenUsage | None = Field(
        default=None, description="Optional token usage for cost tracking"
    )
