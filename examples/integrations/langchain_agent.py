from __future__ import annotations

import json
from typing import Any, Literal

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="LangChain agent adapter", version="0.1.0")


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


class AgentRequest(BaseModel):
    messages: list[ChatMessage]
    metadata: dict[str, Any] | None = None


class TokenUsage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class AgentResponse(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    usage: TokenUsage | None = None


def platform_to_langchain(messages: list[ChatMessage]) -> list[Any]:
    from langchain_core.messages import (
        AIMessage,
        HumanMessage,
        SystemMessage,
        ToolMessage,
    )

    out: list[Any] = []
    for m in messages:
        if m.role == "system":
            out.append(SystemMessage(content=m.content or ""))
        elif m.role == "user":
            out.append(HumanMessage(content=m.content or ""))
        elif m.role == "assistant":
            if m.tool_calls:
                lc_tool_calls = [
                    {
                        "name": tc.function.name,
                        "args": json.loads(tc.function.arguments),
                        "id": tc.id,
                        "type": "tool_call",
                    }
                    for tc in m.tool_calls
                ]
                out.append(AIMessage(content=m.content or "", tool_calls=lc_tool_calls))
            else:
                out.append(AIMessage(content=m.content or ""))
        elif m.role == "tool":
            out.append(
                ToolMessage(
                    content=m.content or "",
                    tool_call_id=m.tool_call_id or "",
                    name=m.name or "",
                )
            )
    return out


def langchain_to_response(msg: Any) -> AgentResponse:
    """Map LangChain AIMessage → AgentResponse with tool_calls and usage."""
    content = msg.content if isinstance(msg.content, str) else None

    tool_calls_out: list[ToolCall] | None = None
    raw = getattr(msg, "tool_calls", None) or []
    if raw:
        tool_calls_out = []
        for tc in raw:
            if isinstance(tc, dict):
                name = tc.get("name", "")
                tid = tc.get("id", "")
                args = tc.get("args", {})
            else:
                name = getattr(tc, "name", "") or ""
                tid = getattr(tc, "id", "") or ""
                args = getattr(tc, "args", {}) or {}
            tool_calls_out.append(
                ToolCall(
                    id=tid or "call_unknown",
                    function=ToolFn(
                        name=name,
                        arguments=json.dumps(args)
                        if isinstance(args, dict)
                        else str(args),
                    ),
                )
            )

    usage_out: TokenUsage | None = None
    meta = getattr(msg, "response_metadata", {}) or {}
    token_usage = meta.get("token_usage") or {}
    if token_usage:
        usage_out = TokenUsage(
            prompt_tokens=token_usage.get("prompt_tokens"),
            completion_tokens=token_usage.get("completion_tokens"),
            total_tokens=token_usage.get("total_tokens"),
        )
    else:
        usage_meta = getattr(msg, "usage_metadata", None)
        if usage_meta:
            usage_out = TokenUsage(
                prompt_tokens=getattr(usage_meta, "input_tokens", None),
                completion_tokens=getattr(usage_meta, "output_tokens", None),
                total_tokens=getattr(usage_meta, "total_tokens", None),
            )

    return AgentResponse(content=content, tool_calls=tool_calls_out, usage=usage_out)


@app.post("/agent/respond", response_model=AgentResponse)
async def respond(body: AgentRequest) -> AgentResponse:
    from langchain_openai import ChatOpenAI

    lc_messages = platform_to_langchain(body.messages)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    ai_msg = await llm.ainvoke(lc_messages)
    return langchain_to_response(ai_msg)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("langchain_agent:app", host="0.0.0.0", port=8003, reload=True)
