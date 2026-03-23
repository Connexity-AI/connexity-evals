import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, field_validator
from sqlalchemy import Column, Index, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import Difficulty, ScenarioStatus
from app.models.schemas import ExpectedToolCall, Persona

if TYPE_CHECKING:
    from app.models.scenario_result import ScenarioResult
    from app.models.scenario_set import ScenarioSetMember


def _validate_persona(v: Any) -> dict[str, Any] | None:
    if v is None:
        return None
    if isinstance(v, BaseModel):
        return v.model_dump()
    if isinstance(v, dict):
        return Persona.model_validate(v).model_dump()
    raise ValueError("persona must be a Persona object or dict")


def _validate_expected_tool_calls(v: Any) -> list[dict[str, Any]] | None:
    if v is None:
        return None
    if isinstance(v, list):
        return [
            item.model_dump()
            if isinstance(item, BaseModel)
            else ExpectedToolCall.model_validate(item).model_dump()
            for item in v
        ]
    raise ValueError("expected_tool_calls must be a list")


class ScenarioBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None)
    difficulty: Difficulty = Field(default=Difficulty.NORMAL, index=True)
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(Text), nullable=False, server_default="{}"),
    )
    status: ScenarioStatus = Field(default=ScenarioStatus.ACTIVE, index=True)
    persona: dict[str, Any] | None = Field(
        default=None, sa_column=Column("persona", JSONB, nullable=True)
    )
    initial_message: str | None = Field(default=None)
    user_context: dict[str, Any] | None = Field(
        default=None, sa_column=Column("user_context", JSONB, nullable=True)
    )
    max_turns: int | None = Field(default=None)
    expected_outcomes: dict[str, Any] | None = Field(
        default=None, sa_column=Column("expected_outcomes", JSONB, nullable=True)
    )
    expected_tool_calls: list[dict[str, Any]] | None = Field(
        default=None,
        sa_column=Column("expected_tool_calls", JSONB, nullable=True),
    )
    evaluation_criteria_override: str | None = Field(default=None)

    @field_validator("persona", mode="before")
    @classmethod
    def _serialize_persona(cls, v: Any) -> dict[str, Any] | None:
        return _validate_persona(v)

    @field_validator("expected_tool_calls", mode="before")
    @classmethod
    def _serialize_expected_tool_calls(cls, v: Any) -> list[dict[str, Any]] | None:
        return _validate_expected_tool_calls(v)


class Scenario(ScenarioBase, table=True):
    __tablename__ = "scenario"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={"server_default": text("now()")},
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={"server_default": text("now()"), "onupdate": datetime.now},
    )

    # Relationships
    scenario_set_links: list["ScenarioSetMember"] = Relationship(
        back_populates="scenario"
    )
    scenario_results: list["ScenarioResult"] = Relationship(back_populates="scenario")

    __table_args__ = (Index("ix_scenario_tags_gin", "tags", postgresql_using="gin"),)


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    difficulty: Difficulty | None = None
    tags: list[str] | None = None
    status: ScenarioStatus | None = None
    persona: dict[str, Any] | None = None
    initial_message: str | None = None
    user_context: dict[str, Any] | None = None
    max_turns: int | None = None
    expected_outcomes: dict[str, Any] | None = None
    expected_tool_calls: list[dict[str, Any]] | None = None
    evaluation_criteria_override: str | None = None

    @field_validator("persona", mode="before")
    @classmethod
    def _serialize_persona(cls, v: Any) -> dict[str, Any] | None:
        return _validate_persona(v)

    @field_validator("expected_tool_calls", mode="before")
    @classmethod
    def _serialize_expected_tool_calls(cls, v: Any) -> list[dict[str, Any]] | None:
        return _validate_expected_tool_calls(v)


class ScenarioPublic(ScenarioBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ScenariosPublic(SQLModel):
    data: list[ScenarioPublic]
    count: int
