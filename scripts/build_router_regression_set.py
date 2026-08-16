"""Build the frozen router regression set from the CSV dataset."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings
from app.evaluation.dataset_loader import (
    build_regression_set_from_settings,
    intent_distribution,
    load_dataset_rows,
    save_regression_set,
)


def main() -> None:
    settings = get_settings()
    rows = load_dataset_rows(settings.router_dataset_path)
    distribution = intent_distribution(rows)

    regression_set = build_regression_set_from_settings(settings)
    save_regression_set(regression_set, settings.router_regression_path)

    print(f"Dataset rows: {len(rows)}")
    print(f"Intent labels: {len(distribution)}")
    print(f"Regression cases: {len(regression_set.cases)}")
    print(f"Saved: {settings.router_regression_path}")


if __name__ == "__main__":
    main()
