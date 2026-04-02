from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth_routes import auth_router
from app.api.routes import api_router, router
from app.core.scheduler import start_scheduler
from app.core.wiring import wire_events
from app.db.session import Base, SessionLocal, engine
from app.services.auth_service import ensure_seed_data
from app.utils.logger import log


@asynccontextmanager
async def lifespan(app: FastAPI):
    log("Starting AllCare Pharmacy runtime")
    try:
        Base.metadata.create_all(bind=engine)
        log("Database schema initialized")

        db = SessionLocal()
        try:
            ensure_seed_data(db)
        finally:
            db.close()

        wire_events()
        log("Event wiring initialized")

        start_scheduler()
        log("Background scheduler started")

        yield

    finally:
        log("Shutting down AllCare Pharmacy runtime")


app = FastAPI(
    title="AllCare Pharmacy Runtime",
    version="0.6.1",
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

app.include_router(router)
app.include_router(api_router)
app.include_router(auth_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "allcare-pharmacy-runtime",
        "version": "0.6.1",
    }