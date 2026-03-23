from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.scenario import ScenarioPublic


class ToolDefinition(BaseModel):
    """A single tool/function definition the agent has access to."""

    name: str
    description: str
    parameters: dict[str, Any] | None = None


class GenerateRequest(BaseModel):
    """Input for scenario generation."""

    model_config = ConfigDict(protected_namespaces=())

    agent_prompt: str
    tools: list[ToolDefinition] = []
    count: int = Field(default=10, ge=1, le=50)
    focus_tags: list[str] = []
    model: str | None = None
    persist: bool = True


class GenerateResult(BaseModel):
    """Output from scenario generation."""

    model_config = ConfigDict(protected_namespaces=())

    scenarios: list[ScenarioPublic]
    count: int
    model_used: str
    generation_time_ms: int
