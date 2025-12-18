from __future__ import annotations
import os

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.logging import setup_logging
from .db.mongo import close_mongo, connect_mongo
from .routers import (
    ai_router,
    config_router,
    export_router,
    feeds_router,
    ingest_router,
    jobs_router,
    portfolio_router,
    proposals_router,
    scoring_router,
    vollna_webhook_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await connect_mongo()
    yield
    await close_mongo()


app = FastAPI(
    title="Upwork Proposal Bot API",
    version="1.0.0",
    description="Production-ready, MongoDB-configurable backend for an Upwork Proposal Bot.",
    lifespan=lifespan,
)

app.include_router(config_router)
app.include_router(ingest_router)
app.include_router(jobs_router)
app.include_router(feeds_router)
app.include_router(ai_router)
app.include_router(scoring_router)
app.include_router(portfolio_router)
app.include_router(proposals_router)
app.include_router(export_router)
app.include_router(vollna_webhook_router)


@app.get("/health")
async def health():
    """
    Health check endpoint that verifies MongoDB connectivity.
    """
    from .db.mongo import mongo_db

    try:
        # Ping MongoDB to verify connection
        db = mongo_db()
        await db.client.admin.command("ping")
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }, 503


@app.get("/")
async def root():
    return {"service": "upwork-proposal-bot", "docs": "/docs", "health": "/health"}
