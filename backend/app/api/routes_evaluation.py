from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.llm.report import generate_quarter_comparison_report
from backend.app.llm.validate import evaluate_report
from backend.app.models import Report
from backend.app.schemas import ReportRequest


router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/report", status_code=status.HTTP_200_OK)
def evaluate_report_endpoint(payload: ReportRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Generate a report and return it with evaluation metrics.
    """
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
            report_data = cached.report_data
        else:
            report_data = generate_quarter_comparison_report(
                db=db,
                ticker=ticker,
                quarter=quarter,
                prev_quarter=prev_quarter,
            )

        evaluation = evaluate_report(report_data)

        return {
            "evaluation": evaluation,
            "report_data": report_data,
        }

    except ValueError as exc:
        msg = str(exc)
        if "Current quarter document not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {type(exc).__name__}: {msg}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {type(exc).__name__}: {exc}",
        ) from exc
