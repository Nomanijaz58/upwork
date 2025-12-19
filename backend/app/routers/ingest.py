from datetime import datetime, timezone
import re
from typing import Any, Optional
from xml.etree import ElementTree as ET

from fastapi import APIRouter, Depends, Header, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from ..core.settings import settings
from ..core.logging import get_logger
from ..db.mongo import get_db
from ..repositories.base import oid_str
from ..repositories.collections import JobsFilteredRepo, JobsRawRepo
from ..schemas.jobs import JobFilteredOut, JobIngestItem, JobIngestRequest, JobIngestResponse, RSSConvertRequest, UpworkJsonConvertRequest
from ..services.filter_service import FilterService
from ..services.audit import AuditService

logger = get_logger(__name__)


async def _update_feed_status(
    db: AsyncIOMotorDatabase,
    source: str,
    success: bool = True,
    new_jobs_count: int = 0,
    error: Optional[str] = None,
) -> None:
    """Update feed status after ingestion - avoids circular import."""
    from ..repositories.collections import FeedStatusRepo
    
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

logger = get_logger(__name__)


router = APIRouter(prefix="/ingest", tags=["ingest"])


def _normalize_vollna_payload(vollna_data: dict[str, Any], source: str = "vollna") -> list[JobIngestItem]:
    """
    Normalize Vollna job payload to our standard format.
    
    Handles various Vollna payload structures and converts them to JobIngestItem format.
    """
    items: list[JobIngestItem] = []
    
    # Vollna might send jobs in different formats
    jobs = None
    
    # Try to find jobs array
    if isinstance(vollna_data, list):
        jobs = vollna_data
    elif "jobs" in vollna_data:
        jobs = vollna_data["jobs"]
    elif "data" in vollna_data and isinstance(vollna_data["data"], list):
        jobs = vollna_data["data"]
    elif "items" in vollna_data:
        jobs = vollna_data["items"]
    
    if not jobs or not isinstance(jobs, list):
        raise HTTPException(
            status_code=400,
            detail="Invalid Vollna payload: expected 'jobs' array or list of jobs"
        )
    
    for idx, job in enumerate(jobs):
        if not isinstance(job, dict):
            logger.warning(f"Skipping invalid job at index {idx}: not a dict")
            continue
        
        # Extract and normalize fields
        title = (
            job.get("title") or 
            job.get("jobTitle") or 
            job.get("name") or 
            job.get("subject") or 
            ""
        ).strip()
        
        description = (
            job.get("description") or 
            job.get("snippet") or 
            job.get("body") or 
            job.get("text") or 
            ""
        ).strip()
        
        url = (
            job.get("url") or 
            job.get("jobUrl") or 
            job.get("link") or 
            job.get("ciphertext") or
            job.get("jobLink") or
            ""
        ).strip()
        
        # Normalize URL
        if url and not url.startswith("http"):
            if url.startswith("/"):
                url = f"https://www.upwork.com{url}"
            else:
                url = f"https://www.upwork.com/jobs/{url}"
        
        # Validate required fields: title, url, client_name, budget
        if not title:
            logger.warning(f"Skipping job {idx}: missing title")
            continue
        
        if not url:
            logger.warning(f"Skipping job {idx}: missing URL")
            continue
        
        # Client name validation (extracted above)
        if not client_name:
            logger.warning(f"Skipping job {idx}: missing client name")
            continue
        
        # Budget validation (extracted above)
        if budget is None:
            logger.warning(f"Skipping job {idx}: missing budget")
            continue
        
        # Validate budget is a positive number
        try:
            budget = float(budget)
            if budget < 0:
                logger.warning(f"Skipping job {idx}: invalid budget (must be positive): {budget}")
                continue
        except (ValueError, TypeError):
            logger.warning(f"Skipping job {idx}: invalid budget format: {budget}")
            continue
        
        # Extract posted_at
        posted_at = None
        date_fields = ["postedOn", "posted_at", "createdAt", "publishedAt", "date", "pubDate", "created_at"]
        for field in date_fields:
            if field in job and job[field]:
                try:
                    date_value = job[field]
                    if isinstance(date_value, (int, float)):
                        # Unix timestamp
                        if date_value > 1e12:  # milliseconds
                            posted_at = datetime.fromtimestamp(date_value / 1000, tz=timezone.utc)
                        else:  # seconds
                            posted_at = datetime.fromtimestamp(date_value, tz=timezone.utc)
                    elif isinstance(date_value, str):
                        # ISO string
                        try:
                            posted_at = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                        except ValueError:
                            pass
                    elif isinstance(date_value, datetime):
                        posted_at = date_value
                except (ValueError, TypeError, OSError):
                    pass
                if posted_at:
                    break
        
        # Extract skills
        skills = []
        skills_fields = ["skills", "categories", "tags", "expertise", "technologies"]
        for field in skills_fields:
            if field in job:
                skills_data = job[field]
                if isinstance(skills_data, list):
                    for skill in skills_data:
                        if isinstance(skill, str):
                            skills.append(skill.strip())
                        elif isinstance(skill, dict):
                            skill_name = skill.get("name") or skill.get("title") or skill.get("label")
                            if skill_name:
                                skills.append(str(skill_name).strip())
                elif isinstance(skills_data, str):
                    skills.extend([s.strip() for s in skills_data.split(",") if s.strip()])
                break
        
        # Extract client name (required)
        client_name = (
            job.get("client_name") or
            job.get("clientName") or
            (job.get("client", {}).get("name") if isinstance(job.get("client"), dict) else None) or
            (job.get("client", {}).get("clientName") if isinstance(job.get("client"), dict) else None) or
            ""
        ).strip()
        
        # Extract budget (required - normalize to float)
        budget = None
        budget_fields = ["budget", "hourlyRate", "fixedPrice", "rate", "price", "budgetValue", "budget_value"]
        for field in budget_fields:
            if field in job:
                budget_value = job[field]
                if isinstance(budget_value, (int, float)):
                    budget = float(budget_value)
                elif isinstance(budget_value, str):
                    # Try to extract number from string like "$50-$100/hour" or "$5000"
                    numbers = re.findall(r'\d+', budget_value.replace(',', ''))
                    if numbers:
                        # Take the first number or average if range
                        if len(numbers) >= 2:
                            budget = (float(numbers[0]) + float(numbers[1])) / 2
                        else:
                            budget = float(numbers[0])
                if budget:
                    break
        
        # Extract proposals count
        proposals = None
        proposal_fields = ["proposals", "proposalCount", "numProposals", "applicants", "applicantCount"]
        for field in proposal_fields:
            if field in job:
                prop_value = job[field]
                if isinstance(prop_value, (int, float)):
                    proposals = int(prop_value)
                elif isinstance(prop_value, str):
                    try:
                        proposals = int(prop_value)
                    except ValueError:
                        pass
                if proposals is not None:
                    break
        
        # Extract region
        region = None
        region_fields = ["country", "location", "region", "clientCountry", "clientLocation"]
        for field in region_fields:
            if field in job:
                region_value = job[field]
                if isinstance(region_value, str):
                    region = region_value
                elif isinstance(region_value, dict):
                    region = region_value.get("name") or region_value.get("title") or region_value.get("country")
                if region:
                    break
        
        # Extract client info
        client = {}
        if "client" in job and isinstance(job["client"], dict):
            client_data = job["client"]
            client = {
                "name": client_name,  # Ensure name is in client dict
                "payment_verified": client_data.get("paymentVerified", client_data.get("payment_verified", False)),
                "phone_verified": client_data.get("phoneVerified", client_data.get("phone_verified", False)),
                "rating": client_data.get("rating") or client_data.get("totalRating"),
                "reviews": client_data.get("reviewsCount") or client_data.get("reviews"),
                "total_spent": client_data.get("totalSpent") or client_data.get("total_spent"),
                "hiring_rate": client_data.get("hiringRate") or client_data.get("hiring_rate"),
            }
            client = {k: v for k, v in client.items() if v is not None}
        else:
            # If no client dict, create one with name
            client = {"name": client_name}
        
        # Create normalized item
        item = JobIngestItem(
            title=title,
            url=url,
            client_name=client_name,
            budget=budget if budget is not None else 0.0,  # Budget is required, default to 0 if not found
            description=description,  # Now optional
            source=source,
            region=region,
            posted_at=posted_at,
            skills=list(set(skills)),  # Remove duplicates
            proposals=proposals,
            client=client,
            raw={
                "original_vollna_payload": job,
                "vollna_source": source,
            }
        )
        
        items.append(item)
    
    return items


