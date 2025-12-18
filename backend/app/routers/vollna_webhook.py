"""
Vollna webhook router - receives job alerts from Vollna extension via n8n.
"""
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.settings import settings
from ..core.logging import get_logger
from ..db.mongo import get_db
from ..routers.ingest import _normalize_vollna_payload, ingest_jobs
from ..schemas.jobs import JobIngestRequest, JobIngestResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/vollna", tags=["vollna"])
security = HTTPBearer(auto_error=False)


def _check_auth(
    request: Request,
    x_n8n_secret: Optional[str] = Header(default=None, alias="X-N8N-Secret"),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> None:
    """Check authentication via Bearer token or X-N8N-Secret header."""
    if settings.N8N_SHARED_SECRET is None:
        return  # not enforced if not configured
    
    # Check Bearer token (from Vollna)
    if credentials and credentials.credentials:
        if credentials.credentials == settings.N8N_SHARED_SECRET:
            return
    
    # Check X-N8N-Secret header (from n8n)
    if x_n8n_secret and x_n8n_secret == settings.N8N_SHARED_SECRET:
        return
    
    # No valid authentication found
    raise HTTPException(status_code=401, detail="invalid authentication")


@router.post("/jobs", response_model=JobIngestResponse)
async def vollna_webhook(
    payload: dict[str, Any],
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    _: None = Depends(_check_auth),
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
    
    Authentication:
    - Supports Bearer Token (from Vollna): Authorization: Bearer <token>
    - Supports X-N8N-Secret header (from n8n): X-N8N-Secret: <token>
    """
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
        
        # Get auth token for ingest_jobs (it expects X-N8N-Secret header)
        # Extract from Bearer token or X-N8N-Secret header
        auth_token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            auth_token = auth_header.replace("Bearer ", "")
        else:
            auth_token = request.headers.get("X-N8N-Secret")
        
        # Use the main ingestion endpoint logic
        result = await ingest_jobs(ingest_request, db, auth_token)
        
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

