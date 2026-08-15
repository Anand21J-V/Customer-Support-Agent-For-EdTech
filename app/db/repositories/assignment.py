"""Assignment and submission lookup repositories."""

from typing import Any

from app.config import Settings
from app.db.mysql import fetch_one


def get_assignment(
    assignment_id: int,
    settings: Settings | None = None,
) -> dict[str, Any] | None:
    """Return an assignment row by primary key."""
    query = """
        SELECT id, course_id, title, description, deadline, created_at
        FROM assignments
        WHERE id = %s
        LIMIT 1
    """
    return fetch_one(query, (assignment_id,), settings)


def get_submission(
    assignment_id: int,
    student_id: int,
    settings: Settings | None = None,
) -> dict[str, Any] | None:
    """Return a submission row for a student and assignment."""
    query = """
        SELECT id, assignment_id, student_id, status, submitted_at, grade
        FROM submissions
        WHERE assignment_id = %s AND student_id = %s
        LIMIT 1
    """
    return fetch_one(query, (assignment_id, student_id), settings)
