"""Unit tests for BM25 keyword search."""

from pathlib import Path

from app.config import get_settings
from app.retrieval.bm25_index import BM25Index, build_corpus_records
from app.retrieval.chunking import chunk_policies
from app.retrieval.docx_parser import parse_policy_docx

DOCX_PATH = Path(get_settings().knowledge_docx_path)


def test_bm25_finds_refund_policy() -> None:
    policies = parse_policy_docx(DOCX_PATH)
    chunks = chunk_policies(policies)
    index = BM25Index(build_corpus_records(chunks))

    hits = index.search("refund policy eligibility", top_k=5)
    assert hits
    assert any(hit["policy_id"] == "POL-REFUND-001" for hit in hits)
