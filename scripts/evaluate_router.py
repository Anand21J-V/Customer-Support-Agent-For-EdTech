"""Evaluate router intent accuracy on the frozen regression set."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings
from app.evaluation.dataset_loader import load_regression_set
from app.evaluation.metrics import PredictionResult, evaluate_predictions
from app.router.router import classify_query


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate router intent accuracy")
    parser.add_argument("--limit", type=int, default=None, help="Evaluate only N cases")
    parser.add_argument(
        "--delay",
        type=float,
        default=None,
        help="Seconds to wait between API calls (defaults to ROUTER_EVAL_DELAY_SECONDS)",
    )
    args = parser.parse_args()

    settings = get_settings()
    delay_seconds = (
        settings.router_eval_delay_seconds if args.delay is None else args.delay
    )
    regression_set = load_regression_set(settings.router_regression_path)
    cases = regression_set.cases[: args.limit] if args.limit else regression_set.cases

    results: list[PredictionResult] = []
    for index, case in enumerate(cases, start=1):
        decision = classify_query(
            case.query,
            user_type=case.user_type,
            settings=settings,
        )
        results.append(PredictionResult(case=case, decision=decision))
        print(
            f"[{index}/{len(cases)}] expected={case.expected_intent} "
            f"predicted={decision.intent} confidence={decision.confidence:.2f}"
        )
        if delay_seconds > 0 and index < len(cases):
            time.sleep(delay_seconds)

    report = evaluate_predictions(results)
    payload = {
        "evaluated_at": datetime.now(UTC).isoformat(),
        "regression_path": settings.router_regression_path,
        "cases_evaluated": len(cases),
        **report.to_dict(),
    }

    report_path = Path(settings.router_eval_report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"\nintent_accuracy: {report.intent_accuracy:.3f}")
    print(f"route_accuracy: {report.route_accuracy:.3f}")
    print(f"report_saved: {report_path}")

    if report.confusion_pairs:
        print("\nTop confusion pairs:")
        for pair in report.confusion_pairs:
            print(f"  {pair.expected} -> {pair.predicted}: {pair.count}")

    if report.intent_accuracy < 0.90 and len(cases) >= 100:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
