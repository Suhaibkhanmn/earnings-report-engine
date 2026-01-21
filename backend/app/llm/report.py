from __future__ import annotations

import json
from typing import Any

from google import genai
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.llm.prompts import BASE_REPORT_INSTRUCTIONS, REPORT_JSON_SCHEMA
from backend.app.models import Chunk, Document
from backend.app.rag.retriever import retrieve_top_k


_settings = get_settings()
_client = genai.Client(api_key=_settings.gemini_api_key)

# Use a model that your dashboard shows quota for.
REPORT_MODEL = "gemini-2.5-flash"


def _get_document_by_ticker_and_quarter(db: Session, ticker: str, quarter: str) -> Document | None:
    stmt = (
        select(Document)
        .where(Document.ticker == ticker.upper().strip())
        .where(Document.quarter == quarter.upper().strip())
    )
    return db.scalars(stmt).first()


def _collect_context_for_report(
    db: Session,
    current_doc: Document,
    prev_doc: Document | None,
    k_per_query: int = 4,
) -> list[dict[str, Any]]:
    queries_by_theme: dict[str, list[str]] = {
        "guidance": [
            "guidance outlook",
            "revenue outlook",
            "EPS guidance",
            "full year outlook",
        ],
        "growth_drivers": [
            "growth drivers",
            "AI revenue",
            "cloud growth",
            "subscriptions growth",
        ],
        "risks": [
            "macro headwinds",
            "regulatory risk",
            "currency headwind",
            "competition",
        ],
        "margin_dynamics": [
            "operating margin",
            "margin expansion",
            "depreciation headwind",
            "cost of revenues",
        ],
        "qa_pressure_points": [
            "analyst concerns",
            "follow up question",
            "can you elaborate",
            "clarify risk",
        ],
    }

    seen_chunk_ids: set[tuple[str, str]] = set()
    context: list[dict[str, Any]] = []

    def add_chunks(chunks: list[Chunk], role: str) -> None:
        for c in chunks:
            key = (role, str(c.id))
            if key in seen_chunk_ids:
                continue
            seen_chunk_ids.add(key)
            context.append(
                {
                    "role": role,
                    "section": c.section,
                    "document_id": str(c.document_id),
                    "chunk_id": str(c.id),
                    "chunk_index": c.chunk_index,
                    "text": c.text,
                }
            )

    for theme, queries in queries_by_theme.items():
        for q in queries:
            current_chunks = retrieve_top_k(db, query=q, k=k_per_query, document_id=str(current_doc.id))
            add_chunks(current_chunks, role="current")

            if prev_doc is not None:
                prev_chunks = retrieve_top_k(db, query=q, k=k_per_query, document_id=str(prev_doc.id))
                add_chunks(prev_chunks, role="prev")

    return context


def generate_quarter_comparison_report(
    db: Session,
    ticker: str,
    quarter: str,
    prev_quarter: str | None,
) -> dict[str, Any]:
    current_doc = _get_document_by_ticker_and_quarter(db, ticker, quarter)
    if current_doc is None:
        raise ValueError("Current quarter document not found.")

    prev_doc: Document | None = None
    if prev_quarter:
        prev_doc = _get_document_by_ticker_and_quarter(db, ticker, prev_quarter)
        if prev_doc is None:
            prev_quarter = None

    context_chunks = _collect_context_for_report(db, current_doc, prev_doc)

    if len(context_chunks) == 0:
        raise RuntimeError("No context chunks retrieved. Ensure documents are embedded.")

    payload: dict[str, Any] = {
        "ticker": ticker.upper().strip(),
        "quarter": quarter.upper().strip(),
        "prev_quarter": prev_quarter.upper().strip() if prev_quarter else None,
        "context_chunks": context_chunks,
        "schema": json.loads(REPORT_JSON_SCHEMA),
    }

    instruction = BASE_REPORT_INSTRUCTIONS

    response = _client.models.generate_content(
        model=REPORT_MODEL,
        contents=[
            {
                "role": "user",
                "parts": [
                    {"text": instruction},
                    {"text": "Here is the JSON schema you must follow:"},
                    {"text": REPORT_JSON_SCHEMA},
                    {"text": "Here is the input payload with metadata and context chunks:"},
                    {"text": json.dumps(payload, ensure_ascii=False)},
                    {
                        "text": "Now produce a single JSON object that follows the schema and only uses evidence from the provided chunks. IMPORTANT: Every evidence quote must include its citation in the format: '(document_id: <id>, chunk_id: <id>, chunk_index: <num>)' at the end of the quote.",
                    },
                ],
            }
        ],
    )

    if not response.candidates:
        raise RuntimeError("Gemini returned no candidates for report generation.")

    if not response.candidates[0].content.parts:
        raise RuntimeError("Gemini response has no parts.")

    text = response.candidates[0].content.parts[0].text  # type: ignore[assignment]

    if not text or not text.strip():
        raise RuntimeError(f"Gemini returned empty text. Full response: {response}")

    raw = text.strip()
    try:
        report = json.loads(raw)
    except json.JSONDecodeError as e:
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise RuntimeError(f"Could not parse JSON from Gemini. Raw text: {raw[:500]}") from e
        inner = raw[start : end + 1]
        report = json.loads(inner)

    if not isinstance(report, dict):
        raise RuntimeError("Report is not a JSON object.")

    return report

