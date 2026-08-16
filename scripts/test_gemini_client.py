"""Live smoke test for the Gemini structured-output client."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings
from app.llm.exceptions import GeminiConfigError, GeminiError
from app.llm.gemini_client import generate_structured
from app.schemas.llm import DemoClassification

DEMO_PROMPT = "Can I get my money back after cancelling?"


def main() -> None:
    settings = get_settings()
    if not settings.gemini_api_key.strip():
        raise GeminiConfigError(
            "GEMINI_API_KEY is empty. Add your key to .env before running this script."
        )

    try:
        result = generate_structured(
            DEMO_PROMPT,
            DemoClassification,
            model="generation",
            system_instruction=(
                "Classify the student support query. "
                "Return JSON matching the schema exactly."
            ),
            settings=settings,
        )
    except GeminiError as exc:
        print(f"Gemini call failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"model: {result.model}")
    print(f"intent: {result.data.intent}")
    print(f"confidence: {result.data.confidence:.2f}")
    print(f"summary: {result.data.summary}")
    print(f"prompt_tokens: {result.prompt_tokens}")
    print(f"output_tokens: {result.output_tokens}")
    print(f"latency_ms: {result.latency_ms}")


if __name__ == "__main__":
    main()
