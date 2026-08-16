"""Unit tests for the Gemini client (mocked, no network)."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest
from google.genai import errors as genai_errors

from app.config import Settings
from app.llm.exceptions import (
    GeminiConfigError,
    GeminiParseError,
    GeminiRateLimitError,
    GeminiSafetyError,
)
from app.llm.gemini_client import generate_structured, resolve_model_id
from app.schemas.llm import DemoClassification

VALID_JSON = (
    '{"intent": "refund", "confidence": 0.92, '
    '"summary": "Student asking about refund after cancellation."}'
)
INVALID_JSON = "not-json"


@dataclass
class _UsageMetadata:
    prompt_token_count: int
    candidates_token_count: int


@dataclass
class _Candidate:
    finish_reason: str
    content: object | None = None


@dataclass
class _PromptFeedback:
    block_reason: str | None = None


def _make_response(
    text: str = VALID_JSON,
    *,
    finish_reason: str = "STOP",
    block_reason: str | None = None,
    include_usage: bool = True,
) -> MagicMock:
    response = MagicMock()
    response.text = text
    response.candidates = [_Candidate(finish_reason=finish_reason)]
    response.prompt_feedback = _PromptFeedback(block_reason=block_reason)
    if include_usage:
        response.usage_metadata = _UsageMetadata(
            prompt_token_count=42,
            candidates_token_count=18,
        )
    else:
        response.usage_metadata = None
    return response


@pytest.fixture
def settings() -> Settings:
    return Settings(
        gemini_api_key="test-key",
        gemini_generation_model="gemini-3.6-flash",
        gemini_fast_model="gemini-3.5-flash-lite",
        gemini_parse_retries=1,
    )


def test_missing_api_key_raises_config_error() -> None:
    empty_settings = Settings(gemini_api_key="")
    with pytest.raises(GeminiConfigError, match="GEMINI_API_KEY"):
        generate_structured(
            "hello",
            DemoClassification,
            settings=empty_settings,
        )


@patch("app.llm.gemini_client.get_gemini_client")
def test_valid_json_returns_validated_model(mock_get_client: MagicMock, settings: Settings) -> None:
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _make_response()
    mock_get_client.return_value = mock_client

    result = generate_structured(
        "Can I get my money back after cancelling?",
        DemoClassification,
        settings=settings,
    )

    assert result.model == "gemini-3.6-flash"
    assert result.data.intent == "refund"
    assert result.data.confidence == pytest.approx(0.92)
    assert result.prompt_tokens == 42
    assert result.output_tokens == 18
    assert result.latency_ms >= 0


@patch("app.llm.gemini_client.get_gemini_client")
def test_invalid_json_then_valid_retry_succeeds(
    mock_get_client: MagicMock,
    settings: Settings,
) -> None:
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        _make_response(INVALID_JSON),
        _make_response(),
    ]
    mock_get_client.return_value = mock_client

    result = generate_structured("refund question", DemoClassification, settings=settings)

    assert result.data.intent == "refund"
    assert mock_client.models.generate_content.call_count == 2


@patch("app.llm.gemini_client.get_gemini_client")
def test_invalid_json_twice_raises_parse_error(
    mock_get_client: MagicMock,
    settings: Settings,
) -> None:
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _make_response(INVALID_JSON)
    mock_get_client.return_value = mock_client

    with pytest.raises(GeminiParseError):
        generate_structured("refund question", DemoClassification, settings=settings)

    assert mock_client.models.generate_content.call_count == 2


@patch("app.llm.gemini_client.get_gemini_client")
def test_rate_limit_raises_typed_error(mock_get_client: MagicMock, settings: Settings) -> None:
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = genai_errors.ClientError(
        429,
        {"error": {"message": "rate limit"}},
        None,
    )
    mock_get_client.return_value = mock_client

    with pytest.raises(GeminiRateLimitError):
        generate_structured("hello", DemoClassification, settings=settings)


@patch("app.llm.gemini_client.get_gemini_client")
def test_safety_finish_reason_raises_safety_error(
    mock_get_client: MagicMock,
    settings: Settings,
) -> None:
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _make_response(
        text="",
        finish_reason="SAFETY",
    )
    mock_get_client.return_value = mock_client

    with pytest.raises(GeminiSafetyError, match="SAFETY"):
        generate_structured("unsafe prompt", DemoClassification, settings=settings)


@patch("app.llm.gemini_client.get_gemini_client")
def test_fast_model_alias_uses_fast_model(mock_get_client: MagicMock, settings: Settings) -> None:
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _make_response()
    mock_get_client.return_value = mock_client

    result = generate_structured(
        "hello",
        DemoClassification,
        model="fast",
        settings=settings,
    )

    assert result.model == "gemini-3.5-flash-lite"
    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == "gemini-3.5-flash-lite"


def test_resolve_model_id_aliases(settings: Settings) -> None:
    assert resolve_model_id(settings, "generation") == "gemini-3.5-flash"
    assert resolve_model_id(settings, "fast") == "gemini-2.5-flash"
