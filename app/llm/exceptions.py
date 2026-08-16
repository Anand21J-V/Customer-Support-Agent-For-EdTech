"""Typed exceptions for Gemini LLM calls."""


class GeminiError(Exception):
    """Base class for Gemini client errors."""


class GeminiConfigError(GeminiError):
    """Configuration is missing or invalid (e.g. empty API key)."""


class GeminiTimeoutError(GeminiError):
    """The request exceeded the configured timeout."""


class GeminiRateLimitError(GeminiError):
    """The API returned HTTP 429 (rate limit)."""


class GeminiSafetyError(GeminiError):
    """Content was blocked by safety filters or prompt policy."""


class GeminiParseError(GeminiError):
    """Response could not be parsed or validated against the schema."""


class GeminiAPIError(GeminiError):
    """Other Gemini API or transport failures."""
