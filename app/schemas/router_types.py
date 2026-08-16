"""Shared router type definitions."""

from typing import Literal

StudentIntent = Literal[
    "course_access",
    "enrollment",
    "payment",
    "refund",
    "certificate",
    "assignment",
    "exam",
    "technical_issue",
    "account",
    "course_information",
    "schedule",
    "tutor_support",
    "progress",
    "attendance",
    "subscription",
    "academic_question",
    "course_content",
    "feedback_complaint",
    "human_support",
    "unknown",
]

RouteTarget = Literal["knowledge", "operations", "learning", "escalation"]

STUDENT_INTENTS: tuple[StudentIntent, ...] = (
    "course_access",
    "enrollment",
    "payment",
    "refund",
    "certificate",
    "assignment",
    "exam",
    "technical_issue",
    "account",
    "course_information",
    "schedule",
    "tutor_support",
    "progress",
    "attendance",
    "subscription",
    "academic_question",
    "course_content",
    "feedback_complaint",
    "human_support",
    "unknown",
)
