"""Hybrid BM25 + vector retrieval."""

from __future__ import annotations

from app.config import Settings, get_settings
from app.retrieval.bm25_index import BM25Index
from app.retrieval.embeddings import embed_query
from app.retrieval.qdrant_client import collection_point_count, vector_search
from app.schemas.knowledge import EvidenceChunk

RRF_K = 60


def _to_evidence(record: dict[str, object], score: float, source: str) -> EvidenceChunk:
    return EvidenceChunk(
        chunk_id=str(record.get("chunk_id", "")),
        policy_id=str(record.get("policy_id", "")),
        intent=str(record.get("intent", "")),
        category=str(record.get("category", "")),
        audience=str(record.get("audience", "")),
        status=str(record.get("status", "")),
        section=str(record.get("section", "")),
        text=str(record.get("text", "")),
        score=score,
        source=source,  # type: ignore[arg-type]
    )


def _reciprocal_rank_fusion(
    bm25_hits: list[dict[str, object]],
    vector_hits: list[dict[str, object]],
) -> list[tuple[dict[str, object], float, str]]:
    fused_scores: dict[str, float] = {}
    records: dict[str, dict[str, object]] = {}
    sources: dict[str, set[str]] = {}

    for rank, hit in enumerate(bm25_hits):
        chunk_id = str(hit.get("chunk_id", ""))
        if not chunk_id:
            continue
        fused_scores[chunk_id] = fused_scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank + 1)
        records[chunk_id] = hit
        sources.setdefault(chunk_id, set()).add("bm25")

    for rank, hit in enumerate(vector_hits):
        chunk_id = str(hit.get("chunk_id", ""))
        if not chunk_id:
            continue
        fused_scores[chunk_id] = fused_scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank + 1)
        records[chunk_id] = hit
        sources.setdefault(chunk_id, set()).add("vector")

    ranked = sorted(fused_scores.items(), key=lambda item: item[1], reverse=True)
    output: list[tuple[dict[str, object], float, str]] = []
    for chunk_id, score in ranked:
        source = "hybrid" if len(sources.get(chunk_id, set())) > 1 else next(iter(sources[chunk_id]))
        output.append((records[chunk_id], score, source))
    return output


def hybrid_search(
    query: str,
    intent: str | None = None,
    settings: Settings | None = None,
) -> list[EvidenceChunk]:
    """Run hybrid retrieval over BM25 and Qdrant vector search."""
    active_settings = settings or get_settings()

    if collection_point_count(active_settings) == 0:
        raise RuntimeError(
            "Qdrant collection is empty. Start Qdrant and run scripts/ingest_knowledge.py first."
        )

    bm25_hits = BM25Index.from_settings(active_settings).search(
        query=query,
        top_k=active_settings.top_k_bm25,
        intent=intent,
    )
    query_vector = embed_query(query, active_settings)
    vector_hits = vector_search(
        query_vector=query_vector,
        top_k=active_settings.top_k_vector,
        intent=intent,
        settings=active_settings,
    )

    fused = _reciprocal_rank_fusion(bm25_hits, vector_hits)
    results: list[EvidenceChunk] = []
    for record, score, source in fused[: active_settings.top_k_final]:
        results.append(_to_evidence(record, score, source))
    return results
