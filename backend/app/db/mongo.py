from typing import AsyncGenerator, Optional
from urllib.parse import urlparse

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..core.logging import get_logger
from ..core.settings import settings


logger = get_logger(__name__)

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def _sanitize_uri_for_logging(uri: str) -> str:
    """
    Remove credentials from MongoDB URI for safe logging.
    Example: mongodb://user:pass@host:port -> mongodb://***:***@host:port
    """
    try:
        parsed = urlparse(uri)
        if parsed.username or parsed.password:
            # Replace credentials with ***
            netloc = f"***:***@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            return f"{parsed.scheme}://{netloc}"
        return uri
    except Exception:
        # If parsing fails, return a safe placeholder
        return "mongodb://***"


async def connect_mongo() -> None:
    """
    Initialize MongoDB connection using AsyncIOMotorClient.
    Compatible with MongoDB Compass local instances.
    """
    global _client, _db
    if _client is not None and _db is not None:
        logger.warning("MongoDB already connected, skipping reconnection")
        return

    try:
        # Log connection details (without credentials)
        safe_uri = _sanitize_uri_for_logging(settings.MONGODB_URI)
        logger.info(f"Connecting to MongoDB: {safe_uri}")
        logger.info(f"Database name: {settings.MONGODB_DB}")

        # Initialize client with URI (no database name in URI)
        _client = AsyncIOMotorClient(settings.MONGODB_URI)
        _db = _client[settings.MONGODB_DB]

        # Verify connection with a ping
        await _client.admin.command("ping")
        logger.info("MongoDB connection verified via ping")

        # Index bootstrap (structure only; no business values)
        # These indexes are created if collections don't exist yet
        
        # Jobs Raw collection indexes
        await _db["jobs_raw"].create_index("url", unique=True)
        await _db["jobs_raw"].create_index([("posted_at", -1)])  # For sorting by posted date
        await _db["jobs_raw"].create_index([("source", 1)])  # For filtering by source
        await _db["jobs_raw"].create_index([("created_at", -1)])  # For sorting by creation time
        await _db["jobs_raw"].create_index([("last_seen_at", -1)])  # For tracking last seen
        await _db["jobs_raw"].create_index([("budget", -1)])  # For budget filtering/sorting
        await _db["jobs_raw"].create_index([("proposals", 1)])  # For proposal count filtering
        
        # Jobs Filtered collection indexes
        await _db["jobs_filtered"].create_index("url", unique=True)
        await _db["jobs_filtered"].create_index([("posted_at", -1)])  # For sorting by posted date
        await _db["jobs_filtered"].create_index([("source", 1)])  # For filtering by source
        await _db["jobs_filtered"].create_index([("created_at", -1)])
        
        # Vollna Jobs collection indexes (simple pipeline)
        await _db["vollna_jobs"].create_index([("posted_at", -1)])  # For sorting by posted time (most important)
        await _db["vollna_jobs"].create_index([("created_at", -1)])  # For sorting by most recent
        await _db["vollna_jobs"].create_index([("received_at", -1)])  # For sorting by received time
        await _db["vollna_jobs"].create_index([("source", 1)])  # For filtering by source
        await _db["jobs_filtered"].create_index([("budget", -1)])  # For budget filtering/sorting
        await _db["jobs_filtered"].create_index([("proposals", 1)])  # For proposal count filtering
        await _db["jobs_filtered"].create_index([("skills", 1)])  # For skills filtering
        
        # Feed tracking collection (for feed status)
        await _db["feed_status"].create_index([("source", 1), ("updated_at", -1)], unique=True)
        
        # Proposals indexes
        await _db["proposals"].create_index([("job_url", 1), ("created_at", -1)])
        
        # Audit logs indexes
        await _db["audit_logs"].create_index([("ts", -1)])

        logger.info(f"MongoDB connected successfully to database '{settings.MONGODB_DB}'")

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise RuntimeError(
            f"MongoDB connection failed. "
            f"URI: {_sanitize_uri_for_logging(settings.MONGODB_URI)}, "
            f"DB: {settings.MONGODB_DB}. "
            f"Error: {str(e)}"
        ) from e


async def close_mongo() -> None:
    """Close MongoDB connection cleanly."""
    global _client, _db
    if _client is not None:
        _client.close()
        logger.info("MongoDB client closed")
    _client = None
    _db = None


def mongo_db() -> AsyncIOMotorDatabase:
    """
    Get the MongoDB database instance.
    Raises RuntimeError if not initialized.
    """
    if _db is None:
        raise RuntimeError(
            "MongoDB not initialized. Ensure the FastAPI lifespan startup event ran."
        )
    return _db


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    FastAPI dependency that yields a MongoDB database handle.
    Usage:
        @router.get("/example")
        async def example(db: AsyncIOMotorDatabase = Depends(get_db)):
            ...
    """
    yield mongo_db()


