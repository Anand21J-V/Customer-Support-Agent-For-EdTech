"""Certificate lookup repository."""

from typing import Any

from app.config import Settings
from app.db.mysql import fetch_one


def get_certificate(
    student_id: int,
    course_id: int,
    settings: Settings | None = None,
) -> dict[str, Any] | None:
    """Return a certificate row for a student and course, if present."""
    query = """
        SELECT id, student_id, course_id, status, certificate_url, issued_at
        FROM certificates
        WHERE student_id = %s AND course_id = %s
        LIMIT 1
    """
    return fetch_one(query, (student_id, course_id), settings)
