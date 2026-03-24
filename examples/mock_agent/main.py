from __future__ import annotations

import json
import os
from typing import Any, Literal

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
MAX_TOOL_ROUNDS = 10

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
    messages: list[ChatMessage]
    model: str | None = None
    provider: str | None = None
    usage: TokenUsage | None = None
    metadata: dict[str, Any] | None = None


def check_service_area(zone: str) -> dict[str, Any]:
    z = zone.replace(" ", "").upper()
    return {"serviced": True, "region": "Metro Vancouver", "zone": z}


TOOL_REGISTRY: dict[str, Any] = {
    "check_service_area": check_service_area,
}


def _infer_provider(model: str) -> str:
    if "/" in model:
        return model.split("/", 1)[0]
    return "openai"


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


def _assistant_message_from_litellm(choice: Any) -> ChatMessage:
    content = choice.content if isinstance(choice.content, str) else None
    tool_calls = _parse_tool_calls(choice.tool_calls) if choice.tool_calls else None
    return ChatMessage(role="assistant", content=content, tool_calls=tool_calls)


def _run_tool(name: str, arguments_json: str) -> str:
    fn = TOOL_REGISTRY.get(name)
    if fn is None:
        return json.dumps({"error": f"unknown tool: {name}"})
    try:
        args = json.loads(arguments_json) if arguments_json else {}
    except json.JSONDecodeError:
        return json.dumps({"error": "invalid JSON arguments"})
    try:
        out = fn(**args) if isinstance(args, dict) else fn(args)
        return json.dumps(out) if not isinstance(out, str) else out
    except TypeError:
        return json.dumps({"error": "tool argument mismatch"})


def _sum_tokens(a: int | None, b: int | None) -> int | None:
    if a is None and b is None:
        return None
    return (a or 0) + (b or 0)


def _merge_usage(acc: TokenUsage | None, response: Any) -> TokenUsage | None:
    u = getattr(response, "usage", None)
    if not u:
        return acc
    pt = getattr(u, "prompt_tokens", None)
    ct = getattr(u, "completion_tokens", None)
    tt = getattr(u, "total_tokens", None)
    if acc is None:
        if pt is None and ct is None and tt is None:
            return None
        return TokenUsage(prompt_tokens=pt, completion_tokens=ct, total_tokens=tt)
    return TokenUsage(
        prompt_tokens=_sum_tokens(acc.prompt_tokens, pt),
        completion_tokens=_sum_tokens(acc.completion_tokens, ct),
        total_tokens=_sum_tokens(acc.total_tokens, tt),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent/respond", response_model=AgentResponse)
async def respond(body: AgentRequest) -> AgentResponse:
    llm_messages = _build_litellm_messages(body.messages)
    turn_messages: list[ChatMessage] = []
    usage_acc: TokenUsage | None = None

    for _ in range(MAX_TOOL_ROUNDS):
        response = await litellm.acompletion(
            model=MODEL,
            messages=llm_messages,
            tools=TOOLS,
            temperature=0,
        )
        usage_acc = _merge_usage(usage_acc, response)
        choice = response.choices[0].message
        assistant_cm = _assistant_message_from_litellm(choice)
        turn_messages.append(assistant_cm)

        if not choice.tool_calls:
            break

        llm_messages.append(assistant_cm.model_dump())

        for tc in choice.tool_calls:
            fn = tc.function if hasattr(tc, "function") else tc.get("function", {})
            name = fn.name if hasattr(fn, "name") else fn.get("name", "")
            raw_args = fn.arguments if hasattr(fn, "arguments") else fn.get("arguments", "{}")
            args_str = raw_args if isinstance(raw_args, str) else json.dumps(raw_args)
            tid = tc.id if hasattr(tc, "id") else tc.get("id", "")
            result_str = _run_tool(name, args_str)
            tool_cm = ChatMessage(
                role="tool",
                tool_call_id=tid,
                name=name,
                content=result_str,
            )
            turn_messages.append(tool_cm)
            llm_messages.append(tool_cm.model_dump())

    return AgentResponse(
        messages=turn_messages,
        model=MODEL,
        provider=_infer_provider(MODEL),
        usage=usage_acc,
        metadata={},
    )
