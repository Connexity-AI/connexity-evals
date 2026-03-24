# Agent HTTP contract

Eval agents expose a single HTTP endpoint that accepts an OpenAI-style chat history and returns an assistant message, optionally with tool calls and usage metadata. This is **not** a custom protocol: it matches common OpenAI-compatible chat patterns so frameworks can adapt with thin wrappers.

Canonical Pydantic models live in the backend at `app.models.agent_contract` (`AgentRequest`, `AgentResponse`, `ChatMessage`, `TokenUsage`, …) and reuse `ToolCall` / `ToolCallFunction` from `app.models.schemas` for tool-call shape.

## Endpoint

| | |
|---|---|
| **Method / path** | `POST /agent/respond` |
| **Content-Type** | `application/json` |
| **Auth** | Your deployment (API key, mTLS, etc.) — not defined by this contract |

The platform stores the full URL on the `Agent` record (e.g. `https://your-host/agent/respond`). The path segment `/agent/respond` is the recommended convention used by the reference [mock agent](../examples/mock_agent/).

## Request body (`AgentRequest`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `messages` | `array` | yes | Ordered chat messages (OpenAI roles). |
| `metadata` | `object` | no | Platform context for logging / evaluation. |

### `messages[]` (`ChatMessage`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | string | yes | One of `system`, `user`, `assistant`, `tool`. |
| `content` | string \| null | no | Text body; may be omitted when `tool_calls` is present on `assistant`. |
| `tool_calls` | array | no | On `assistant`, OpenAI-style tool calls (see below). |
| `tool_call_id` | string \| null | no | On `tool`, id of the call this message answers. |
| `name` | string \| null | no | On `tool`, optional function name (OpenAI convention). |

### `metadata` (`AgentRequestMetadata`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scenario_id` | string \| null | no | Scenario identifier from the eval platform. |
| `turn_index` | integer \| null | no | Zero-based turn index in the scenario. |

### Tool call object (`ToolCall`)

Same shape as OpenAI chat completions, plus an optional platform field on **stored transcripts** (not required on the wire from the agent):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique id (e.g. `call_abc123`). |
| `type` | string | yes | Must be `function`. |
| `function` | object | yes | `name` (string), `arguments` (JSON **string**). |
| `tool_result` | any | no | Filled by the platform when persisting transcript turns after tool execution. |

## Response body (`AgentResponse`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | string | yes | Always `assistant` for this contract. |
| `content` | string \| null | no | Assistant text; may be null if only `tool_calls` are returned. |
| `tool_calls` | array \| null | no | OpenAI-shaped tool calls (same as in `messages`). |
| `usage` | object \| null | no | Token usage for cost tracking. |

### `usage` (`TokenUsage`)

All fields optional; include whatever your stack reports.

| Field | Type | Description |
|-------|------|-------------|
| `prompt_tokens` | integer | Tokens in the prompt. |
| `completion_tokens` | integer | Tokens in the completion. |
| `total_tokens` | integer | Total if available. |

## Tool results in the next request

After the assistant returns `tool_calls`, the platform executes tools (or simulates them), then sends **tool** role messages back with:

- `role`: `tool`
- `content`: string (often JSON) with the tool output
- `tool_call_id`: same `id` as in the assistant’s `tool_calls` entry
- `name`: optional, matching `function.name`

The next `POST /agent/respond` includes the full `messages` array including those `tool` messages, so the agent can continue the conversation.

## Example payloads

### 1. Simple text reply

**Request**

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hi, I'd like to book a duct cleaning."
    }
  ],
  "metadata": {
    "scenario_id": "residential_duct_cleaning_happy_path",
    "turn_index": 0
  }
}
```

**Response**

```json
{
  "role": "assistant",
  "content": "I can help with that. What is your postal code?"
}
```

### 2. Response with tool call

**Request**

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hi, I'd like to book a duct cleaning."
    },
    {
      "role": "assistant",
      "content": "Sure! Can I get your postal code?"
    },
    {
      "role": "user",
      "content": "V4T 0A7"
    }
  ],
  "metadata": {
    "scenario_id": "residential_duct_cleaning_happy_path",
    "turn_index": 2
  }
}
```

**Response**

```json
{
  "role": "assistant",
  "content": "Let me check if we service your area.",
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "check_service_area",
        "arguments": "{\"zone\": \"V4T0A7\"}"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 245,
    "completion_tokens": 38
  }
}
```

### 3. Refusal / error-style response (HTTP 200)

Agents should still return valid JSON with `role: assistant` when they refuse or explain an error, unless you use HTTP error codes intentionally.

**Response**

```json
{
  "role": "assistant",
  "content": "I can't help with that request. I can only assist with duct cleaning bookings and service area questions."
}
```

For hard transport failures (timeout, 5xx), the platform run records an appropriate error category.

## OpenAPI (machine-readable)

- **Reference implementation:** run the mock agent (`examples/mock_agent/`) and open its `/docs` — FastAPI generates OpenAPI from the same request/response shapes.
- **Backend models:** `AgentRequest` / `AgentResponse` are part of the Python package for the runner and tests; the main Connexity API OpenAPI documents scenario/run resources that *reference* transcript types (`ConversationTurn`, `ToolCall`).

## Examples in this repo

| Path | Purpose |
|------|---------|
| [examples/mock_agent/](../examples/mock_agent/) | Tiny FastAPI agent for local testing and onboarding. |
| [examples/integrations/raw_python_agent.py](../examples/integrations/raw_python_agent.py) | Wrap a plain Python function. |
| [examples/integrations/langchain_agent.py](../examples/integrations/langchain_agent.py) | Adapt LangChain message types and tool calls. |

## What this is not

- Not a separate proprietary protocol — OpenAI-compatible messages and tool calls.
- Not an SDK — HTTP + JSON only.
- Not tied to a single framework — any stack that can parse and emit JSON can implement `POST /agent/respond`.
