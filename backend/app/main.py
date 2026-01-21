from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes_ingest import router as ingest_router
from backend.app.api.routes_report import router as report_router
from backend.app.api.routes_rag import router as rag_router
from backend.app.api.routes_evaluation import router as evaluation_router


def create_app() -> FastAPI:
    app = FastAPI(title="Earnings Call Intelligence Engine", version="0.1.0")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
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

