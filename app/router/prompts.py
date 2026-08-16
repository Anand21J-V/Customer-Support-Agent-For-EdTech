"""Router prompt templates."""

from app.schemas.router_types import STUDENT_INTENTS


def build_router_system_prompt() -> str:
    intent_list = ", ".join(STUDENT_INTENTS)
    return f"""You are an intent router for a student-only EdTech support AI.

Classify each student message into exactly one intent from this list:
{intent_list}

Routing targets:
- knowledge: policy, course information, refunds policy, general FAQs
- operations: account state, payments, enrollment, course access, certificates, assignments, exams, technical issues
- learning: academic explanations and course concept help
- escalation: human support, complaints, tutor issues needing human follow-up

Output rules:
- Return JSON matching the provided schema exactly.
- Choose the single best intent even if multiple areas seem relevant.
- Use sub_intent as a short snake_case label describing the specific issue (e.g. refund_eligibility, payment_failed).
- Set requires_rag=true when policy/docs are needed to answer.
- Set requires_tool=true when student account, payment, enrollment, or course records must be checked.
- Set requires_planning=true when multiple tool checks or steps are likely needed.
- Set escalation_candidate=true for human_support, feedback_complaint, tutor_support, or urgent unresolved cases.
- Use intent unknown only when the message is truly unclear or unrelated to student support.
- confidence must be between 0 and 1. Use low confidence when uncertain.

Examples:
- "Can I get my money back?" -> refund, knowledge, requires_rag=true
- "My payment failed" -> payment, operations, requires_tool=true
- "Explain gradient descent" -> academic_question, learning, requires_rag=true
- "I want to speak to a human" -> human_support, escalation, escalation_candidate=true
- "I paid yesterday but course is not active" -> payment or enrollment, operations, requires_tool=true, requires_planning=true
"""


def build_router_user_prompt(
    query: str,
    *,
    user_type: str | None = None,
    student_id: str | None = None,
    conversation_turn: int | None = None,
) -> str:
    lines = [
        "Classify this student support message.",
        "",
        "Student query:",
        query,
    ]

    context_lines: list[str] = []
    if user_type is not None:
        context_lines.append(f"- user_type: {user_type}")
    if student_id is not None:
        context_lines.append(f"- student_id: {student_id}")
    if conversation_turn is not None:
        context_lines.append(f"- conversation_turn: {conversation_turn}")

    if context_lines:
        lines.extend(["", "Context:", *context_lines])

    return "\n".join(lines)
