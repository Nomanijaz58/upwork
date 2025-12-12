from fastapi import FastAPI
from contextlib import asynccontextmanager

from .db import init_mongodb, close_mongodb
from .routes.example import router as example_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize MongoDB and Beanie
    await init_mongodb()
    yield
    # Shutdown: Close MongoDB connections
    await close_mongodb()


app = FastAPI(
    title="Upwork Automation - MongoDB with Beanie ODM",
    description="FastAPI application using Beanie ODM with PyMongo",
    version="1.0.0",
    lifespan=lifespan
)

# Include example routes
app.include_router(example_router)


# --------------------- Health Check ---------------------
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "message": "Server is running",
        "database": "MongoDB with Beanie ODM"
    }


# --------------------- Root ---------------------
@app.get("/")
async def root():
    return {
        "message": "Upwork Automation API",
        "docs": "/docs",
        "health": "/health"
    }
