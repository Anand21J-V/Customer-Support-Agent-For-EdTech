"""MySQL connection helper using mysql-connector-python."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import mysql.connector
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursorDict

from app.config import Settings, get_settings


def _connection_kwargs(settings: Settings) -> dict[str, Any]:
    return {
        "host": settings.mysql_host,
        "port": settings.mysql_port,
        "database": settings.mysql_database,
        "user": settings.mysql_user,
        "password": settings.mysql_password,
        "autocommit": False,
    }


@contextmanager
def get_connection(settings: Settings | None = None) -> Generator[MySQLConnection, None, None]:
    """Yield a MySQL connection and close it when done."""
    active_settings = settings or get_settings()
    connection = mysql.connector.connect(**_connection_kwargs(active_settings))
    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def get_cursor(
    settings: Settings | None = None,
) -> Generator[MySQLCursorDict, None, None]:
    """Yield a dict cursor inside a managed connection."""
    with get_connection(settings) as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            yield cursor
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()


def fetch_one(
    query: str,
    params: tuple[Any, ...] | dict[str, Any] | None = None,
    settings: Settings | None = None,
) -> dict[str, Any] | None:
    """Run a SELECT and return one row or None."""
    with get_cursor(settings) as cursor:
        cursor.execute(query, params or ())
        row = cursor.fetchone()
        return row if row is None else dict(row)


def fetch_all(
    query: str,
    params: tuple[Any, ...] | dict[str, Any] | None = None,
    settings: Settings | None = None,
) -> list[dict[str, Any]]:
    """Run a SELECT and return all rows."""
    with get_cursor(settings) as cursor:
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
