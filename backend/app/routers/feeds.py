"""
Feeds router - provides endpoints for feed status and management.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db.mongo import get_db
from ..repositories.collections import FeedStatusRepo, JobsRawRepo, JobsFilteredRepo
from ..schemas.jobs import FeedStatusOut

router = APIRouter(prefix="/feeds", tags=["feeds"])


async def update_feed_status(
    db: AsyncIOMotorDatabase,
    source: str,
    success: bool = True,
    new_jobs_count: int = 0,
    error: Optional[str] = None,
) -> None:
    """
    Update feed status after a fetch operation.
    Called internally by ingestion endpoints.
    """
    feed_repo = FeedStatusRepo(db)
    now = datetime.utcnow()
    
    update_doc: dict[str, any] = {  # type: ignore
        "source": source,
        "last_fetch_at": now,
        "updated_at": now,
    }
    
    if success:
        update_doc["last_successful_fetch_at"] = now
        update_doc["error_count"] = 0
        update_doc["last_error"] = None
        if new_jobs_count > 0:
            update_doc["metadata"] = {
                **update_doc.get("metadata", {}),
                "last_new_jobs": new_jobs_count,
            }
    else:
        # Increment error count
        existing = await feed_repo.find_one({"source": source})
        error_count = (existing.get("error_count", 0) if existing else 0) + 1
        update_doc["error_count"] = error_count
        update_doc["last_error"] = error
    
    await feed_repo.update_one(
        {"source": source},
        {"$set": update_doc},
        upsert=True
    )


@router.get("/status", response_model=list[FeedStatusOut])
async def get_feed_status(
    db: AsyncIOMotorDatabase = Depends(get_db),
    source: Optional[str] = Query(None, description="Filter by specific source"),
):
    """
    Get feed status for all sources or a specific source.
    
    Returns:
    - Last fetch time
    - Total job count
    - New jobs from last fetch
    - Error information
    """
    feed_repo = FeedStatusRepo(db)
    jobs_raw_repo = JobsRawRepo(db)
    
    query = {}
    if source:
        query["source"] = source
    
    feed_docs = await feed_repo.find_many(query, limit=100, sort=[("updated_at", -1)])
    
    statuses: list[FeedStatusOut] = []
    
    for feed_doc in feed_docs:
        feed_source = feed_doc.get("source", "unknown")
        
        # Count total jobs for this source
        total_jobs = await jobs_raw_repo.col.count_documents({"source": feed_source})
        
        # Get new jobs count from last fetch
        last_fetch = feed_doc.get("last_fetch_at")
        new_jobs = 0
        if last_fetch:
            new_jobs = await jobs_raw_repo.col.count_documents({
                "source": feed_source,
                "created_at": {"$gte": last_fetch}
            })
        
        statuses.append(
            FeedStatusOut(
                source=feed_source,
                last_fetch_at=feed_doc.get("last_fetch_at"),
                last_successful_fetch_at=feed_doc.get("last_successful_fetch_at"),
                total_jobs=total_jobs,
                new_jobs_last_fetch=new_jobs,
                error_count=feed_doc.get("error_count", 0),
                last_error=feed_doc.get("last_error"),
                metadata=feed_doc.get("metadata", {}),
            )
        )
    
    # If no feed status exists, return empty or create default
    if not statuses and source:
        # Return status for source even if no feed_status record exists
        total_jobs = await jobs_raw_repo.col.count_documents({"source": source})
        statuses.append(
            FeedStatusOut(
                source=source,
                total_jobs=total_jobs,
                new_jobs_last_fetch=0,
            )
        )
    
    return statuses

