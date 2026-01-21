from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import Chunk
from backend.app.rag.embeddings import embed_query


def retrieve_top_k(
    db: Session,
    query: str,
    k: int = 8,
    document_id: str | None = None,
) -> list[Chunk]:
    qvec = embed_query(query)

    stmt = select(Chunk).where(Chunk.embedding.is_not(None))
    if document_id is not None:
        stmt = stmt.where(Chunk.document_id == document_id)

    stmt = stmt.order_by(Chunk.embedding.op("<=>")(qvec)).limit(k)

    return list(db.scalars(stmt).all())

