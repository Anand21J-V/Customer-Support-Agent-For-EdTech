"""Qdrant client helpers for knowledge retrieval."""

from __future__ import annotations

import uuid
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import Settings, get_settings
from app.schemas.knowledge import KnowledgeChunk

DEFAULT_FILTERS = {
    "audience": "student",
    "status": "active",
}


def chunk_point_id(chunk_id: str) -> str:
    """Return a deterministic UUID for a chunk."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))


def get_qdrant_client(settings: Settings | None = None) -> QdrantClient:
    active_settings = settings or get_settings()
    return QdrantClient(
        host=active_settings.qdrant_host,
        port=active_settings.qdrant_port,
    )


def ensure_collection(settings: Settings | None = None) -> None:
    """Create the knowledge collection if it does not exist."""
    active_settings = settings or get_settings()
    client = get_qdrant_client(active_settings)
    collection_name = active_settings.qdrant_collection

    if client.collection_exists(collection_name):
        info = client.get_collection(collection_name)
        vector_size = info.config.params.vectors.size  # type: ignore[union-attr]
        if vector_size != active_settings.embedding_dimension:
            raise ValueError(
                f"Collection {collection_name} has dimension {vector_size}, "
                f"expected {active_settings.embedding_dimension}"
            )
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=active_settings.embedding_dimension,
            distance=models.Distance.COSINE,
        ),
    )

    for field_name in ("intent", "category", "audience", "status", "policy_id"):
        client.create_payload_index(
            collection_name=collection_name,
            field_name=field_name,
            field_schema=models.PayloadSchemaType.KEYWORD,
        )


def _chunk_payload(chunk: KnowledgeChunk) -> dict[str, Any]:
    return {
        "chunk_id": chunk.chunk_id,
        "policy_id": chunk.policy_id,
        "document_type": chunk.document_type,
        "intent": chunk.intent,
        "category": chunk.category,
        "audience": chunk.audience,
        "route": chunk.route,
        "status": chunk.status,
        "version": chunk.version,
        "section": chunk.section,
        "text": chunk.text,
        "keywords": chunk.keywords,
    }


def upsert_chunks(
    chunks: list[KnowledgeChunk],
    vectors: list[list[float]],
    settings: Settings | None = None,
) -> None:
    """Upsert embedded chunks into Qdrant."""
    if len(chunks) != len(vectors):
        raise ValueError("Chunk and vector counts must match")

    active_settings = settings or get_settings()
    client = get_qdrant_client(active_settings)
    ensure_collection(active_settings)

    points = [
        models.PointStruct(
            id=chunk_point_id(chunk.chunk_id),
            vector=vector,
            payload=_chunk_payload(chunk),
        )
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]

    client.upsert(collection_name=active_settings.qdrant_collection, points=points)


def _build_filter(
    intent: str | None = None,
    extra_filters: dict[str, str] | None = None,
) -> models.Filter:
    filters = dict(DEFAULT_FILTERS)
    if extra_filters:
        filters.update(extra_filters)
    if intent:
        filters["intent"] = intent

    conditions = [
        models.FieldCondition(key=key, match=models.MatchValue(value=value))
        for key, value in filters.items()
    ]
    return models.Filter(must=conditions)


def vector_search(
    query_vector: list[float],
    top_k: int,
    intent: str | None = None,
    settings: Settings | None = None,
) -> list[dict[str, Any]]:
    """Search Qdrant using a query vector."""
    active_settings = settings or get_settings()
    client = get_qdrant_client(active_settings)
    if not client.collection_exists(active_settings.qdrant_collection):
        return []

    results = client.search(
        collection_name=active_settings.qdrant_collection,
        query_vector=query_vector,
        limit=top_k,
        query_filter=_build_filter(intent=intent),
        with_payload=True,
    )

    hits: list[dict[str, Any]] = []
    for result in results:
        payload = dict(result.payload or {})
        payload["score"] = float(result.score or 0.0)
        payload["source"] = "vector"
        hits.append(payload)
    return hits


def scroll_all_chunks(settings: Settings | None = None) -> list[dict[str, Any]]:
    """Return all stored chunk payloads from Qdrant."""
    active_settings = settings or get_settings()
    client = get_qdrant_client(active_settings)
    if not client.collection_exists(active_settings.qdrant_collection):
        return []

    records, _ = client.scroll(
        collection_name=active_settings.qdrant_collection,
        limit=10000,
        with_payload=True,
        with_vectors=False,
    )
    return [dict(record.payload or {}) for record in records]


def collection_point_count(settings: Settings | None = None) -> int:
    active_settings = settings or get_settings()
    client = get_qdrant_client(active_settings)
    if not client.collection_exists(active_settings.qdrant_collection):
        return 0
    info = client.get_collection(active_settings.qdrant_collection)
    return int(info.points_count or 0)
