"""Unit tests for router evaluation metrics."""

from app.evaluation.dataset_loader import RegressionCase
from app.evaluation.metrics import PredictionResult, evaluate_predictions
from app.schemas.router import RouterDecision


def _decision(intent: str, route: str) -> RouterDecision:
    return RouterDecision(
        intent=intent,  # type: ignore[arg-type]
        sub_intent="test",
        route=route,  # type: ignore[arg-type]
        requires_rag=False,
        requires_tool=False,
        requires_planning=False,
        escalation_candidate=False,
        confidence=0.9,
        is_unknown=False,
        raw_intent=None,
        model="test",
        latency_ms=1,
        prompt_tokens=1,
        output_tokens=1,
    )


def test_evaluate_predictions_computes_accuracy() -> None:
    cases = [
        RegressionCase(
            id="reg_0001",
            query="refund please",
            expected_intent="refund",
            expected_route="knowledge",
            user_type="student",
            source_row=1,
        ),
        RegressionCase(
            id="reg_0002",
            query="payment failed",
            expected_intent="payment",
            expected_route="operations",
            user_type="student",
            source_row=2,
        ),
    ]
    results = [
        PredictionResult(case=cases[0], decision=_decision("refund", "knowledge")),
        PredictionResult(case=cases[1], decision=_decision("enrollment", "operations")),
    ]

    report = evaluate_predictions(results)

    assert report.total == 2
    assert report.intent_accuracy == 0.5
    assert report.route_accuracy == 1.0
    assert report.confusion_pairs[0].expected == "payment"
    assert report.confusion_pairs[0].predicted == "enrollment"
