from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.llm.report import generate_quarter_comparison_report
from backend.app.models import Report
from backend.app.schemas import ReportRequest, ReportResponse


router = APIRouter(prefix="", tags=["report"])
logger = logging.getLogger(__name__)


@router.get("/report/health")
def report_health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/report", response_model=ReportResponse, status_code=status.HTTP_200_OK)
def create_report(payload: ReportRequest, db: Session = Depends(get_db)) -> ReportResponse:
    try:
        ticker = payload.ticker.upper().strip()
        quarter = payload.quarter.upper().strip()
        prev_quarter = payload.prev_quarter.upper().strip() if payload.prev_quarter else None

        stmt = (
            select(Report)
            .where(Report.ticker == ticker)
            .where(Report.quarter == quarter)
            .where(Report.prev_quarter == prev_quarter)
        )
        cached = db.scalars(stmt).first()
        if cached:
            return ReportResponse(data=cached.report_data)

        data = generate_quarter_comparison_report(
            db=db,
            ticker=ticker,
            quarter=quarter,
            prev_quarter=prev_quarter,
        )

        report = Report(
            ticker=ticker,
            quarter=quarter,
            prev_quarter=prev_quarter,
            report_data=data,
        )
        db.add(report)
        db.commit()

    except ValueError as exc:
        msg = str(exc)
        if "Current quarter document not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        logger.exception("Report generation value error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {type(exc).__name__}: {msg}",
        ) from exc
    except Exception as exc:
        logger.exception("Report generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {type(exc).__name__}: {exc}",
        ) from exc

    return ReportResponse(data=data)

