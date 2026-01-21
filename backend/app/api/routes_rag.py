from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.ingestion.ingest import create_chunks_for_document
from backend.app.models import Chunk, Document
from backend.app.rag.retriever import retrieve_top_k
from backend.app.rag.vector_store import embed_chunks_for_document
from backend.app.schemas import RagSearchRequest, RagSearchResponse, RagSearchChunk
from sqlalchemy import func


router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/documents/{document_id}/embed", status_code=status.HTTP_200_OK)
def embed_document_chunks(document_id: str, db: Session = Depends(get_db)) -> dict[str, int | str]:
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    existing_chunks = db.scalars(
        select(Chunk).where(Chunk.document_id == document_id).limit(1)
    ).all()

    if not existing_chunks:
        create_chunks_for_document(db, doc)

    chunks_embedded = embed_chunks_for_document(db, document_id)
    total_chunks = db.scalar(
        select(func.count()).select_from(Chunk).where(Chunk.document_id == document_id)
    )

    return {
        "document_id": str(document_id),
        "chunks_embedded": chunks_embedded,
        "total_chunks": int(total_chunks or 0),
    }


@router.post("/search", response_model=RagSearchResponse)
def rag_search(payload: RagSearchRequest, db: Session = Depends(get_db)) -> RagSearchResponse:
    chunks = retrieve_top_k(
        db=db,
        query=payload.query,
        k=payload.k,
        document_id=str(payload.document_id) if payload.document_id is not None else None,
    )

    results: list[RagSearchChunk] = []
    for c in chunks:
        results.append(
            RagSearchChunk(
                chunk_id=c.id,
                document_id=c.document_id,
                chunk_index=c.chunk_index,
                section=c.section,
                speaker=c.speaker,
                text=c.text,
            )
        )

    return RagSearchResponse(query=payload.query, k=payload.k, results=results)

