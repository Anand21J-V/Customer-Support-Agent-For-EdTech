"""Student and course lookup repositories."""

from typing import Any

from app.config import Settings
from app.db.mysql import fetch_one


def get_student(external_id: str, settings: Settings | None = None) -> dict[str, Any] | None:
    """Return a student row by external_id."""
    query = """
        SELECT id, external_id, name, email, status, created_at, updated_at
        FROM students
        WHERE external_id = %s
        LIMIT 1
    """
    return fetch_one(query, (external_id,), settings)


def get_student_by_id(student_id: int, settings: Settings | None = None) -> dict[str, Any] | None:
    """Return a student row by primary key."""
    query = """
        SELECT id, external_id, name, email, status, created_at, updated_at
        FROM students
        WHERE id = %s
        LIMIT 1
    """
    return fetch_one(query, (student_id,), settings)


def get_course_by_external_id(
    external_id: str,
    settings: Settings | None = None,
) -> dict[str, Any] | None:
    """Return a course row by external_id."""
    query = """
        SELECT id, external_id, title, description, status, created_at
        FROM courses
        WHERE external_id = %s
        LIMIT 1
    """
    return fetch_one(query, (external_id,), settings)
