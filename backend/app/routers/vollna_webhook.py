"""
Vollna webhook router - receives job alerts from Vollna extension via n8n.
"""
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.settings import settings
from ..core.logging import get_logger
from ..db.mongo import get_db
from ..routers.ingest import _normalize_vollna_payload, ingest_jobs
from ..schemas.jobs import JobIngestRequest, JobIngestResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/vollna", tags=["vollna"])


def _check_n8n_secret(x_n8n_secret: Optional[str]) -> None:
    """Check n8n shared secret for authentication."""
    if settings.N8N_SHARED_SECRET is None:
        return  # not enforced if not configured
    if not x_n8n_secret or x_n8n_secret != settings.N8N_SHARED_SECRET:
        raise HTTPException(status_code=401, detail="invalid n8n secret")


@router.post("/jobs", response_model=JobIngestResponse)
async def vollna_webhook(
    payload: dict[str, Any],
    db: AsyncIOMotorDatabase = Depends(get_db),
    x_n8n_secret: Optional[str] = Header(default=None, alias="X-N8N-Secret"),
):
    """
    Webhook endpoint for Vollna job alerts via n8n.
    
    This endpoint receives job data from Vollna extension alerts/saved searches.
    Vollna sends job payloads via n8n webhook, which then forwards to this endpoint.
    
    Expected Vollna Payload Format:
    - Single job: {"title": "...", "description": "...", "url": "...", "budget": 50, "proposals": 5, "skills": [...], "postedAt": "2025-01-15T10:00:00Z"}
    - Multiple jobs: [{"title": "...", ...}, ...]
    - Or wrapped: {"jobs": [{"title": "...", ...}]}
    
    The endpoint:
    1. Normalizes the payload to standard format
    2. Validates required fields (title, description, url)
    3. Extracts budget, proposals, skills, postedOn
    4. Deduplicates by URL
    5. Stores in MongoDB with proper indexes
    6. Returns ingestion summary
    
    Security:
    - Requires X-N8N-Secret header (configured in .env as N8N_SHARED_SECRET)
    - No Upwork credentials stored in backend
    - No scraping or login automation
    
    Workflow:
    Vollna Extension → n8n Webhook → POST /vollna/jobs → Normalize → POST /ingest/upwork → MongoDB
    """
    _check_n8n_secret(x_n8n_secret)
    
    logger.info(f"Received Vollna webhook payload: {type(payload).__name__}")
    
    try:
        # Normalize Vollna payload (handles various formats)
        normalized_items = _normalize_vollna_payload(payload, source="vollna")
        
        if not normalized_items:
            raise HTTPException(
                status_code=400,
                detail="No valid jobs found in Vollna payload after normalization. Ensure payload contains: title, description, url"
            )
        
        logger.info(f"Normalized {len(normalized_items)} jobs from Vollna webhook")
        
        # Create JobIngestRequest and use main ingestion logic
        ingest_request = JobIngestRequest(items=normalized_items)
        
        # Use the main ingestion endpoint logic
        result = await ingest_jobs(ingest_request, db, x_n8n_secret)
        
        logger.info(
            f"Vollna webhook processed: received={result.received}, "
            f"inserted_raw={result.inserted_raw}, inserted_filtered={result.inserted_filtered}, "
            f"deduped={result.deduped}"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vollna webhook processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process Vollna webhook: {str(e)}"
        )

