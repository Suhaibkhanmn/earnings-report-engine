from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_settings
from backend.app.api.routes_ingest import router as ingest_router
from backend.app.api.routes_report import router as report_router
from backend.app.api.routes_rag import router as rag_router
from backend.app.api.routes_evaluation import router as evaluation_router


def create_app() -> FastAPI:
    app = FastAPI(title="Earnings Call Intelligence Engine", version="0.1.0")
 
    # For this project we keep CORS simple: allow all origins.
    # This avoids deployment/env mismatches while you're iterating.
    # If you want to lock this down later, we can re-introduce
    # environment-based origin configuration.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(ingest_router)
    app.include_router(report_router)
    app.include_router(rag_router)
    app.include_router(evaluation_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

