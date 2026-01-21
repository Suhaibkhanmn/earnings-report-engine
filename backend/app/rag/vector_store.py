from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import Chunk
from backend.app.rag.embeddings import embed_texts


def embed_chunks_for_document(db: Session, document_id, batch_size: int = 32) -> int:
    total = 0

    while True:
        stmt = (
            select(Chunk)
            .where(Chunk.document_id == document_id)
            .where(Chunk.embedding.is_(None))
            .order_by(Chunk.section.asc(), Chunk.chunk_index.asc())
            .limit(batch_size)
        )
        batch: Sequence[Chunk] = db.scalars(stmt).all()
        if not batch:
            break

        vectors = embed_texts([c.text for c in batch])
        for chunk, vec in zip(batch, vectors, strict=True):
            chunk.embedding = vec

        db.commit()
        total += len(batch)

    return total

