"""
Simple Vollna pipeline - receive and expose all jobs without filtering.
"""
from typing import Any, Optional, Union
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db.mongo import get_db
from ..repositories.vollna_jobs import VollnaJobsRepo
from ..core.logging import get_logger

logger = get_logger(__name__)

# Use root router with no prefix to ensure it matches first
router = APIRouter(tags=["vollna-simple"])


def _check_auth(
    request: Request,
    x_n8n_secret: Optional[str] = Header(default=None, alias="X-N8N-Secret")
) -> None:
    """
    Check authentication via Bearer token (from Vollna) or X-N8N-Secret header (from n8n).
    
    Supports both:
    - Bearer Token: Authorization: Bearer <token> (Vollna uses this)
    - X-N8N-Secret header: X-N8N-Secret: <token> (n8n uses this)
    """
    from ..core.settings import settings
    
    # Get the expected token (prefer VOLLNA_BEARER_TOKEN, fallback to N8N_SHARED_SECRET)
    expected_token = settings.VOLLNA_BEARER_TOKEN or settings.N8N_SHARED_SECRET
    
    if not expected_token:
        # If no token configured, allow all requests (development mode)
        logger.warning("VOLLNA_BEARER_TOKEN and N8N_SHARED_SECRET not configured - allowing all requests")
        return
    
    # Check Bearer token (from Vollna)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        bearer_token = auth_header.replace("Bearer ", "").strip()
        if bearer_token == expected_token:
            logger.debug("✅ Bearer token authentication successful")
            return
        else:
            logger.warning(f"Invalid Bearer token provided")
            raise HTTPException(status_code=401, detail="invalid token")
    
    # Check X-N8N-Secret header (from n8n, for backward compatibility)
    if x_n8n_secret and x_n8n_secret == expected_token:
        logger.debug("✅ X-N8N-Secret authentication successful")
        return
    
    # No valid authentication found
    logger.warning(f"Authentication failed - no valid Bearer token or X-N8N-Secret provided")
    raise HTTPException(status_code=401, detail="invalid token")


@router.post("/webhook/vollna")
async def vollna_webhook(
    payload: Union[dict[str, Any], list[dict[str, Any]]],
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: None = Depends(_check_auth),
):
    """
    Webhook endpoint to receive jobs from Vollna.
    
    Accepts:
    - Single job: {"title": "...", "url": "...", ...}
    - List of jobs: [{"title": "..."}, ...]
    - Wrapped: {"jobs": [...]}
    
    Stores ALL jobs in vollna_jobs collection without filtering or modification.
    """
    # 🔹 Enhanced debug logging
    logger.info("🔹 Webhook hit! /webhook/vollna")
    logger.info(f"🔹 Payload type: {type(payload).__name__}")
    logger.info(f"🔹 Payload received: {payload}")
    
    # Log headers for debugging
    headers = dict(request.headers)
    logger.debug(f"🔹 Request headers: {headers}")
    
    try:
        # Normalize payload to list of jobs
        jobs = []
        if isinstance(payload, list):
            jobs = payload
        elif isinstance(payload, dict):
            if "jobs" in payload:
                jobs = payload["jobs"] if isinstance(payload["jobs"], list) else [payload["jobs"]]
            elif "items" in payload:
                jobs = payload["items"] if isinstance(payload["items"], list) else [payload["items"]]
            elif "data" in payload:
                jobs = payload["data"] if isinstance(payload["data"], list) else [payload["data"]]
            else:
                # Single job object
                jobs = [payload]
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payload type: {type(payload).__name__}. Expected dict or list."
            )
        
        if not jobs:
            logger.warning("No jobs found in payload")
            return {"received": 0, "inserted": 0, "message": "No jobs in payload"}
        
        logger.info(f"Processing {len(jobs)} jobs from Vollna")
        
        repo = VollnaJobsRepo(db)
        received_at = datetime.utcnow()
        inserted = 0
        errors = []
        
        for idx, job in enumerate(jobs):
            try:
                if not isinstance(job, dict):
                    errors.append(f"Job {idx}: Not a dictionary")
                    logger.warning(f"Skipping job {idx}: not a dict")
                    continue
                
                # Prepare document - store raw job with metadata
                # Only add metadata fields if they don't exist to avoid conflicts
                doc = dict(job)  # Copy all fields from Vollna as-is
                
                # Add metadata only if missing (avoid $set conflicts)
                if "source" not in doc:
                    doc["source"] = "vollna"
                if "received_at" not in doc:
                    doc["received_at"] = received_at
                if "created_at" not in doc:
                    doc["created_at"] = received_at
                
                # Insert job - use insert_one to avoid conflicts
                await repo.insert_one(doc)
                inserted += 1
                logger.debug(f"Inserted job {idx}: {job.get('title', 'No title')}")
                
            except Exception as e:
                error_msg = f"Job {idx}: Error inserting - {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg, exc_info=True)
                continue
        
        logger.info(f"Vollna webhook processed: {len(jobs)} received, {inserted} inserted, {len(errors)} errors")
        
        return {
            "received": len(jobs),
            "inserted": inserted,
            "errors": len(errors),
            "error_details": errors if errors else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Vollna webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/jobs/all")
async def get_all_jobs(
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get ALL jobs from vollna_jobs collection.
    
    Returns all jobs sorted by most recent first (created_at or received_at).
    No filtering, no pagination - returns everything.
    """
    logger.info("GET /jobs/all - Fetching all Vollna jobs")
    
    try:
        repo = VollnaJobsRepo(db)
        
        # Find all jobs, sorted by most recent first
        # Try created_at first, then received_at, then _id as fallback
        docs = await repo.col.find({}).sort([
            ("created_at", -1),
            ("received_at", -1),
            ("_id", -1)
        ]).to_list(length=None)  # No limit - get all
        
        # Convert ObjectId to string for JSON serialization
        jobs = []
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            jobs.append(doc)
        
        count = len(jobs)
        logger.info(f"GET /jobs/all - Returning {count} jobs")
        
        return {
            "count": count,
            "jobs": jobs,
        }
        
    except Exception as e:
        logger.error(f"Error fetching all jobs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
