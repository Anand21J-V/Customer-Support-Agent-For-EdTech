"""Evaluation metrics for router predictions."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from app.evaluation.dataset_loader import RegressionCase
from app.schemas.router import RouterDecision


@dataclass(frozen=True)
class PredictionResult:
    case: RegressionCase
    decision: RouterDecision


@dataclass(frozen=True)
class ConfusionPair:
    expected: str
    predicted: str
    count: int


@dataclass(frozen=True)
class RouterEvalReport:
    total: int
    intent_accuracy: float
    route_accuracy: float
    per_intent_accuracy: dict[str, float]
    confusion_pairs: list[ConfusionPair]

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "intent_accuracy": self.intent_accuracy,
            "route_accuracy": self.route_accuracy,
            "per_intent_accuracy": self.per_intent_accuracy,
            "confusion_pairs": [
                {
                    "expected": pair.expected,
                    "predicted": pair.predicted,
                    "count": pair.count,
                }
                for pair in self.confusion_pairs
            ],
        }


def evaluate_predictions(results: list[PredictionResult]) -> RouterEvalReport:
    if not results:
        return RouterEvalReport(0, 0.0, 0.0, {}, [])

    intent_correct = 0
    route_correct = 0
    per_intent_total: dict[str, int] = defaultdict(int)
    per_intent_correct: dict[str, int] = defaultdict(int)
    confusion_counter: Counter[tuple[str, str]] = Counter()

    for result in results:
        expected_intent = result.case.expected_intent
        predicted_intent = result.decision.intent
        per_intent_total[expected_intent] += 1

        if predicted_intent == expected_intent:
            intent_correct += 1
            per_intent_correct[expected_intent] += 1
        else:
            confusion_counter[(expected_intent, predicted_intent)] += 1

        if result.decision.route == result.case.expected_route:
            route_correct += 1

    total = len(results)
    per_intent_accuracy = {
        intent: per_intent_correct[intent] / per_intent_total[intent]
        for intent in sorted(per_intent_total)
    }
    confusion_pairs = [
        ConfusionPair(expected=expected, predicted=predicted, count=count)
        for (expected, predicted), count in confusion_counter.most_common(10)
    ]

    return RouterEvalReport(
        total=total,
        intent_accuracy=intent_correct / total,
        route_accuracy=route_correct / total,
        per_intent_accuracy=per_intent_accuracy,
        confusion_pairs=confusion_pairs,
    )
