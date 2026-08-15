"""Unit tests for DOCX policy parsing."""

from pathlib import Path

import pytest

from app.config import get_settings
from app.retrieval.docx_parser import parse_policy_docx, validate_policies

DOCX_PATH = Path(get_settings().knowledge_docx_path)


@pytest.fixture(scope="module")
def policies():
    if not DOCX_PATH.exists():
        pytest.fail(f"Knowledge base DOCX not found: {DOCX_PATH}")
    parsed = parse_policy_docx(DOCX_PATH)
    validate_policies(parsed)
    return parsed


def test_parse_twenty_policies(policies) -> None:
    assert len(policies) == 20


def test_refund_policy_metadata(policies) -> None:
    refund = next(policy for policy in policies if policy.intent == "refund")
    assert refund.policy_id == "POL-REFUND-001"
    assert refund.category == "Payments"
    assert refund.audience == "student"
    assert "Refund eligibility" in refund.purpose


def test_all_policy_ids_unique(policies) -> None:
    policy_ids = [policy.policy_id for policy in policies]
    assert len(policy_ids) == len(set(policy_ids))
