"""Intent taxonomy and routing defaults."""

from __future__ import annotations

from dataclasses import dataclass

from app.schemas.router_types import RouteTarget, StudentIntent

__all__ = [
    "INTENT_REGISTRY",
    "IntentConfig",
    "RouteTarget",
    "STUDENT_INTENTS",
    "StudentIntent",
    "get_intent_config",
]


@dataclass(frozen=True)
class IntentConfig:
    route: RouteTarget
    requires_rag: bool
    requires_tool: bool
    requires_planning: bool
    escalation_candidate: bool


INTENT_REGISTRY: dict[StudentIntent, IntentConfig] = {
    "course_access": IntentConfig("operations", False, True, False, False),
    "enrollment": IntentConfig("operations", False, True, False, False),
    "payment": IntentConfig("operations", False, True, False, False),
    "refund": IntentConfig("knowledge", True, False, False, False),
    "certificate": IntentConfig("operations", False, True, False, False),
    "assignment": IntentConfig("operations", False, True, False, False),
    "exam": IntentConfig("operations", False, True, False, False),
    "technical_issue": IntentConfig("operations", False, True, False, False),
    "account": IntentConfig("operations", False, True, False, False),
    "course_information": IntentConfig("knowledge", True, False, False, False),
    "schedule": IntentConfig("operations", False, True, False, False),
    "tutor_support": IntentConfig("escalation", False, True, False, True),
    "progress": IntentConfig("operations", False, True, False, False),
    "attendance": IntentConfig("operations", False, True, False, False),
    "subscription": IntentConfig("operations", False, True, False, False),
    "academic_question": IntentConfig("learning", True, False, False, False),
    "course_content": IntentConfig("knowledge", True, False, False, False),
    "feedback_complaint": IntentConfig("escalation", False, False, False, True),
    "human_support": IntentConfig("escalation", False, False, False, True),
    "unknown": IntentConfig("knowledge", True, False, False, False),
}


def get_intent_config(intent: StudentIntent) -> IntentConfig:
    return INTENT_REGISTRY[intent]
