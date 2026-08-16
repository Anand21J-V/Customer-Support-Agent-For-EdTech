"""Re-run the Phase 1 seed SQL file against the configured database."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings
from app.db.mysql import get_connection


def main() -> None:
    seed_path = Path(__file__).resolve().parents[1] / "app" / "db" / "schema" / "02_seed.sql"
    sql = seed_path.read_text(encoding="utf-8")

    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip() and not statement.strip().startswith("--")
    ]

    settings = get_settings()
    with get_connection(settings) as connection:
        cursor = connection.cursor()
        try:
            for statement in statements:
                cursor.execute(statement)
            connection.commit()
            print(f"Seed applied from {seed_path}")
        finally:
            cursor.close()


if __name__ == "__main__":
    main()
