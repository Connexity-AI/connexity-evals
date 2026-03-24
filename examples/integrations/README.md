# Agent integration examples

Runnable adapters that match the [agent HTTP contract](../../docs/agent-contract.md). Both call real LLMs and return actual token usage.

## `raw_python_agent.py`

Uses the OpenAI Python SDK directly. Sends the incoming messages to `gpt-4o-mini` and maps the completion response (including token usage) back to `AgentResponse`.

```bash
cd examples/integrations
pip install fastapi uvicorn pydantic openai
export OPENAI_API_KEY=sk-...
uvicorn raw_python_agent:app --reload --port 8002
```

## `langchain_agent.py`

Converts platform messages to LangChain `BaseMessage` types, invokes `ChatOpenAI`, then maps the `AIMessage` back to `AgentResponse` — including `tool_calls` and `usage` extracted from `response_metadata`.

```bash
cd examples/integrations
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
uvicorn langchain_agent:app --reload --port 8003
```

Swap `ChatOpenAI` for another LangChain chat model that supports tool calling if you use a different provider.

## Contract reference

See [docs/agent-contract.md](../../docs/agent-contract.md) and the [mock agent](../mock_agent/) OpenAPI at `/docs`.
