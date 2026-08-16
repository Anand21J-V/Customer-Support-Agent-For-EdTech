"""Load and sample router evaluation datasets."""

from __future__ import annotations

import csv
import json
import random
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.config import Settings, get_settings
from app.router.intents import get_intent_config
from app.schemas.router_types import STUDENT_INTENTS

REQUIRED_COLUMNS = ("user_type", "intent", "category", "query", "response", "priority")


@dataclass(frozen=True)
class DatasetRow:
    row_number: int
    user_type: str
    intent: str
    category: str
    query: str
    response: str
    priority: str


@dataclass(frozen=True)
class RegressionCase:
    id: str
    query: str
    expected_intent: str
    expected_route: str
    user_type: str
    source_row: int


@dataclass(frozen=True)
class RegressionSet:
    version: str
    created_at: str
    seed: int
    per_intent: int
    cases: list[RegressionCase]


def load_dataset_rows(path: str | Path) -> list[DatasetRow]:
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    rows: list[DatasetRow] = []
    with dataset_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Dataset CSV is missing a header row")
        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"Dataset CSV missing columns: {', '.join(missing)}")

        for row_number, row in enumerate(reader, start=2):
            rows.append(
                DatasetRow(
                    row_number=row_number,
                    user_type=row["user_type"].strip(),
                    intent=row["intent"].strip(),
                    category=row["category"].strip(),
                    query=row["query"].strip(),
                    response=row["response"].strip(),
                    priority=row["priority"].strip(),
                )
            )
    return rows


def intent_distribution(rows: list[DatasetRow]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.intent] = counts.get(row.intent, 0) + 1
    return counts


def build_regression_set(
    rows: list[DatasetRow],
    *,
    per_intent: int,
    seed: int,
) -> RegressionSet:
    grouped: dict[str, list[DatasetRow]] = {intent: [] for intent in STUDENT_INTENTS}
    for row in rows:
        if row.intent not in grouped:
            raise ValueError(f"Unexpected intent in dataset: {row.intent}")
        grouped[row.intent].append(row)

    rng = random.Random(seed)
    cases: list[RegressionCase] = []
    case_index = 1

    for intent in STUDENT_INTENTS:
        bucket = grouped[intent]
        if len(bucket) < per_intent:
            raise ValueError(
                f"Intent {intent} has only {len(bucket)} rows; need {per_intent}"
            )
        sampled = rng.sample(bucket, per_intent)
        for row in sampled:
            cases.append(
                RegressionCase(
                    id=f"reg_{case_index:04d}",
                    query=row.query,
                    expected_intent=row.intent,
                    expected_route=get_intent_config(row.intent).route,  # type: ignore[arg-type]
                    user_type=row.user_type,
                    source_row=row.row_number,
                )
            )
            case_index += 1

    return RegressionSet(
        version="1.0",
        created_at=datetime.now(UTC).isoformat(),
        seed=seed,
        per_intent=per_intent,
        cases=cases,
    )


def regression_set_to_dict(regression_set: RegressionSet) -> dict:
    return {
        "version": regression_set.version,
        "created_at": regression_set.created_at,
        "seed": regression_set.seed,
        "per_intent": regression_set.per_intent,
        "cases": [
            {
                "id": case.id,
                "query": case.query,
                "expected_intent": case.expected_intent,
                "expected_route": case.expected_route,
                "user_type": case.user_type,
                "source_row": case.source_row,
            }
            for case in regression_set.cases
        ],
    }


def save_regression_set(regression_set: RegressionSet, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(regression_set_to_dict(regression_set), indent=2),
        encoding="utf-8",
    )


def load_regression_set(path: str | Path) -> RegressionSet:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    cases = [
        RegressionCase(
            id=case["id"],
            query=case["query"],
            expected_intent=case["expected_intent"],
            expected_route=case["expected_route"],
            user_type=case["user_type"],
            source_row=case["source_row"],
        )
        for case in payload["cases"]
    ]
    return RegressionSet(
        version=payload["version"],
        created_at=payload.get("created_at", ""),
        seed=payload["seed"],
        per_intent=payload["per_intent"],
        cases=cases,
    )


def build_regression_set_from_settings(settings: Settings | None = None) -> RegressionSet:
    active_settings = settings or get_settings()
    rows = load_dataset_rows(active_settings.router_dataset_path)
    return build_regression_set(
        rows,
        per_intent=active_settings.router_regression_per_intent,
        seed=active_settings.router_regression_seed,
    )
