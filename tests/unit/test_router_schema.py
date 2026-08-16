"""Unit tests for router schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.router import RouterModelOutput, RouterRequest


def test_router_request_rejects_blank_query() -> None:
    with pytest.raises(ValidationError):
        RouterRequest(query="   ")


def test_router_request_strips_query() -> None:
    request = RouterRequest(query="  hello  ")
    assert request.query == "hello"


def test_router_model_output_validates_confidence_bounds() -> None:
    with pytest.raises(ValidationError):
        RouterModelOutput(
            intent="refund",
            sub_intent="refund_eligibility",
            route="knowledge",
            requires_rag=True,
            requires_tool=False,
            requires_planning=False,
            escalation_candidate=False,
            confidence=1.5,
        )


def test_router_model_output_accepts_valid_payload() -> None:
    output = RouterModelOutput(
        intent="payment",
        sub_intent="payment_failed",
        route="operations",
        requires_rag=False,
        requires_tool=True,
        requires_planning=False,
        escalation_candidate=False,
        confidence=0.91,
    )
    assert output.intent == "payment"
