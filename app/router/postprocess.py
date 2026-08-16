"""Post-processing helpers for router model output."""

from __future__ import annotations

from app.router.intents import get_intent_config
from app.schemas.router import RouterDecision, RouterModelOutput
from app.schemas.router_types import StudentIntent


def apply_unknown_defaults() -> RouterModelOutput:
    config = get_intent_config("unknown")
    return RouterModelOutput(
        intent="unknown",
        sub_intent="needs_clarification",
        route=config.route,
        requires_rag=config.requires_rag,
        requires_tool=config.requires_tool,
        requires_planning=config.requires_planning,
        escalation_candidate=config.escalation_candidate,
        confidence=0.0,
    )


def normalize_router_output(
    model_output: RouterModelOutput,
    *,
    confidence_threshold: float,
) -> tuple[RouterModelOutput, StudentIntent | None, bool]:
    """Apply confidence and unknown rules to raw model output."""
    raw_intent: StudentIntent | None = None
    is_unknown = False
    output = model_output

    if model_output.intent == "unknown":
        is_unknown = True
    elif model_output.confidence < confidence_threshold:
        raw_intent = model_output.intent
        is_unknown = True
        unknown_config = get_intent_config("unknown")
        output = RouterModelOutput(
            intent="unknown",
            sub_intent="needs_clarification",
            route=unknown_config.route,
            requires_rag=unknown_config.requires_rag,
            requires_tool=unknown_config.requires_tool,
            requires_planning=unknown_config.requires_planning,
            escalation_candidate=unknown_config.escalation_candidate,
            confidence=model_output.confidence,
        )

    if is_unknown and output.intent == "unknown":
        unknown_config = get_intent_config("unknown")
        output = RouterModelOutput(
            intent="unknown",
            sub_intent=output.sub_intent,
            route=unknown_config.route,
            requires_rag=unknown_config.requires_rag,
            requires_tool=unknown_config.requires_tool,
            requires_planning=unknown_config.requires_planning,
            escalation_candidate=unknown_config.escalation_candidate,
            confidence=output.confidence,
        )

    return output, raw_intent, is_unknown


def align_with_registry(model_output: RouterModelOutput) -> RouterModelOutput:
    """Normalize route flags using the intent registry defaults."""
    config = get_intent_config(model_output.intent)
    requires_tool = model_output.requires_tool or config.requires_tool
    requires_planning = model_output.requires_planning or config.requires_planning
    requires_rag = model_output.requires_rag or config.requires_rag
    escalation_candidate = (
        model_output.escalation_candidate or config.escalation_candidate
    )

    return RouterModelOutput(
        intent=model_output.intent,
        sub_intent=model_output.sub_intent,
        route=config.route,
        requires_rag=requires_rag,
        requires_tool=requires_tool,
        requires_planning=requires_planning,
        escalation_candidate=escalation_candidate,
        confidence=model_output.confidence,
    )


def model_output_to_decision(
    model_output: RouterModelOutput,
    *,
    is_unknown: bool,
    raw_intent: StudentIntent | None,
    model: str,
    latency_ms: int,
    prompt_tokens: int | None,
    output_tokens: int | None,
) -> RouterDecision:
    return RouterDecision(
        intent=model_output.intent,
        sub_intent=model_output.sub_intent,
        route=model_output.route,
        requires_rag=model_output.requires_rag,
        requires_tool=model_output.requires_tool,
        requires_planning=model_output.requires_planning,
        escalation_candidate=model_output.escalation_candidate,
        confidence=model_output.confidence,
        is_unknown=is_unknown,
        raw_intent=raw_intent,
        model=model,
        latency_ms=latency_ms,
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
    )


def fallback_decision(
    *,
    model: str = "",
    latency_ms: int = 0,
    prompt_tokens: int | None = None,
    output_tokens: int | None = None,
) -> RouterDecision:
    """Safe fallback when classification fails."""
    unknown_config = get_intent_config("unknown")
    return RouterDecision(
        intent="unknown",
        sub_intent="classification_failed",
        route=unknown_config.route,
        requires_rag=unknown_config.requires_rag,
        requires_tool=unknown_config.requires_tool,
        requires_planning=unknown_config.requires_planning,
        escalation_candidate=unknown_config.escalation_candidate,
        confidence=0.0,
        is_unknown=True,
        raw_intent=None,
        model=model,
        latency_ms=latency_ms,
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
    )
