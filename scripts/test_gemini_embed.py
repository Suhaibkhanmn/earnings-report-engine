from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.rag.embeddings import embed_texts  # noqa: E402


def main() -> None:
    texts = ["Test embedding from Earnings Call Intelligence Engine."]
    vectors = embed_texts(texts)
    print(f"Got {len(vectors)} embedding(s). First vector length: {len(vectors[0]) if vectors else 0}")


if __name__ == "__main__":
    main()

