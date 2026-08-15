"""Enrollment lookup repository."""

from typing import Any

from app.config import Settings
from app.db.mysql import fetch_one


def get_enrollment(
    student_id: int,
    course_id: int,
    settings: Settings | None = None,
) -> dict[str, Any] | None:
    """Return an enrollment row for a student and course."""
    query = """
        SELECT id, student_id, course_id, status, enrolled_at, completed_at, created_at
        FROM enrollments
        WHERE student_id = %s AND course_id = %s
        LIMIT 1
    """
    return fetch_one(query, (student_id, course_id), settings)
