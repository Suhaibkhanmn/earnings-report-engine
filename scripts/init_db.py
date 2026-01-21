from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db import engine  # noqa: E402
from backend.app.models import Base  # noqa: E402


def main() -> None:
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        conn.exec_driver_sql(
            "ALTER TABLE chunks ADD COLUMN IF NOT EXISTS embedding vector(768)"
        )


if __name__ == "__main__":
    main()

