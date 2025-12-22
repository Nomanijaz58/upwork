"""
Simple Vollna pipeline - receive and expose all jobs without filtering.
"""
import re
from typing import Any, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, unquote
from email.utils import parsedate_to_datetime

from fastapi import APIRouter, Depends, HTTPException, Header, Request, Query
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
    
    # Log payload structure (truncate if too large, but show keys)
    if isinstance(payload, dict):
        logger.info(f"🔹 Payload keys: {list(payload.keys())}")
        # Log full payload only if it's not too large
        payload_str = str(payload)
        if len(payload_str) < 2000:
            logger.info(f"🔹 Payload received: {payload}")
        else:
            logger.info(f"🔹 Payload received (truncated): {payload_str[:500]}...")
    else:
        logger.info(f"🔹 Payload received (list with {len(payload) if isinstance(payload, list) else 'unknown'} items)")
    
    # Log headers for debugging
    headers = dict(request.headers)
    logger.debug(f"🔹 Request headers: {headers}")
    
    try:
        # Normalize payload to list of jobs
        jobs = []
        if isinstance(payload, list):
            jobs = payload
        elif isinstance(payload, dict):
            # Skip test events
            if payload.get("event") == "webhook.test":
                logger.info("Skipping test webhook event")
                return {"received": 0, "inserted": 0, "message": "Test event skipped"}
            
            # Try to find jobs array in various locations
            # Vollna sends "projects" array, not "jobs"
            if "projects" in payload:
                jobs = payload["projects"] if isinstance(payload["projects"], list) else [payload["projects"]]
            elif "jobs" in payload:
                jobs = payload["jobs"] if isinstance(payload["jobs"], list) else [payload["jobs"]]
            elif "items" in payload:
                jobs = payload["items"] if isinstance(payload["items"], list) else [payload["items"]]
            elif "data" in payload:
                # data might be a list or a dict with jobs
                data = payload["data"]
                if isinstance(data, list):
                    jobs = data
                elif isinstance(data, dict):
                    if "jobs" in data:
                        jobs = data["jobs"] if isinstance(data["jobs"], list) else [data["jobs"]]
                    elif "items" in data:
                        jobs = data["items"] if isinstance(data["items"], list) else [data["items"]]
            elif "filter" in payload:
                # Vollna might send filter metadata with jobs nested
                filter_data = payload.get("filter", {})
                if isinstance(filter_data, dict):
                    # Check if jobs are in filter object
                    if "jobs" in filter_data:
                        jobs = filter_data["jobs"] if isinstance(filter_data["jobs"], list) else [filter_data["jobs"]]
                    elif "items" in filter_data:
                        jobs = filter_data["items"] if isinstance(filter_data["items"], list) else [filter_data["items"]]
                # Also check if jobs array exists at root level alongside filter
                if "jobs" in payload and not jobs:
                    jobs = payload["jobs"] if isinstance(payload["jobs"], list) else [payload["jobs"]]
            else:
                # Check if this is a single job object (has title and url)
                if payload.get("title") or payload.get("url"):
                    jobs = [payload]
                else:
                    # Log full payload structure for debugging
                    logger.warning(f"Could not extract jobs from payload structure. Keys: {list(payload.keys())}")
                    logger.debug(f"Full payload: {payload}")
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payload type: {type(payload).__name__}. Expected dict or list."
            )
        
        if not jobs:
            logger.warning("No jobs found in payload")
            logger.warning(f"Payload structure: type={type(payload).__name__}, keys={list(payload.keys()) if isinstance(payload, dict) else 'N/A'}")
            return {"received": 0, "inserted": 0, "message": "No jobs in payload"}
        
        logger.info(f"Processing {len(jobs)} jobs from Vollna")
        # Log structure of first job to understand format
        if jobs and isinstance(jobs[0], dict):
            logger.info(f"First job structure - keys: {list(jobs[0].keys())[:15]}")
            logger.debug(f"First job sample: {str(jobs[0])[:500]}")
        
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
                
                # 🛑 Skip test messages and test jobs (already handled at payload level, but double-check)
                if job.get("event") == "webhook.test":
                    logger.info(f"Skipping test webhook payload (event: webhook.test)")
                    continue
                
                # Skip filter metadata objects (they don't have job data)
                if "filter" in job and not (job.get("title") or job.get("url")):
                    logger.debug(f"Skipping filter metadata object: {job.get('filter', {}).get('name', 'unknown')}")
                    continue
                
                # Get title (check multiple possible fields)
                job_title = job.get("title") or job.get("job_title") or job.get("name") or ""
                if "test" in str(job_title).lower():
                    logger.info(f"Skipping test job: {job_title}")
                    continue
                
                # ✅ Extract URL - handle Vollna tracking links
                job_url = job.get("url") or job.get("job_url") or job.get("link") or ""
                
                # Extract real Upwork URL from Vollna tracking links
                # Format: https://www.vollna.com/go?...&url=https%253A%2F%2Fwww.upwork.com%2Fjobs%2F~
                if job_url and "vollna.com/go" in job_url and "url=" in job_url:
                    try:
                        parsed = urlparse(job_url)
                        params = parse_qs(parsed.query)
                        if "url" in params:
                            # Double URL encoding: %253A becomes %3A becomes :
                            decoded_url = unquote(unquote(params["url"][0]))
                            job_url = decoded_url
                            logger.debug(f"Extracted Upwork URL from tracking link: {job_url[:50]}...")
                    except Exception as e:
                        logger.warning(f"Failed to extract URL from tracking link: {e}")
                        # Keep original URL if extraction fails
                
                if not job_title or not job_url:
                    # Log the actual job structure to understand what Vollna is sending
                    logger.warning(
                        f"Skipping incomplete job payload (missing title or URL): "
                        f"title={bool(job_title)}, url={bool(job_url)}, "
                        f"job_keys={list(job.keys())[:10]}, "
                        f"sample_job={str(job)[:200]}"
                    )
                    continue
                
                # Extract description - handle CDATA from RSS
                description = job.get("description") or job.get("job_description") or ""
                # Clean HTML/CDATA tags if present
                if description:
                    # Remove CDATA markers
                    description = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', description, flags=re.DOTALL)
                    # Remove HTML tags
                    description = re.sub(r'<[^>]+>', '', description)
                    # Decode HTML entities
                    description = description.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&nbsp;', ' ')
                    description = description.strip()
                
                # Extract skills from categories (RSS format)
                skills = job.get("skills") or job.get("job_skills") or []
                if not skills and "categories" in job:
                    categories = job["categories"]
                    if isinstance(categories, list):
                        skills = [cat.get("text", cat) if isinstance(cat, dict) else str(cat) for cat in categories]
                    elif isinstance(categories, str):
                        skills = [categories]
                
                # Extract budget from title if present (e.g., "Job Title (Hourly Rate: 3 - 10 USD)")
                budget = job.get("budget") or job.get("formatted_budget") or job.get("budget_value") or job.get("hourly_rate") or job.get("fixed_price") or 0.0
                if not budget or budget == 0:
                    # Try to extract from title
                    budget_match = re.search(r'\(.*?:\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)', job_title)
                    if budget_match:
                        budget = float(budget_match.group(2))  # Use max rate
                
                # Parse posted_at from various Vollna field names
                # Check multiple possible field names that Vollna might use
                posted_at = None
                time_fields = [
                    "posted_at", "posted_on", "created_at", "pubDate", "published",
                    "published_at", "published_time", "time", "published_time_ago",
                    "posted_time", "date", "timestamp", "published_date"
                ]
                
                # Try to find time field in job data
                for field in time_fields:
                    if field in job and job[field]:
                        posted_at = job[field]
                        if idx == 0:  # Log for first job only
                            logger.info(f"🔍 Found time field '{field}': {posted_at}")
                        break
                
                # Log if no time field found (first job only)
                if not posted_at and idx == 0:
                    logger.warning(f"🔍 No time field found in job. Available fields: {list(job.keys())}")
                
                # If not found in direct fields, check nested locations
                if not posted_at:
                    # Check in raw data if it exists
                    if "raw" in job and isinstance(job["raw"], dict):
                        for field in time_fields:
                            if field in job["raw"] and job["raw"][field]:
                                posted_at = job["raw"][field]
                                break
                
                # Parse the time value
                if posted_at:
                    if isinstance(posted_at, str):
                        # Try to parse relative time strings like "5h ago", "20 minutes ago", "53 seconds ago"
                        relative_time_match = re.search(r'(\d+)\s*(second|minute|hour|day|week|month|year)s?\s+ago', posted_at.lower())
                        if relative_time_match:
                            try:
                                value = int(relative_time_match.group(1))
                                unit = relative_time_match.group(2)
                                
                                # Calculate the actual datetime
                                now = datetime.utcnow()
                                if unit.startswith('second'):
                                    posted_at = (now - timedelta(seconds=value)).isoformat()
                                elif unit.startswith('minute'):
                                    posted_at = (now - timedelta(minutes=value)).isoformat()
                                elif unit.startswith('hour'):
                                    posted_at = (now - timedelta(hours=value)).isoformat()
                                elif unit.startswith('day'):
                                    posted_at = (now - timedelta(days=value)).isoformat()
                                elif unit.startswith('week'):
                                    posted_at = (now - timedelta(weeks=value)).isoformat()
                                elif unit.startswith('month'):
                                    posted_at = (now - timedelta(days=value * 30)).isoformat()
                                elif unit.startswith('year'):
                                    posted_at = (now - timedelta(days=value * 365)).isoformat()
                                else:
                                    # Fall through to standard parsing
                                    raise ValueError("Unknown time unit")
                            except Exception:
                                # If relative time parsing fails, try standard parsing
                                try:
                                    dt = parsedate_to_datetime(posted_at)
                                    posted_at = dt.isoformat()
                                except Exception:
                                    # Keep as string if all parsing fails
                                    pass
                        else:
                            # Try standard date parsing (ISO, RFC, etc.)
                            try:
                                # Try ISO format parsing first (most common for Vollna)
                                dt = datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
                                posted_at = dt.isoformat()
                                if idx == 0:
                                    logger.info(f"🔍 Parsed ISO format time: {posted_at}")
                            except Exception:
                                # Try RFC format parsing
                                try:
                                    dt = parsedate_to_datetime(posted_at)
                                    posted_at = dt.isoformat()
                                    if idx == 0:
                                        logger.info(f"🔍 Parsed RFC format time: {posted_at}")
                                except Exception as e:
                                    # Keep as string if all parsing fails
                                    if idx == 0:
                                        logger.warning(f"🔍 Failed to parse time '{posted_at}': {e}")
                                    pass
                    elif isinstance(posted_at, (int, float)):
                        # Handle Unix timestamp (milliseconds or seconds)
                        try:
                            if posted_at > 1e12:  # milliseconds
                                posted_at = datetime.fromtimestamp(posted_at / 1000).isoformat()
                            else:  # seconds
                                posted_at = datetime.fromtimestamp(posted_at).isoformat()
                        except Exception:
                            posted_at = None
                    elif isinstance(posted_at, datetime):
                        posted_at = posted_at.isoformat()
                
                # If posted_at is still None or empty after all parsing attempts, use received_at as fallback
                if not posted_at:
                    logger.debug(f"No posted_at found for job: {job_title[:50]}... Using received_at as fallback")
                    posted_at = received_at.isoformat()
                
                # Log available fields from Vollna payload (first job only to avoid spam)
                if idx == 0:
                    logger.info(f"🔍 Sample job fields from Vollna: {list(job.keys())}")
                    logger.info(f"🔍 Client data: client_name={job.get('client_name')}, client={job.get('client')}")
                    logger.info(f"🔍 Proposals data: proposals={job.get('proposals')}, proposal_count={job.get('proposal_count')}, num_proposals={job.get('num_proposals')}")
                    # Show full job structure for first job (truncated)
                    job_str = str(job)
                    if len(job_str) > 1000:
                        logger.info(f"🔍 Full job structure (truncated): {job_str[:1000]}...")
                    else:
                        logger.info(f"🔍 Full job structure: {job}")
                
                # Extract client_name - Vollna doesn't send client_name, only client_details
                # client_details contains: rank, rating, payment_method_verified, total_spent, etc., but NO name
                client_name = job.get("client_name") or (job.get("client", {}).get("name") if isinstance(job.get("client"), dict) else "") or ""
                
                # Extract client_rating from client_details if available
                client_details = job.get("client_details", {})
                client_rating_from_details = None
                if isinstance(client_details, dict):
                    client_rating_from_details = client_details.get("rating")
                
                if idx == 0:
                    logger.info(f"🔍 Extracted client_name: '{client_name}' (Vollna doesn't provide client names)")
                    logger.info(f"🔍 client_details available: {bool(client_details)}, rating: {client_rating_from_details}")
                
                # Extract proposals - Vollna does NOT send proposals/proposal_count in their payload
                proposals = job.get("proposals") or job.get("proposal_count") or job.get("num_proposals")
                if idx == 0:
                    logger.info(f"🔍 Extracted proposals: {proposals} (Vollna does NOT provide proposal counts)")
                
                # Normalize job fields to standard format
                doc = {
                    # Standard fields (map from various Vollna field names)
                    "title": job_title,
                    "url": job_url,
                    "description": description,
                    "budget": budget,
                    "budget_value": budget,
                    "client_name": client_name,  # Vollna doesn't provide this - will be empty
                    "client_rating": client_rating_from_details or job.get("client_rating") or (job.get("client", {}).get("rating") if isinstance(job.get("client"), dict) else None),
                    "client_details": client_details,  # Store full client_details for reference
                    "proposals": proposals,
                    "skills": skills if isinstance(skills, list) else (skills.split(", ") if isinstance(skills, str) else []),
                    "platform": job.get("platform") or "upwork",
                    "posted_at": posted_at,
                    "location": job.get("location") or job.get("country") or job.get("region"),
                    "job_type": job.get("job_type") or job.get("type"),
                    
                    # Preserve original client object if it exists
                    "client": job.get("client") if isinstance(job.get("client"), dict) else {},
                    
                    # Store all original fields in raw field for reference
                    "raw": job,
                }
                
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
                logger.info(f"✅ Inserted job {idx}: {doc['title'][:60]}... (URL: {doc['url'][:50]}...)")
                
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
    skip: int = Query(0, ge=0, description="Number of jobs to skip (for pagination)"),
    limit: Optional[int] = Query(None, ge=1, description="Maximum number of jobs to return (optional, returns all if not specified)"),
    include_raw: bool = Query(False, description="Include raw field (excluded by default for performance)"),
):
    """
    Get ALL jobs from vollna_jobs collection.
    
    Returns all jobs sorted by posted_at (most recent first), then created_at, then received_at.
    By default, returns all jobs. Use limit parameter to restrict the number of results.
    
    The 'raw' field is excluded by default to improve response time. Set include_raw=true to include it.
    """
    logger.info(f"GET /jobs/all - Fetching jobs (skip={skip}, limit={limit}, include_raw={include_raw})")
    
    try:
        repo = VollnaJobsRepo(db)
        
        # Get total count for pagination info
        total_count = await repo.col.count_documents({})
        
        # Build projection to exclude large 'raw' field by default for better performance
        projection = {"raw": 0} if not include_raw else {}
        
        # Find jobs, sorted by posted_at first (most recent), then fallback to created_at/received_at
        # Use posted_at for better sorting since we now have actual timestamps
        cursor = repo.col.find({}, projection).sort([
            ("posted_at", -1),  # Sort by posted_at first (actual job posting time)
            ("created_at", -1),
            ("received_at", -1),
            ("_id", -1)
        ]).skip(skip)
        
        # Apply limit only if specified, otherwise return all
        if limit is not None:
            cursor = cursor.limit(limit)
            docs = await cursor.to_list(length=limit)
        else:
            docs = await cursor.to_list(length=None)  # Return all jobs
        
        # Convert ObjectId to string for JSON serialization
        jobs = []
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            jobs.append(doc)
        
        logger.info(f"GET /jobs/all - Returning {len(jobs)} jobs (total: {total_count})")
        
        return {
            "count": len(jobs),
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "has_more": limit is not None and (skip + len(jobs)) < total_count,
            "jobs": jobs,
        }
        
    except Exception as e:
        logger.error(f"Error fetching jobs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
