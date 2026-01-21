from __future__ import annotations

import uuid

from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.ingestion.ingest import create_chunks_for_document
from backend.app.models import Document
from backend.app.schemas import ChunkOut, DocumentCreate, DocumentDetail, DocumentOut


router = APIRouter(prefix="", tags=["ingest"])


@router.post("/ingest", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def ingest_document(payload: DocumentCreate, db: Session = Depends(get_db)) -> DocumentOut:
    doc = Document(
        ticker=payload.ticker.strip().upper(),
        quarter=payload.quarter.strip().upper(),
        call_date=payload.call_date,
        raw_text=payload.raw_text,
    )

    db.add(doc)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document already exists for (ticker, quarter).",
        )

    db.refresh(doc)

    create_chunks_for_document(db, doc)

    return DocumentOut.model_validate(doc)


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)) -> list[DocumentOut]:
    docs = db.scalars(select(Document).order_by(Document.ticker.asc(), Document.quarter.asc())).all()
    return [DocumentOut.model_validate(d) for d in docs]


@router.get("/documents/{document_id}", response_model=DocumentDetail)
def get_document(document_id: uuid.UUID, db: Session = Depends(get_db)) -> DocumentDetail:
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return DocumentDetail.model_validate(doc)


@router.post("/ingest/file", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def ingest_document_file(
    ticker: str = Form(...),
    quarter: str = Form(...),
    call_date: date | None = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentOut:
    content_bytes = await file.read()
    try:
        raw_text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript file must be UTF-8 encoded text.",
        )

    doc = Document(
        ticker=ticker.strip().upper(),
        quarter=quarter.strip().upper(),
        call_date=call_date,
        raw_text=raw_text,
    )

    db.add(doc)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document already exists for (ticker, quarter).",
        )

    db.refresh(doc)

    create_chunks_for_document(db, doc)

    return DocumentOut.model_validate(doc)


@router.get("/documents/{document_id}/chunks", response_model=list[ChunkOut])
def list_document_chunks(document_id: uuid.UUID, db: Session = Depends(get_db)) -> list[ChunkOut]:
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    from backend.app.models import Chunk

    chunks = db.scalars(
        select(Chunk)
        .where(Chunk.document_id == document_id)
        .order_by(Chunk.section.asc(), Chunk.chunk_index.asc())
    ).all()

    return [ChunkOut.model_validate(c) for c in chunks]

