from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth_routes import auth_router
from app.api.malone_routes import router as malone_router
from app.api.routes import api_router, router
from app.core.scheduler import start_scheduler
from app.core.wiring import wire_events
from app.db.session import Base, SessionLocal, engine
from app.models import legal_handbook as _legal_handbook_models  # noqa: F401 — register legal ORM tables
from app.models import ingestion_control as _ingestion_control_models  # noqa: F401 — business ingest control plane
from app.services.auth_service import ensure_seed_data
from app.services.workflow_service import ensure_workflow_seed_data
from app.utils.logger import log


APP_TITLE = "AllCare Pharmacy Runtime"
APP_VERSION = "0.6.2"


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "allcare-pharmacy-runtime",
        "version": APP_VERSION,
    }