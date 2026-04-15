"""Prompt editor preset suggestions (CS-63) — static presets with contextual filtering."""

from enum import StrEnum

from pydantic import BaseModel
from sqlmodel import Session, select

from app.models import Agent, Run
from app.models.enums import RunStatus


class PresetContext(StrEnum):
    """What context the chat endpoint should load when this preset is sent."""

    NONE = "none"
    EVAL = "eval"


class PresetRequirements(BaseModel):
    """Agent state gates; ``None`` means the requirement is not checked."""

    has_prompt: bool | None = None
    has_tools: bool | None = None
    has_completed_runs: bool | None = None


class Preset(BaseModel):
    id: str
    label: str
    message: str
    description: str | None = None
    context: PresetContext = PresetContext.NONE
    requires: PresetRequirements


ALL_PRESETS: list[Preset] = [
    Preset(
        id="help_create_agent",
        label="Help me create an agent",
        message=(
            "I need help creating a system prompt for this agent. Ask me about "
            "its purpose, target audience, and desired behavior so you can "
            "draft an effective prompt."
        ),
        description="Start from scratch with guided prompt creation",
        requires=PresetRequirements(has_prompt=False),
    ),
    Preset(
        id="improve_prompt",
        label="Improve my prompt",
        message=(
            "Review my current prompt and suggest improvements. Focus on "
            "clarity, structure, and effectiveness."
        ),
        description="Get suggestions to enhance your existing prompt",
        requires=PresetRequirements(has_prompt=True),
    ),
    Preset(
        id="make_concise",
        label="Make my prompt more concise",
        message=(
            "My prompt feels too verbose. Trim unnecessary repetition and "
            "tighten the instructions while preserving all key behaviors."
        ),
        description="Reduce verbosity while keeping key behaviors",
        requires=PresetRequirements(has_prompt=True),
    ),
    Preset(
        id="add_examples",
        label="Add examples",
        message=(
            "Add concrete input/output examples to my prompt that demonstrate "
            "the expected behavior. Pick scenarios that cover common and edge cases."
        ),
        description="Add input/output examples for clearer behavior",
        requires=PresetRequirements(has_prompt=True),
    ),
    Preset(
        id="suggest_from_evals",
        label="Suggest improvements from eval results",
        message=(
            "Analyze the eval results for this agent and suggest targeted prompt "
            "improvements to address failing test cases and low-scoring metrics."
        ),
        description="Data-driven suggestions based on eval performance",
        context=PresetContext.EVAL,
        requires=PresetRequirements(has_prompt=True, has_completed_runs=True),
    ),
    Preset(
        id="review_tools",
        label="Review my tool definitions",
        message=(
            "Review my agent's tool definitions and suggest improvements to "
            "their names, descriptions, and parameter schemas. Also check if the "
            "prompt gives adequate guidance on when and how to use each tool."
        ),
        description="Optimize tool names, descriptions, and usage guidance",
        requires=PresetRequirements(has_prompt=True, has_tools=True),
    ),
]


def _agent_has_prompt(agent: Agent) -> bool:
    return bool(agent.system_prompt and str(agent.system_prompt).strip())


def _agent_has_tools(agent: Agent) -> bool:
    return bool(agent.tools and len(agent.tools) > 0)


def _agent_has_completed_runs(*, session: Session, agent: Agent) -> bool:
    row = session.exec(
        select(Run.id)
        .where(Run.agent_id == agent.id, Run.status == RunStatus.COMPLETED)
        .limit(1)
    ).first()
    return row is not None


def _preset_available(
    preset: Preset,
    *,
    has_prompt: bool,
    has_tools: bool,
    has_completed_runs: bool,
) -> bool:
    req = preset.requires
    if req.has_prompt is not None and req.has_prompt != has_prompt:
        return False
    if req.has_tools is not None and req.has_tools != has_tools:
        return False
    if (
        req.has_completed_runs is not None
        and req.has_completed_runs != has_completed_runs
    ):
        return False
    return True


def get_available_presets(*, agent: Agent, session: Session) -> list[Preset]:
    """Return presets whose requirements match the agent's current state."""
    has_prompt = _agent_has_prompt(agent)
    has_tools = _agent_has_tools(agent)
    has_completed_runs = _agent_has_completed_runs(session=session, agent=agent)
    return [
        p
        for p in ALL_PRESETS
        if _preset_available(
            p,
            has_prompt=has_prompt,
            has_tools=has_tools,
            has_completed_runs=has_completed_runs,
        )
    ]
