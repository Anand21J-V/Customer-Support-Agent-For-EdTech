"""Integration tests for hybrid retrieval."""

import pytest
from qdrant_client import QdrantClient

from app.config import get_settings
from app.retrieval.hybrid import hybrid_search
from app.retrieval.qdrant_client import collection_point_count


def _require_qdrant() -> None:
    settings = get_settings()
    try:
        client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        client.get_collections()
    except Exception as exc:  # noqa: BLE001
        pytest.fail(
            "Could not connect to Qdrant. Start it with `docker compose up qdrant -d`. "
            f"Details: {exc}"
        )

    if collection_point_count(settings) == 0:
        pytest.fail(
            "Qdrant collection is empty. Run `python scripts/ingest_knowledge.py` first."
        )


@pytest.fixture(scope="module", autouse=True)
def qdrant_ready() -> None:
    _require_qdrant()


def test_refund_query_returns_refund_policy() -> None:
    results = hybrid_search("Can I get my money back after cancelling?")
    assert results
    assert any(result.policy_id == "POL-REFUND-001" for result in results)
    refund_results = [result for result in results if result.policy_id == "POL-REFUND-001"]
    assert all(result.intent == "refund" for result in refund_results)


def test_enrollment_query_returns_enrollment_policy() -> None:
    results = hybrid_search("How do I enroll in a course?")
    assert any(result.policy_id == "POL-ENROLLMENT-001" for result in results)


def test_results_are_active_student_policies() -> None:
    results = hybrid_search("How can I request a refund?")
    assert results
    assert all(result.audience == "student" for result in results)
    assert all(result.status == "active" for result in results)
