"""Convert parsed policies into embeddable knowledge chunks."""

from __future__ import annotations

from app.schemas.knowledge import KnowledgeChunk, PolicyDocument

EXPECTED_INTENTS = {
    "academic_question",
    "account",
    "assignment",
    "attendance",
    "certificate",
    "course_access",
    "course_content",
    "course_information",
    "enrollment",
    "exam",
    "feedback_complaint",
    "human_support",
    "payment",
    "progress",
    "refund",
    "schedule",
    "subscription",
    "technical_issue",
    "tutor_support",
    "unknown",
}


def _format_chunk_text(policy: PolicyDocument, section: str, body: str) -> str:
    return (
        f"Policy: {policy.policy_id}\n"
        f"Intent: {policy.intent}\n"
        f"Category: {policy.category}\n"
        f"Section: {section}\n"
        f"Content: {body}"
    )


def chunk_policy(policy: PolicyDocument) -> list[KnowledgeChunk]:
    """Create semantic chunks for one policy document."""
    chunks: list[KnowledgeChunk] = []

    def add_chunk(section: str, seq: int, body: str) -> None:
        if not body.strip():
            return
        chunks.append(
            KnowledgeChunk(
                chunk_id=f"{policy.policy_id}::{section}::{seq:03d}",
                policy_id=policy.policy_id,
                intent=policy.intent,
                category=policy.category,
                audience=policy.audience,
                route=policy.route,
                status=policy.status,
                version=policy.version,
                section=section,
                text=_format_chunk_text(policy, section, body.strip()),
                keywords=policy.keywords,
            )
        )

    add_chunk("purpose", 1, policy.purpose)

    if policy.core_rules:
        rules_text = "\n".join(f"- {rule}" for rule in policy.core_rules)
        add_chunk("core_rules", 1, rules_text)

    if policy.agent_behavior:
        behavior_text = "\n".join(f"- {line}" for line in policy.agent_behavior)
        add_chunk("agent_behavior", 1, behavior_text)

    if policy.grounding_scenarios:
        scenario_text = "\n".join(f"- {line}" for line in policy.grounding_scenarios)
        add_chunk("grounding_scenarios", 1, scenario_text)

    if policy.keywords:
        add_chunk("keywords", 1, ", ".join(policy.keywords))

    return chunks


def chunk_policies(policies: list[PolicyDocument]) -> list[KnowledgeChunk]:
    """Chunk all policies and validate intent coverage."""
    found_intents = {policy.intent for policy in policies}
    missing = EXPECTED_INTENTS - found_intents
    if missing:
        raise ValueError(f"Missing intents in knowledge base: {sorted(missing)}")

    all_chunks: list[KnowledgeChunk] = []
    for policy in policies:
        all_chunks.extend(chunk_policy(policy))

    if not all_chunks:
        raise ValueError("No knowledge chunks were produced")

    for chunk in all_chunks:
        if not chunk.policy_id or not chunk.intent:
            raise ValueError(f"Chunk missing policy_id or intent: {chunk.chunk_id}")

    return all_chunks
