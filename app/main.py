from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth_routes import auth_router
from app.api.malone_routes import router as malone_router
from app.api.operations_map_routes import router as operations_map_router
from app.api.review_feedback_routes import router as review_feedback_router
from app.api.routes import api_router, router
from app.core.scheduler import start_scheduler
from app.core.wiring import wire_events
from app.db.session import Base, SessionLocal, engine
from app.models import legal_handbook as _legal_handbook_models  # noqa: F401 — register legal ORM tables
from app.models import ingestion_control as _ingestion_control_models  # noqa: F401 — business ingest control plane
from app.models import operations_map as _operations_map_models  # noqa: F401 — department intake / operations map
from app.models import review_feedback as _review_feedback_models  # noqa: F401 — human review loop
from app.models import scenario_memory as _scenario_memory_models  # noqa: F401 — scenario memory / decision trace
from app.services.auth_service import ensure_seed_data
from app.services.workflow_service import ensure_workflow_seed_data
from app.utils.logger import log


APP_TITLE = "AllCare Pharmacy Runtime"
APP_VERSION = "0.6.3"


@asynccontextmanager
async def lifespan(app: FastAPI):
    log("Starting AllCare Pharmacy runtime")
    db = None

    try:
        Base.metadata.create_all(bind=engine)
        log("Database schema initialized")

        db = SessionLocal()
        ensure_seed_data(db)
        ensure_workflow_seed_data(db)
        log("Seed data ensured")
        log("Workflow seed data ensured")

        wire_events()
        log("Event wiring initialized")

        start_scheduler()
        log("Background scheduler started")

        yield

    except Exception as exc:
        log(f"Application startup failed: {exc}")
        raise

    finally:
        if db is not None:
            db.close()
        log("Shutting down AllCare Pharmacy runtime")


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    lifespan=lifespan,
)

_cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
_extra = os.environ.get("MALONE_CORS_ORIGINS", "")
if _extra.strip():
    _cors_origins.extend([o.strip() for o in _extra.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(dict.fromkeys(_cors_origins)),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep both router names for backward compatibility.
app.include_router(router)
if api_router is not router:
    app.include_router(api_router)

app.include_router(auth_router)
app.include_router(malone_router)
app.include_router(review_feedback_router)
app.include_router(operations_map_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "allcare-pharmacy-runtime",
        "version": APP_VERSION,
    }