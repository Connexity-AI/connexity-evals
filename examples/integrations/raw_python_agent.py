from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from openai import AsyncOpenAI
from pydantic import BaseModel

app = FastAPI(title="Raw Python agent (OpenAI SDK)", version="0.1.0")
client = AsyncOpenAI()


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
    metadata: dict[str, object] | None = None


class TokenUsage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class AgentResponse(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    usage: TokenUsage | None = None


@app.post("/agent/respond", response_model=AgentResponse)
async def respond(request: AgentRequest) -> AgentResponse:
    openai_messages = [m.model_dump(exclude_none=True) for m in request.messages]

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=openai_messages,
        temperature=0,
    )
    choice = completion.choices[0].message

    tool_calls_out: list[ToolCall] | None = None
    if choice.tool_calls:
        tool_calls_out = [
            ToolCall(
                id=tc.id,
                function=ToolFn(name=tc.function.name, arguments=tc.function.arguments),
            )
            for tc in choice.tool_calls
        ]

    usage_out: TokenUsage | None = None
    if completion.usage:
        usage_out = TokenUsage(
            prompt_tokens=completion.usage.prompt_tokens,
            completion_tokens=completion.usage.completion_tokens,
            total_tokens=completion.usage.total_tokens,
        )

    return AgentResponse(
        content=choice.content,
        tool_calls=tool_calls_out,
        usage=usage_out,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("raw_python_agent:app", host="0.0.0.0", port=8002, reload=True)
