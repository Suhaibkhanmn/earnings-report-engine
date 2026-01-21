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
    
    settings = get_settings()
    origins = settings.cors_origins_list()
    allow_any_origin = "*" in origins

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_any_origin else origins,
        # If allowing any origin, credentials must be disabled per CORS spec.
        allow_credentials=False if allow_any_origin else True,
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

