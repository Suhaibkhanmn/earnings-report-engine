from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DocumentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticker: str = Field(..., min_length=1, max_length=16)
    quarter: str = Field(..., min_length=1, max_length=16)
    call_date: date | None = None
    raw_text: str | dict[str, str] = Field(..., min_length=1)

    @field_validator("raw_text", mode="before")
    @classmethod
    def unwrap_powershell_value_object(cls, v):
        if isinstance(v, dict) and "value" in v and isinstance(v["value"], str):
            return v["value"]
        return v


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ticker: str
    quarter: str
    call_date: date | None
    created_at: datetime


class DocumentDetail(DocumentOut):
    raw_text: str


class ChunkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    section: str
    speaker: str | None
    chunk_index: int
    text: str
    created_at: datetime


class RagSearchRequest(BaseModel):
    query: str
    k: int = 8
    document_id: uuid.UUID | None = None


class RagSearchChunk(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    section: str
    speaker: str | None
    text: str


class RagSearchResponse(BaseModel):
    query: str
    k: int
    results: list[RagSearchChunk]


class ReportRequest(BaseModel):
    ticker: str
    quarter: str
    prev_quarter: str | None = None


class ReportResponse(BaseModel):
    data: dict[str, object]



class EvaluationResponse(BaseModel):
    evaluation: Dict[str, Any]
    report_data: Dict[str, Any]
