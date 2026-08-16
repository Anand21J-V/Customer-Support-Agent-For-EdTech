"""Reusable Gemini client with structured output."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Generic, Literal, TypeVar

from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from pydantic import BaseModel, ValidationError

from app.config import Settings, get_settings
from app.llm.exceptions import (
    GeminiAPIError,
    GeminiConfigError,
    GeminiParseError,
    GeminiRateLimitError,
    GeminiSafetyError,
    GeminiTimeoutError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

ModelAlias = Literal["generation", "fast"]

BLOCKED_FINISH_REASONS = frozenset(
    {
        "SAFETY",
        "BLOCKLIST",
        "PROHIBITED_CONTENT",
        "SPII",
        "IMAGE_SAFETY",
        "RECITATION",
    }
)

RETRY_HTTP_STATUS_CODES = [408, 429, 500, 502, 503, 504]


@dataclass(frozen=True)
class LLMCallResult(Generic[T]):
    """Validated structured output plus call metadata."""

    data: T
    model: str
    latency_ms: int
    prompt_tokens: int | None
    output_tokens: int | None


def _ensure_logging(settings: Settings) -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(level=settings.log_level)


def _require_api_key(settings: Settings) -> None:
    if not settings.gemini_api_key.strip():
        raise GeminiConfigError(
            "GEMINI_API_KEY is empty. Set it in .env before calling Gemini."
        )


def resolve_model_id(settings: Settings, model: ModelAlias) -> str:
    """Map a model alias to the configured Gemini model ID."""
    if model == "fast":
        return settings.gemini_fast_model
    return settings.gemini_generation_model


def get_gemini_client(settings: Settings | None = None) -> genai.Client:
    """Create a configured Gemini SDK client."""
    active_settings = settings or get_settings()
    _require_api_key(active_settings)
    return genai.Client(
        api_key=active_settings.gemini_api_key,
        http_options=types.HttpOptions(
            timeout=active_settings.gemini_timeout_ms,
            retry_options=types.HttpRetryOptions(
                attempts=active_settings.gemini_retry_attempts,
                http_status_codes=RETRY_HTTP_STATUS_CODES,
            ),
        ),
    )


def _map_api_error(
    exc: Exception,
) -> GeminiAPIError | GeminiRateLimitError | GeminiTimeoutError:
    if isinstance(exc, genai_errors.ClientError):
        if exc.code == 429:
            return GeminiRateLimitError(str(exc))
        if exc.code == 408:
            return GeminiTimeoutError(str(exc))
        return GeminiAPIError(str(exc))
    if isinstance(exc, genai_errors.ServerError):
        return GeminiAPIError(str(exc))
    if isinstance(exc, genai_errors.APIError):
        if exc.code == 429:
            return GeminiRateLimitError(str(exc))
        if exc.code == 408:
            return GeminiTimeoutError(str(exc))
        return GeminiAPIError(str(exc))

    exc_name = type(exc).__name__.lower()
    message = str(exc).lower()
    if "timeout" in exc_name or "timed out" in message:
        return GeminiTimeoutError(str(exc))
    return GeminiAPIError(str(exc))


def _extract_response_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return ""

    content = getattr(candidates[0], "content", None)
    if content is None:
        return ""

    parts = getattr(content, "parts", None) or []
    joined = "".join(getattr(part, "text", "") or "" for part in parts).strip()
    return joined


def _normalize_finish_reason(finish_reason: Any) -> str:
    if finish_reason is None:
        return ""
    reason = str(finish_reason)
    if "." in reason:
        reason = reason.rsplit(".", maxsplit=1)[-1]
    return reason


def _check_safety(response: Any) -> None:
    prompt_feedback = getattr(response, "prompt_feedback", None)
    if prompt_feedback is not None:
        block_reason = getattr(prompt_feedback, "block_reason", None)
        if block_reason and str(block_reason) not in {
            "BLOCK_REASON_UNSPECIFIED",
            "None",
            "",
        }:
            raise GeminiSafetyError(f"Prompt blocked: {block_reason}")

    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return

    finish_reason = _normalize_finish_reason(getattr(candidates[0], "finish_reason", None))
    if finish_reason in BLOCKED_FINISH_REASONS:
        raise GeminiSafetyError(f"Generation blocked: finish_reason={finish_reason}")


def _extract_token_counts(response: Any) -> tuple[int | None, int | None]:
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return None, None
    prompt_tokens = getattr(usage, "prompt_token_count", None)
    output_tokens = getattr(usage, "candidates_token_count", None)
    return prompt_tokens, output_tokens


def _validate_structured_response(text: str, schema: type[T]) -> T:
    if not text:
        raise GeminiParseError("Gemini returned empty response text.")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise GeminiParseError(f"Invalid JSON from Gemini: {exc}") from exc
    try:
        return schema.model_validate(payload)
    except ValidationError as exc:
        raise GeminiParseError(f"Response failed schema validation: {exc}") from exc


def _call_gemini_structured(
    client: genai.Client,
    *,
    model_id: str,
    prompt: str,
    schema: type[T],
    system_instruction: str | None,
) -> Any:
    config_kwargs: dict[str, Any] = {
        "response_mime_type": "application/json",
        "response_schema": schema,
        "temperature": 0,
    }
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction

    return client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=types.GenerateContentConfig(**config_kwargs),
    )


def generate_structured(
    prompt: str,
    schema: type[T],
    *,
    model: ModelAlias = "generation",
    system_instruction: str | None = None,
    settings: Settings | None = None,
) -> LLMCallResult[T]:
    """Call Gemini and return Pydantic-validated structured output."""
    active_settings = settings or get_settings()
    _ensure_logging(active_settings)
    _require_api_key(active_settings)

    model_id = resolve_model_id(active_settings, model)
    client = get_gemini_client(active_settings)
    max_parse_attempts = 1 + active_settings.gemini_parse_retries

    last_parse_error: GeminiParseError | None = None
    start = time.perf_counter()

    for attempt in range(max_parse_attempts):
        try:
            response = _call_gemini_structured(
                client,
                model_id=model_id,
                prompt=prompt,
                schema=schema,
                system_instruction=system_instruction,
            )
            _check_safety(response)
            text = _extract_response_text(response)
            data = _validate_structured_response(text, schema)
            latency_ms = int((time.perf_counter() - start) * 1000)
            prompt_tokens, output_tokens = _extract_token_counts(response)

            logger.info(
                "gemini_call_success model=%s latency_ms=%s prompt_tokens=%s "
                "output_tokens=%s parse_attempt=%s",
                model_id,
                latency_ms,
                prompt_tokens,
                output_tokens,
                attempt + 1,
            )
            return LLMCallResult(
                data=data,
                model=model_id,
                latency_ms=latency_ms,
                prompt_tokens=prompt_tokens,
                output_tokens=output_tokens,
            )
        except GeminiSafetyError:
            logger.warning("gemini_call_blocked model=%s", model_id)
            raise
        except GeminiParseError as exc:
            last_parse_error = exc
            logger.warning(
                "gemini_parse_retry model=%s attempt=%s error=%s",
                model_id,
                attempt + 1,
                exc,
            )
            if attempt + 1 >= max_parse_attempts:
                break
            continue
        except (genai_errors.APIError, genai_errors.ClientError, genai_errors.ServerError) as exc:
            mapped = _map_api_error(exc)
            logger.error("gemini_call_failed model=%s error=%s", model_id, mapped)
            raise mapped from exc
        except Exception as exc:
            mapped = _map_api_error(exc)
            logger.error("gemini_call_failed model=%s error=%s", model_id, mapped)
            raise mapped from exc

    assert last_parse_error is not None
    logger.error("gemini_parse_exhausted model=%s error=%s", model_id, last_parse_error)
    raise last_parse_error
