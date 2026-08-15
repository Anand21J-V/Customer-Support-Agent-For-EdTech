"""Local open-source embedding helpers."""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import Settings, get_settings

_model: SentenceTransformer | None = None
_model_name: str | None = None


def _load_model(model_name: str) -> SentenceTransformer:
    global _model, _model_name
    if _model is None or _model_name != model_name:
        _model = SentenceTransformer(model_name)
        _model_name = model_name
    return _model


@lru_cache
def get_embedding_model_name(settings: Settings | None = None) -> str:
    active_settings = settings or get_settings()
    return active_settings.embedding_model


def embed_texts(texts: list[str], settings: Settings | None = None) -> list[list[float]]:
    """Embed a batch of texts using the configured sentence-transformer model."""
    if not texts:
        return []

    active_settings = settings or get_settings()
    model = _load_model(active_settings.embedding_model)
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    np_vectors = np.asarray(vectors)
    if np_vectors.ndim == 1:
        np_vectors = np_vectors.reshape(1, -1)

    output = np_vectors.tolist()
    for vector in output:
        if len(vector) != active_settings.embedding_dimension:
            raise ValueError(
                f"Expected embedding dimension {active_settings.embedding_dimension}, "
                f"got {len(vector)}"
            )
    return output


def embed_query(query: str, settings: Settings | None = None) -> list[float]:
    """Embed a single query string."""
    vectors = embed_texts([query], settings=settings)
    return vectors[0]