@router.post("/vollna", response_model=JobIngestResponse)
async def ingest_vollna_jobs(
    payload: dict[str, Any],
    db: AsyncIOMotorDatabase = Depends(get_db),
    x_n8n_secret: Optional[str] = Header(default=None, alias="X-N8N-Secret"),
    source: Optional[str] = None,
):
    """
    Accept Vollna job payloads and normalize them.
    
    This endpoint is specifically designed for Vollna integration via n8n.
    It accepts Vollna's payload format and automatically normalizes it to our standard format.
    
    Vollna Payload Format:
    - Can be a list of jobs: [{"title": "...", ...}, ...]
    - Can be {"jobs": [...]}
    - Can be {"data": [...]}
    - Can be {"items": [...]}
    
    The endpoint automatically:
    - Normalizes field names (title, description, url, budget, proposals, skills, postedOn)
    - Extracts and validates required fields
    - Deduplicates by URL
    - Tracks feed status
    - Stores in MongoDB with proper indexes
    """
    _check_n8n_secret(x_n8n_secret)
    
    # Determine source
    feed_source = source or payload.get("source") or "vollna"
    
    logger.info(f"Received Vollna payload: {len(payload) if isinstance(payload, dict) else 'list'} items")
    
    try:
        # Normalize Vollna payload
        normalized_items = _normalize_vollna_payload(payload, source=feed_source)
        
        if not normalized_items:
            raise HTTPException(
                status_code=400,
                detail="No valid jobs found in Vollna payload after normalization"
            )
        
        logger.info(f"Normalized {len(normalized_items)} jobs from Vollna payload")
        
        # Create JobIngestRequest
        ingest_request = JobIngestRequest(items=normalized_items)
        
        # Use the main ingestion logic
        result = await ingest_jobs(ingest_request, db, x_n8n_secret)
        
        logger.info(
            f"Vollna ingestion completed: source={feed_source}, "
            f"received={result.received}, inserted={result.inserted_raw}"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vollna ingestion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process Vollna payload: {str(e)}"
        )


