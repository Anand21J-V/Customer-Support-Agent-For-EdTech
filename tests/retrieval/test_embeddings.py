"""Unit tests for local embedding helpers."""

import math

import pytest

from app.config import get_settings
from app.retrieval.embeddings import embed_query, embed_texts


@pytest.fixture(scope="module")
def settings():
    return get_settings()


def test_embed_texts_dimension(settings) -> None:
    vectors = embed_texts(["refund policy eligibility"], settings)
    assert len(vectors) == 1
    assert len(vectors[0]) == settings.embedding_dimension


def test_embed_query_normalized(settings) -> None:
    vector = embed_query("Can I get my money back after cancelling?", settings)
    assert len(vector) == settings.embedding_dimension
    magnitude = math.sqrt(sum(value * value for value in vector))
    assert abs(magnitude - 1.0) < 0.01
