"""CLI demo for a single router classification."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings
from app.router.router import classify_query


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify a single student query")
    parser.add_argument("--query", required=True, help="Student support message")
    parser.add_argument("--user-type", default=None, help="Optional user type")
    parser.add_argument("--student-id", default=None, help="Optional student ID")
    parser.add_argument("--turn", type=int, default=None, help="Optional conversation turn")
    args = parser.parse_args()

    settings = get_settings()
    decision = classify_query(
        args.query,
        user_type=args.user_type,
        student_id=args.student_id,
        conversation_turn=args.turn,
        settings=settings,
    )

    print(f"intent: {decision.intent}")
    print(f"sub_intent: {decision.sub_intent}")
    print(f"route: {decision.route}")
    print(f"requires_rag: {decision.requires_rag}")
    print(f"requires_tool: {decision.requires_tool}")
    print(f"requires_planning: {decision.requires_planning}")
    print(f"escalation_candidate: {decision.escalation_candidate}")
    print(f"confidence: {decision.confidence:.2f}")
    print(f"is_unknown: {decision.is_unknown}")
    print(f"raw_intent: {decision.raw_intent}")
    print(f"model: {decision.model}")
    print(f"latency_ms: {decision.latency_ms}")


if __name__ == "__main__":
    main()