@router.post("/upwork", response_model=JobIngestResponse)
async def ingest_upwork_jobs(
    payload: JobIngestRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    x_n8n_secret: Optional[str] = Header(default=None, alias="X-N8N-Secret"),
):
    """
    Dedicated endpoint for n8n Upwork integration.
    
    Accepts JSON only (validated by Pydantic).
    This endpoint is optimized for n8n workflows that fetch Upwork job data.
    
    Requirements:
    - Valid JSON payload
    - Each job must have: title, description, url, postedOn (optional), skills (optional)
    - Jobs are automatically deduplicated by URL
    - Feed status is tracked per source
    """
    # Reuse the main ingest_jobs logic
    return await ingest_jobs(payload, db, x_n8n_secret)


def _check_n8n_secret(x_n8n_secret: Optional[str]) -> None:
    if settings.N8N_SHARED_SECRET is None:
        return  # not enforced if not configured
    if not x_n8n_secret or x_n8n_secret != settings.N8N_SHARED_SECRET:
        raise HTTPException(status_code=401, detail="invalid n8n secret")


@router.post("/jobs", response_model=JobIngestResponse)
async def ingest_jobs(
    payload: JobIngestRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    x_n8n_secret: Optional[str] = Header(default=None, alias="X-N8N-Secret"),
):
    """
    Ingest jobs from n8n or other sources.
    
    Validates and stores jobs with:
    - Field validation (title, description, url, postedOn, skills)
    - Deduplication by URL
    - Automatic filtering
    - Feed status tracking
    """
    _check_n8n_secret(x_n8n_secret)

    raw_repo = JobsRawRepo(db)
    filtered_repo = JobsFilteredRepo(db)
    filters = FilterService(db)
    audit = AuditService(db)

    settings_doc = await filters.load_keyword_settings()
    keywords = await filters.load_keywords()
    geo = await filters.load_geo()

    received = len(payload.items)
    inserted_raw = 0
    inserted_filtered = 0
    deduped = 0
    errors: list[str] = []
    sources_seen: set[str] = set()

    logger.info(f"Starting job ingestion: {received} jobs received")

    for idx, item in enumerate(payload.items):
        try:
            # Validate required fields: title, url, client_name, budget
            if not item.title or not item.title.strip():
                errors.append(f"Job {idx}: Missing or empty title")
                continue
            
            if not item.url or not item.url.strip():
                errors.append(f"Job {idx}: Missing or empty URL")
                continue
            
            # Validate URL format
            if not item.url.startswith(("http://", "https://")):
                errors.append(f"Job {idx}: Invalid URL format: {item.url}")
                continue
            
            # Validate client name
            client_name = item.client_name if hasattr(item, 'client_name') else (item.client.get("name") if item.client and isinstance(item.client, dict) else None)
            if not client_name or not str(client_name).strip():
                errors.append(f"Job {idx}: Missing or empty client name")
                continue
            
            # Validate budget
            if item.budget is None:
                errors.append(f"Job {idx}: Missing budget")
                continue
            
            if not isinstance(item.budget, (int, float)) or item.budget < 0:
                errors.append(f"Job {idx}: Invalid budget (must be a positive number): {item.budget}")
                continue
            
            # Normalize URL (remove trailing slash, etc.)
            normalized_url = item.url.rstrip("/")
            
            # Track sources
            sources_seen.add(item.source)
            
            now = datetime.utcnow()
            
            # Extract client name (from client_name field or client.name)
            client_name_value = item.client_name if hasattr(item, 'client_name') else (item.client.get("name") if item.client and isinstance(item.client, dict) else "")
            
            # Ensure client dict has name field
            client_dict = item.client.copy() if item.client else {}
            client_dict["name"] = client_name_value.strip()
            
            raw_doc = {
                "title": item.title.strip(),
                "description": (item.description or "").strip(),  # Description is now optional
                "url": normalized_url,
                "source": item.source,
                "region": item.region,
                "posted_at": item.posted_at,
                "skills": [s.strip() for s in item.skills if s and s.strip()],  # Clean skills
                "budget": float(item.budget),  # Budget is now required
                "proposals": item.proposals,  # Store proposal count if provided
                "client": client_dict,  # Client dict with name
                "raw": item.raw,
                "created_at": now,
                "updated_at": now,
                "last_seen_at": now,
            }

            raw_id: Optional[str] = None
            try:
                raw_id = await raw_repo.insert_one(raw_doc)
                inserted_raw += 1
                logger.debug(f"Inserted new job: {normalized_url}")
            except DuplicateKeyError:
                deduped += 1
                # Update last_seen_at and payload for traceability
                await raw_repo.update_one(
                    {"url": normalized_url},
                    {
                        "$set": {
                            "last_seen_at": now,
                            "updated_at": now,
                            "raw": item.raw,
                            "client": item.client,
                        }
                    }
                )
                existing = await raw_repo.find_one({"url": normalized_url})
                raw_id = oid_str(existing["_id"]) if existing else None
                logger.debug(f"Deduplicated job: {normalized_url}")

            ok_kw, reasons_kw = filters.keyword_match(item.model_dump(mode="json"), settings=settings_doc, keywords=keywords)
            ok_geo, reasons_geo = filters.geo_match(item.model_dump(mode="json"), geo)
            reasons = reasons_kw + reasons_geo

            # Log filter results for debugging
            logger.debug(
                f"Job {idx} filter check: keyword_match={ok_kw} (reasons: {reasons_kw}), "
                f"geo_match={ok_geo} (reasons: {reasons_geo}), "
                f"settings={settings_doc}, keywords_count={len(keywords)}, geo={geo}"
            )

            if ok_kw and ok_geo:
                filtered_doc = {
                    "raw_id": raw_id,
                    "title": item.title.strip(),
                    "description": item.description.strip(),
                    "url": normalized_url,
                    "source": item.source,
                    "region": item.region,
                    "posted_at": item.posted_at,
                    "skills": [s.strip() for s in item.skills if s and s.strip()],
                    "budget": item.budget,  # Store budget if provided
                    "proposals": item.proposals,  # Store proposal count if provided
                    "client": item.client,
                    "filter_reasons": reasons,
                    "metadata": {},
                    "created_at": now,
                    "updated_at": now,
                }
                # Upsert by url - fix MongoDB conflict by separating setOnInsert and set
                await filtered_repo.update_one(
                    {"url": normalized_url},
                    {
                        "$setOnInsert": {
                            k: v for k, v in filtered_doc.items() if k != "updated_at"
                        },
                        "$set": {
                            "updated_at": now,
                            "raw_id": raw_id,
                            "title": item.title.strip(),
                            "description": item.description.strip(),
                            "source": item.source,
                            "region": item.region,
                            "posted_at": item.posted_at,
                            "skills": [s.strip() for s in item.skills if s and s.strip()],
                            "budget": item.budget,
                            "proposals": item.proposals,
                            "client": item.client,
                            "filter_reasons": reasons,
                        }
                    },
                    upsert=True
                )
                inserted_filtered += 1

            await audit.log(
                action="job_ingested",
                entity="jobs_raw",
                entity_id=raw_id,
                data={
                    "url": normalized_url,
                    "passed_filters": ok_kw and ok_geo,
                    "reasons": reasons,
                }
            )
        except Exception as e:
            error_msg = f"Job {idx}: Error processing job - {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg, exc_info=True)
            continue

    # Update feed status for each source
    for source in sources_seen:
        try:
            await _update_feed_status(
                db=db,
                source=source,
                success=len(errors) == 0,
                new_jobs_count=inserted_raw,
                error="; ".join(errors) if errors else None,
            )
        except Exception as e:
            logger.error(f"Failed to update feed status for {source}: {e}")

    logger.info(
        f"Job ingestion completed: received={received}, "
        f"inserted_raw={inserted_raw}, inserted_filtered={inserted_filtered}, "
        f"deduped={deduped}, errors={len(errors)}, sources={list(sources_seen)}"
    )
    
    # Log feed health summary
    for source in sources_seen:
        source_count = await raw_repo.col.count_documents({"source": source})
        logger.info(f"Feed health - Source: {source}, Total jobs: {source_count}, New jobs this run: {inserted_raw}")

    if errors:
        logger.warning(f"Ingestion errors: {errors}")

    return JobIngestResponse(
        received=received,
        inserted_raw=inserted_raw,
        inserted_filtered=inserted_filtered,
        deduped=deduped
    )

    return JobIngestResponse(received=received, inserted_raw=inserted_raw, inserted_filtered=inserted_filtered, deduped=deduped)


