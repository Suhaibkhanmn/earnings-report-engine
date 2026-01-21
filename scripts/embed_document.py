from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from sqlalchemy import select, func

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db import SessionLocal  # noqa: E402
from backend.app.models import Chunk  # noqa: E402
from backend.app.rag.embeddings import embed_texts  # noqa: E402


def embed_document(document_id: str, batch_size: int = 16) -> None:
    with SessionLocal() as db:
        total = 0

        while True:
            stmt = (
                select(Chunk)
                .where(Chunk.document_id == document_id)
                .where(Chunk.embedding.is_(None))
                .order_by(Chunk.section.asc(), Chunk.chunk_index.asc())
                .limit(batch_size)
            )
            batch = db.scalars(stmt).all()
            if not batch:
                break

            vectors = embed_texts([c.text for c in batch])
            for chunk, vec in zip(batch, vectors, strict=True):
                chunk.embedding = vec

            db.commit()
            total += len(batch)
            print(f"Embedded {total} chunks so far...")

        embedded_stmt = (
            select(func.count())
            .select_from(Chunk)
            .where(Chunk.document_id == document_id)
            .where(Chunk.embedding.is_not(None))
        )
        embedded = db.scalar(embedded_stmt) or 0
        print(f"Done. Total embedded chunks for {document_id}: {int(embedded)}")


def main(doc_id: Optional[str]) -> None:
    if not doc_id:
        print("Usage: python scripts/embed_document.py <document_id>")
        raise SystemExit(1)
    embed_document(doc_id)


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg)

