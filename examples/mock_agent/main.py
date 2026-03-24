from __future__ import annotations

import json
import os
from typing import Literal

import litellm
from fastapi import FastAPI
from pydantic import BaseModel

SYSTEM_PROMPT = (
    "You are a helpful customer support agent for a home services company. "
    "You help customers book duct cleaning, plumbing, and HVAC services. "
    "When a customer provides a postal code, call the check_service_area tool. "
    "Keep responses concise and professional."
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_service_area",
            "description": "Check whether we service a given postal/zip code area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "zone": {
                        "type": "string",
                        "description": "Postal or zip code (whitespace stripped)",
                    }
                },
                "required": ["zone"],
            },
        },
    }
]

MODEL = os.getenv("MOCK_AGENT_MODEL", "gpt-4o-mini")

app = FastAPI(title="Connexity mock agent", version="0.1.0")


class ToolFn(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str
    type: Literal["function"] = "function"
    function: ToolFn


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None
    name: str | None = None


class AgentMetadata(BaseModel):
    scenario_id: str | None = None
    turn_index: int | None = None


class AgentRequest(BaseModel):
    messages: list[ChatMessage]
    metadata: AgentMetadata | None = None


class TokenUsage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class AgentResponse(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    usage: TokenUsage | None = None


def _build_litellm_messages(messages: list[ChatMessage]) -> list[dict]:
    has_system = any(m.role == "system" for m in messages)
    out: list[dict] = []
    if not has_system:
        out.append({"role": "system", "content": SYSTEM_PROMPT})
    for m in messages:
        msg: dict = {"role": m.role}
        if m.content is not None:
            msg["content"] = m.content
        if m.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in m.tool_calls
            ]
        if m.tool_call_id:
            msg["tool_call_id"] = m.tool_call_id
        if m.name:
            msg["name"] = m.name
        out.append(msg)
    return out


def _parse_tool_calls(raw_calls: list) -> list[ToolCall] | None:
    if not raw_calls:
        return None
    result: list[ToolCall] = []
    for rc in raw_calls:
        fn = rc.function if hasattr(rc, "function") else rc.get("function", {})
        name = fn.name if hasattr(fn, "name") else fn.get("name", "")
        arguments = fn.arguments if hasattr(fn, "arguments") else fn.get("arguments", "{}")
        result.append(
            ToolCall(
                id=rc.id if hasattr(rc, "id") else rc.get("id", ""),
                function=ToolFn(
                    name=name,
                    arguments=arguments if isinstance(arguments, str) else json.dumps(arguments),
                ),
            )
        )
    return result


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent/respond", response_model=AgentResponse)
async def respond(body: AgentRequest) -> AgentResponse:
    llm_messages = _build_litellm_messages(body.messages)
    response = await litellm.acompletion(
        model=MODEL,
        messages=llm_messages,
        tools=TOOLS,
        temperature=0,
    )
    choice = response.choices[0].message

    content = choice.content if isinstance(choice.content, str) else None
    tool_calls = _parse_tool_calls(choice.tool_calls) if choice.tool_calls else None

    usage_out: TokenUsage | None = None
    if response.usage:
        usage_out = TokenUsage(
            prompt_tokens=getattr(response.usage, "prompt_tokens", None),
            completion_tokens=getattr(response.usage, "completion_tokens", None),
            total_tokens=getattr(response.usage, "total_tokens", None),
        )

    return AgentResponse(content=content, tool_calls=tool_calls, usage=usage_out)
