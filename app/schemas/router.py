"""Pydantic schemas for intent routing."""

from dataclasses import dataclass

from pydantic import BaseModel, Field, field_validator

from app.schemas.router_types import RouteTarget, StudentIntent


class RouterRequest(BaseModel):
    """Validated router input."""

    query: str
    user_type: str | None = None
    student_id: str | None = None
    conversation_turn: int | None = None

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query must not be empty")
        return value.strip()


class RouterModelOutput(BaseModel):
    """Structured output returned by the LLM router."""

    intent: StudentIntent
    sub_intent: str = Field(min_length=1)
    route: RouteTarget
    requires_rag: bool
    requires_tool: bool
    requires_planning: bool
    escalation_candidate: bool
    confidence: float = Field(ge=0, le=1)


@dataclass(frozen=True)
class RouterDecision:
    """Final routing decision after post-processing."""

    intent: StudentIntent
    sub_intent: str
    route: RouteTarget
    requires_rag: bool
    requires_tool: bool
    requires_planning: bool
    escalation_candidate: bool
    confidence: float
    is_unknown: bool
    raw_intent: StudentIntent | None
    model: str
    latency_ms: int
    prompt_tokens: int | None
    output_tokens: int | None
