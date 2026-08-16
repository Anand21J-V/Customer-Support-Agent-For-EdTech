"""Intent router entry point."""

from __future__ import annotations

import logging

from pydantic import ValidationError

from app.config import Settings, get_settings
from app.llm.exceptions import GeminiError
from app.llm.gemini_client import generate_structured
from app.router.exceptions import RouterValidationError
from app.router.postprocess import (
    align_with_registry,
    fallback_decision,
    model_output_to_decision,
    normalize_router_output,
)
from app.router.prompts import build_router_system_prompt, build_router_user_prompt
from app.schemas.router import RouterDecision, RouterModelOutput, RouterRequest

logger = logging.getLogger(__name__)


def classify_query(
    query: str,
    *,
    user_type: str | None = None,
    student_id: str | None = None,
    conversation_turn: int | None = None,
    settings: Settings | None = None,
) -> RouterDecision:
    """Classify a student query and return a routing decision."""
    active_settings = settings or get_settings()

    try:
        request = RouterRequest(
            query=query,
            user_type=user_type,
            student_id=student_id,
            conversation_turn=conversation_turn,
        )
    except ValidationError as exc:
        raise RouterValidationError(str(exc)) from exc

    user_prompt = build_router_user_prompt(
        request.query,
        user_type=request.user_type,
        student_id=request.student_id,
        conversation_turn=request.conversation_turn,
    )

    try:
        result = generate_structured(
            user_prompt,
            RouterModelOutput,
            model="fast",
            system_instruction=build_router_system_prompt(),
            settings=active_settings,
        )
    except GeminiError as exc:
        logger.warning("router_classification_failed error=%s", exc)
        return fallback_decision()

    normalized, raw_intent, is_unknown = normalize_router_output(
        result.data,
        confidence_threshold=active_settings.router_confidence_threshold,
    )
    aligned = align_with_registry(normalized)

    return model_output_to_decision(
        aligned,
        is_unknown=is_unknown,
        raw_intent=raw_intent,
        model=result.model,
        latency_ms=result.latency_ms,
        prompt_tokens=result.prompt_tokens,
        output_tokens=result.output_tokens,
    )
