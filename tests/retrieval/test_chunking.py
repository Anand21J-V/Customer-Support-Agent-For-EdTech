"""Unit tests for policy chunking."""

from pathlib import Path

import pytest

from app.config import get_settings
from app.retrieval.chunking import chunk_policies
from app.retrieval.docx_parser import parse_policy_docx

DOCX_PATH = Path(get_settings().knowledge_docx_path)


@pytest.fixture(scope="module")
def chunks():
    if not DOCX_PATH.exists():
        pytest.fail(f"Knowledge base DOCX not found: {DOCX_PATH}")
    policies = parse_policy_docx(DOCX_PATH)
    return chunk_policies(policies)


def test_chunk_count_reasonable(chunks) -> None:
    assert 80 <= len(chunks) <= 140


def test_refund_chunks_have_expected_ids(chunks) -> None:
    refund_chunks = [chunk for chunk in chunks if chunk.policy_id == "POL-REFUND-001"]
    assert refund_chunks
    assert any(chunk.section == "core_rules" for chunk in refund_chunks)


def test_chunk_payload_fields(chunks) -> None:
    sample = chunks[0]
    assert sample.chunk_id
    assert sample.policy_id
    assert sample.intent
    assert sample.audience == "student"
    assert sample.status == "active"
    assert sample.text
