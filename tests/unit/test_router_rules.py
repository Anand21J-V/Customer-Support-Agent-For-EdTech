"""Unit tests for router post-processing rules."""

from unittest.mock import MagicMock, patch

import pytest

from app.router.exceptions import RouterValidationError
from app.router.postprocess import align_with_registry, fallback_decision, normalize_router_output
from app.router.router import classify_query
from app.schemas.router import RouterModelOutput


def test_low_confidence_forces_unknown() -> None:
    model_output = RouterModelOutput(
        intent="payment",
        sub_intent="payment_failed",
        route="operations",
        requires_rag=False,
        requires_tool=True,
        requires_planning=False,
        escalation_candidate=False,
        confidence=0.55,
    )

    normalized, raw_intent, is_unknown = normalize_router_output(
        model_output,
        confidence_threshold=0.70,
    )

    assert is_unknown is True
    assert normalized.intent == "unknown"
    assert raw_intent == "payment"


def test_unknown_intent_keeps_unknown_route_defaults() -> None:
    model_output = RouterModelOutput(
        intent="unknown",
        sub_intent="unclear_request",
        route="operations",
        requires_rag=False,
        requires_tool=True,
        requires_planning=False,
        escalation_candidate=False,
        confidence=0.40,
    )

    normalized, _, is_unknown = normalize_router_output(
        model_output,
        confidence_threshold=0.70,
    )

    assert is_unknown is True
    assert normalized.intent == "unknown"
    assert normalized.route == "knowledge"
    assert normalized.requires_rag is True
    assert normalized.requires_tool is False


def test_align_with_registry_sets_primary_route() -> None:
    model_output = RouterModelOutput(
        intent="refund",
        sub_intent="refund_eligibility",
        route="operations",
        requires_rag=False,
        requires_tool=False,
        requires_planning=False,
        escalation_candidate=False,
        confidence=0.92,
    )

    aligned = align_with_registry(model_output)

    assert aligned.route == "knowledge"
    assert aligned.requires_rag is True


def test_fallback_decision_is_safe_unknown() -> None:
    decision = fallback_decision()
    assert decision.intent == "unknown"
    assert decision.is_unknown is True
    assert decision.confidence == 0.0


def test_classify_query_rejects_empty_query() -> None:
    with pytest.raises(RouterValidationError):
        classify_query("   ")


@patch("app.router.router.generate_structured")
def test_classify_query_returns_fallback_on_gemini_error(mock_generate: MagicMock) -> None:
    from app.llm.exceptions import GeminiAPIError

    mock_generate.side_effect = GeminiAPIError("api down")

    decision = classify_query("My payment failed")

    assert decision.intent == "unknown"
    assert decision.sub_intent == "classification_failed"
    assert decision.is_unknown is True


@patch("app.router.router.generate_structured")
def test_classify_query_success(mock_generate: MagicMock) -> None:
    mock_result = MagicMock()
    mock_result.data = RouterModelOutput(
        intent="refund",
        sub_intent="refund_eligibility",
        route="knowledge",
        requires_rag=True,
        requires_tool=False,
        requires_planning=False,
        escalation_candidate=False,
        confidence=0.93,
    )
    mock_result.model = "gemini-test"
    mock_result.latency_ms = 100
    mock_result.prompt_tokens = 10
    mock_result.output_tokens = 20
    mock_generate.return_value = mock_result

    decision = classify_query("Can I get my money back?")

    assert decision.intent == "refund"
    assert decision.route == "knowledge"
    assert decision.is_unknown is False
    assert decision.model == "gemini-test"
