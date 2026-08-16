"""Optional live router regression checks."""

import pytest

from app.config import get_settings
from app.evaluation.dataset_loader import load_regression_set
from app.evaluation.metrics import PredictionResult, evaluate_predictions
from app.router.router import classify_query


@pytest.mark.live
def test_live_router_regression_subset() -> None:
    settings = get_settings()
    if not settings.gemini_api_key.strip():
        pytest.skip("GEMINI_API_KEY is not configured")

    regression_set = load_regression_set(settings.router_regression_path)
    cases = regression_set.cases[:10]

    results = [
        PredictionResult(
            case=case,
            decision=classify_query(case.query, user_type=case.user_type, settings=settings),
        )
        for case in cases
    ]
    report = evaluate_predictions(results)

    assert report.intent_accuracy >= 0.70