@router.get("/jobs/filtered", response_model=list[JobFilteredOut])
async def list_filtered_jobs(db: AsyncIOMotorDatabase = Depends(get_db), skip: int = 0, limit: int = 50):
    repo = JobsFilteredRepo(db)
    docs = await repo.find_many({}, skip=skip, limit=limit, sort=[("posted_at", -1), ("created_at", -1)])
    out: list[JobFilteredOut] = []
    for d in docs:
        out.append(
            JobFilteredOut(
                id=oid_str(d["_id"]),
                title=d.get("title") or "",
                description=d.get("description") or "",
                url=d.get("url") or "",
                source=d.get("source") or "",
                region=d.get("region"),
                posted_at=d.get("posted_at"),
                skills=d.get("skills") or [],
                filter_reasons=d.get("filter_reasons") or [],
                metadata=d.get("metadata") or {},
            )
        )
    return out


@router.post("/convert/rss")
async def convert_rss_to_api_format(payload: RSSConvertRequest):
    """
    Converts Upwork RSS XML feed to API format.
    
    Paste your Upwork RSS XML here, and it will be converted to the format
    needed for POST /ingest/jobs.
    
    Steps:
    1. Get your Upwork RSS feed URL
    2. Open it in browser and copy the XML
    3. Paste it in the rss_xml field below
    4. Execute to get converted JSON
    5. Use the result in POST /ingest/jobs
    
    Returns:
        JSON payload ready for POST /ingest/jobs
    """
    rss_xml = payload.rss_xml
    source = payload.source
    from email.utils import parsedate_to_datetime
    
    try:
        root = ET.fromstring(rss_xml)
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Invalid RSS XML: {str(e)}")
    
    items = []
    namespace = {'rss': 'http://www.w3.org/2005/Atom', 'default': 'http://purl.org/rss/1.0/'}
    
    # Try different RSS formats
    rss_items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
    
    for item in rss_items:
        # Extract title
        title_elem = item.find('title') or item.find('{http://www.w3.org/2005/Atom}title')
        title = title_elem.text if title_elem is not None and title_elem.text else ""
        
        # Extract description
        desc_elem = item.find('description') or item.find('{http://www.w3.org/2005/Atom}summary') or item.find('{http://purl.org/rss/1.0/}description')
        description = ""
        if desc_elem is not None:
            if desc_elem.text:
                description = desc_elem.text
            elif desc_elem.find('{http://www.w3.org/1999/xhtml}div') is not None:
                description = ET.tostring(desc_elem.find('{http://www.w3.org/1999/xhtml}div'), encoding='unicode', method='text')
        
        # Clean HTML tags from description
        description = re.sub(r'<[^>]+>', '', description)
        description = description.replace('&nbsp;', ' ').replace('&amp;', '&').strip()
        
        # Extract URL
        link_elem = item.find('link') or item.find('{http://www.w3.org/2005/Atom}link')
        url = ""
        if link_elem is not None:
            url = link_elem.text if link_elem.text else link_elem.get('href', '')
        
        # Extract date
        date_elem = item.find('pubDate') or item.find('published') or item.find('{http://www.w3.org/2005/Atom}published')
        posted_at = None
        if date_elem is not None and date_elem.text:
            try:
                dt = parsedate_to_datetime(date_elem.text)
                posted_at = dt.isoformat()
            except (ValueError, TypeError):
                pass
        
        # Extract skills from categories
        skills = []
        categories = item.findall('category') or item.findall('{http://www.w3.org/2005/Atom}category')
        for cat in categories:
            if cat.text:
                skills.append(cat.text.strip())
        
        # Extract region (try to find in description or use default)
        region = "United States"  # Default, can be overridden
        
        # Build the item
        api_item = {
            "title": title,
            "description": description,
            "url": url,
            "source": source,
            "region": region,
            "posted_at": posted_at,
            "skills": skills,
            "client": {},  # RSS usually doesn't have client data
            "raw": {
                "original_rss_title": title,
                "original_rss_description": description,
                "rss_source": source
            }
        }
        
        items.append(api_item)
    
    return {"items": items}


