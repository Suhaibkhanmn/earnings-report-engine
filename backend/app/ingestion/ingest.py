from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.ingestion.chunker import ChunkInput, chunk_section
from backend.app.ingestion.parser import parse_transcript
from backend.app.models import Chunk, Document


def create_chunks_for_document(db: Session, document: Document) -> list[Chunk]:
    parsed = parse_transcript(document.raw_text)

    chunk_inputs: list[ChunkInput] = []
    for section_name, section_text in parsed.sections.items():
        chunk_inputs.extend(chunk_section(section_name, section_text))

    chunks: list[Chunk] = []
    for ci in chunk_inputs:
        chunk = Chunk(
            document_id=document.id,
            section=ci.section,
            speaker=ci.speaker,
            chunk_index=ci.index,
            text=ci.text,
        )
        db.add(chunk)
        chunks.append(chunk)

    if chunks:
        db.commit()
        for chunk in chunks:
            db.refresh(chunk)

    return chunks

