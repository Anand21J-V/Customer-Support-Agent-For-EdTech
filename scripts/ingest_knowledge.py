"""Ingest the policy DOCX into Qdrant and the BM25 manifest."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings
from app.retrieval.bm25_index import build_corpus_records, save_corpus_manifest
from app.retrieval.chunking import chunk_policies
from app.retrieval.docx_parser import parse_policy_docx, validate_policies
from app.retrieval.embeddings import embed_texts
from app.retrieval.qdrant_client import collection_point_count, ensure_collection, upsert_chunks


def main() -> None:
    settings = get_settings()
    docx_path = Path(settings.knowledge_docx_path)
    if not docx_path.exists():
        raise FileNotFoundError(f"Knowledge base DOCX not found: {docx_path}")

    policies = parse_policy_docx(docx_path)
    validate_policies(policies)
    chunks = chunk_policies(policies)

    ensure_collection(settings)
    vectors = embed_texts([chunk.text for chunk in chunks], settings)
    upsert_chunks(chunks, vectors, settings)

    records = build_corpus_records(chunks)
    save_corpus_manifest(records, settings.bm25_cache_path)

    manifest = {
        "ingested_at": datetime.now(UTC).isoformat(),
        "embedding_model": settings.embedding_model,
        "embedding_dimension": settings.embedding_dimension,
        "policy_count": len(policies),
        "chunk_count": len(chunks),
        "collection": settings.qdrant_collection,
        "policy_ids": sorted({policy.policy_id for policy in policies}),
        "qdrant_points": collection_point_count(settings),
    }
    manifest_path = Path(settings.ingest_manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        f"Ingest complete: policies={len(policies)}, chunks={len(chunks)}, "
        f"collection={settings.qdrant_collection}, points={manifest['qdrant_points']}"
    )


if __name__ == "__main__":
    main()