@router.post("/convert/upwork-json")
async def convert_upwork_json_to_api_format(payload: UpworkJsonConvertRequest):
    """
    Converts Upwork's JSON job data to API format.
    
    ⚠️ IMPORTANT: Upwork discontinued RSS feeds in August 2024.
    This endpoint accepts the JSON format from Upwork's web interface.
    
    How to get Upwork JSON:
    1. Open https://www.upwork.com/nx/find-work/ in your browser
    2. Open DevTools (F12 or Right-click → Inspect)
    3. Go to Network tab
    4. Filter by "XHR" or "Fetch"
    5. Refresh the page or scroll to load more jobs
    6. Look for API calls (usually contain "jobs" or "search" in URL)
    7. Click on a response → Preview or Response tab
    8. Copy the entire JSON object
    9. Paste it in the upwork_json field below
    
    Common Upwork API endpoints:
    - /api/profiles/v2/search/jobs
    - /api/jobs/v2/jobs/search
    - /ab/jobs/search
    
    Returns:
        JSON payload ready for POST /ingest/jobs
    """
    upwork_data = payload.upwork_json
    source = payload.source
    
    items = []
    
    # Try to find jobs in various possible JSON structures
    jobs = None
    
    # Common structure 1: { "jobs": [...] }
    if "jobs" in upwork_data and isinstance(upwork_data["jobs"], list):
        jobs = upwork_data["jobs"]
    # Common structure 2: { "results": { "jobs": [...] } }
    elif "results" in upwork_data and isinstance(upwork_data["results"], dict):
        if "jobs" in upwork_data["results"] and isinstance(upwork_data["results"]["jobs"], list):
            jobs = upwork_data["results"]["jobs"]
        elif "data" in upwork_data["results"] and isinstance(upwork_data["results"]["data"], list):
            jobs = upwork_data["results"]["data"]
    # Common structure 3: { "data": { "jobs": [...] } }
    elif "data" in upwork_data and isinstance(upwork_data["data"], dict):
        if "jobs" in upwork_data["data"] and isinstance(upwork_data["data"]["jobs"], list):
            jobs = upwork_data["data"]["jobs"]
    # Common structure 4: Direct array
    elif isinstance(upwork_data, list):
        jobs = upwork_data
    # Common structure 5: { "searchResults": { "jobs": [...] } }
    elif "searchResults" in upwork_data and isinstance(upwork_data["searchResults"], dict):
        if "jobs" in upwork_data["searchResults"]:
            jobs = upwork_data["searchResults"]["jobs"]
    
    if jobs is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not find job listings in the provided JSON. "
                "Expected structure: { 'jobs': [...] } or { 'results': { 'jobs': [...] } } or similar. "
                "Please check the Upwork JSON response structure."
            )
        )
    
    for job in jobs:
        if not isinstance(job, dict):
            continue
        
        # Extract title - try multiple possible field names
        title = (
            job.get("title") or 
            job.get("jobTitle") or 
            job.get("name") or 
            job.get("subject") or 
            ""
        )
        
        # Extract description - try multiple possible field names
        description = (
            job.get("description") or 
            job.get("snippet") or 
            job.get("body") or 
            job.get("text") or 
            ""
        )
        
        # Clean HTML from description if present
        if description:
            description = re.sub(r'<[^>]+>', '', description)
            description = description.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').strip()
        
        # Extract URL - try multiple possible field names
        url = (
            job.get("url") or 
            job.get("jobUrl") or 
            job.get("link") or 
            job.get("ciphertext") or
            ""
        )
        
        # If URL is relative, make it absolute
        if url and not url.startswith("http"):
            if url.startswith("/"):
                url = f"https://www.upwork.com{url}"
            else:
                url = f"https://www.upwork.com/jobs/{url}"
        
        # Extract posted_at - try multiple possible field names and formats
        posted_at = None
        date_fields = ["postedOn", "createdAt", "publishedAt", "date", "pubDate", "posted_at", "created_at"]
        for field in date_fields:
            if field in job and job[field]:
                try:
                    date_value = job[field]
                    # Handle Unix timestamp (milliseconds or seconds)
                    if isinstance(date_value, (int, float)):
                        if date_value > 1e12:  # milliseconds
                            posted_at = datetime.fromtimestamp(date_value / 1000, tz=timezone.utc).isoformat()
                        else:  # seconds
                            posted_at = datetime.fromtimestamp(date_value, tz=timezone.utc).isoformat()
                    # Handle ISO string
                    elif isinstance(date_value, str):
                        # Try parsing ISO format
                        try:
                            dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                            posted_at = dt.isoformat()
                        except ValueError:
                            pass
                    # Handle datetime object
                    elif isinstance(date_value, datetime):
                        posted_at = date_value.isoformat()
                except (ValueError, TypeError, OSError):
                    pass
                if posted_at:
                    break
        
        # Extract skills - try multiple possible field names
        skills = []
        skills_fields = ["skills", "categories", "tags", "expertise", "technologies"]
        for field in skills_fields:
            if field in job:
                skills_data = job[field]
                if isinstance(skills_data, list):
                    for skill in skills_data:
                        if isinstance(skill, str):
                            skills.append(skill.strip())
                        elif isinstance(skill, dict):
                            # Handle { "name": "Python" } or { "title": "Python" } format
                            skill_name = skill.get("name") or skill.get("title") or skill.get("label")
                            if skill_name:
                                skills.append(str(skill_name).strip())
                elif isinstance(skills_data, str):
                    # Comma-separated string
                    skills.extend([s.strip() for s in skills_data.split(",") if s.strip()])
                break
        
        # Extract region - try multiple possible field names
        region = None
        region_fields = ["country", "location", "region", "clientCountry", "clientLocation"]
        for field in region_fields:
            if field in job:
                region_value = job[field]
                if isinstance(region_value, str):
                    region = region_value
                elif isinstance(region_value, dict):
                    region = region_value.get("name") or region_value.get("title") or region_value.get("country")
                if region:
                    break
        
        # Extract client info if available
        client = {}
        if "client" in job and isinstance(job["client"], dict):
            client_data = job["client"]
            client = {
                "payment_verified": client_data.get("paymentVerified", client_data.get("payment_verified", False)),
                "phone_verified": client_data.get("phoneVerified", client_data.get("phone_verified", False)),
                "rating": client_data.get("rating") or client_data.get("totalRating"),
                "reviews": client_data.get("reviewsCount") or client_data.get("reviews"),
                "total_spent": client_data.get("totalSpent") or client_data.get("total_spent"),
                "hiring_rate": client_data.get("hiringRate") or client_data.get("hiring_rate"),
            }
            # Remove None values
            client = {k: v for k, v in client.items() if v is not None}
        
        # Build the API item
        api_item = {
            "title": title,
            "description": description,
            "url": url,
            "source": source,
            "region": region,
            "posted_at": posted_at,
            "skills": list(set(skills)),  # Remove duplicates
            "client": client,
            "raw": {
                "original_upwork_json": job,
                "upwork_source": source
            }
        }
        
        # Only add if we have at least title and url
        if title and url:
            items.append(api_item)
    
    if not items:
        raise HTTPException(
            status_code=400,
            detail="No valid jobs found in the provided JSON. Please check the structure and ensure jobs have 'title' and 'url' fields."
        )
    
    return {"items": items}


