"""BM25 keyword search over the ingested knowledge corpus."""

from __future__ import annotations

import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

from app.config import Settings, get_settings
from app.schemas.knowledge import KnowledgeChunk

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def build_corpus_records(chunks: list[KnowledgeChunk]) -> list[dict[str, object]]:
    return [
        {
            "chunk_id": chunk.chunk_id,
            "policy_id": chunk.policy_id,
            "intent": chunk.intent,
            "category": chunk.category,
            "audience": chunk.audience,
            "status": chunk.status,
            "section": chunk.section,
            "text": chunk.text,
            "keywords": chunk.keywords,
        }
        for chunk in chunks
    ]


def save_corpus_manifest(records: list[dict[str, object]], path: str | Path) -> None:
    manifest_path = Path(path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def load_corpus_manifest(path: str | Path) -> list[dict[str, object]]:
    manifest_path = Path(path)
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"BM25 corpus manifest not found at {manifest_path}. Run scripts/ingest_knowledge.py first."
        )
    return json.loads(manifest_path.read_text(encoding="utf-8"))


class BM25Index:
    """In-memory BM25 index backed by a corpus manifest."""

    def __init__(self, records: list[dict[str, object]]) -> None:
        self.records = records
        self.tokenized_corpus = [tokenize(str(record.get("text", ""))) for record in records]
        self.index = BM25Okapi(self.tokenized_corpus) if self.tokenized_corpus else None

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> BM25Index:
        active_settings = settings or get_settings()
        records = load_corpus_manifest(active_settings.bm25_cache_path)
        return cls(records)

    def search(self, query: str, top_k: int, intent: str | None = None) -> list[dict[str, object]]:
        if not self.index or not self.records:
            return []

        scores = self.index.get_scores(tokenize(query))
        ranked = sorted(
            enumerate(scores),
            key=lambda item: item[1],
            reverse=True,
        )

        hits: list[dict[str, object]] = []
        for index, score in ranked:
            if score <= 0:
                continue
            record = dict(self.records[index])
            if record.get("audience") != "student" or record.get("status") != "active":
                continue
            if intent and record.get("intent") != intent:
                continue
            record["score"] = float(score)
            record["source"] = "bm25"
            hits.append(record)
            if len(hits) >= top_k:
                break
        return hits
