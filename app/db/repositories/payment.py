"""Payment lookup repositories."""

from typing import Any

from app.config import Settings
from app.db.mysql import fetch_all, fetch_one


def get_payment(
    transaction_id: str,
    settings: Settings | None = None,
) -> dict[str, Any] | None:
    """Return a payment row by transaction_id."""
    query = """
        SELECT id, student_id, course_id, transaction_id, amount, currency, status, created_at
        FROM payments
        WHERE transaction_id = %s
        LIMIT 1
    """
    return fetch_one(query, (transaction_id,), settings)


def get_payments_by_student_course(
    student_id: int,
    course_id: int,
    settings: Settings | None = None,
) -> list[dict[str, Any]]:
    """Return all payment rows for a student and course."""
    query = """
        SELECT id, student_id, course_id, transaction_id, amount, currency, status, created_at
        FROM payments
        WHERE student_id = %s AND course_id = %s
        ORDER BY created_at ASC, id ASC
    """
    return fetch_all(query, (student_id, course_id), settings)