@router.get("/test/sample-payload")
async def get_sample_payload():
    """
    Returns a sample payload that n8n/Volna can use to test the /ingest/jobs endpoint.
    Copy this JSON and use it in Swagger or your n8n workflow.
    """
    sample = {
        "items": [
            {
                "title": "Python Developer Needed for FastAPI Backend",
                "description": "Looking for an experienced Python developer to build a REST API using FastAPI. Must have experience with MongoDB, async programming, and API design. This is a long-term project.",
                "url": "https://www.upwork.com/jobs/~test_sample_001",
                "source": "my_feed",
                "region": "United States",
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "skills": ["Python", "FastAPI", "MongoDB", "REST API", "Async Programming"],
                "client": {
                    "payment_verified": True,
                    "phone_verified": True,
                    "rating": 4.8,
                    "reviews": 25,
                    "total_spent": 50000,
                    "hiring_rate": 85.5,
                    "account_age_days": 365
                },
                "raw": {
                    "budget": "$50-$100/hour",
                    "job_type": "Hourly",
                    "duration": "3-6 months",
                    "proposals": 5,
                    "interviewing": 2
                }
            },
            {
                "title": "Full Stack Developer - React and Node.js",
                "description": "Need a full stack developer for a web application. Frontend in React, backend in Node.js. Experience with TypeScript required.",
                "url": "https://www.upwork.com/jobs/~test_sample_002",
                "source": "best_match",
                "region": "Canada",
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "skills": ["React", "Node.js", "TypeScript", "Full Stack"],
                "client": {
                    "payment_verified": True,
                    "rating": 4.5,
                    "reviews": 10,
                    "total_spent": 20000
                },
                "raw": {
                    "budget": "$30-$50/hour",
                    "job_type": "Hourly"
                }
            }
        ]
    }
    return sample


