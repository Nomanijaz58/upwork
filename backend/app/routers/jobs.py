"""
Jobs router - provides endpoints for querying and filtering jobs.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db.mongo import get_db
from ..repositories.base import oid_str
from ..repositories.collections import JobsRawRepo, JobsFilteredRepo
from ..schemas.jobs import (
    JobOut, 
    JobFilterRequest, 
    JobFilterResponse, 
    JobSearchRequest, 
    JobSearchResponse, 
    JobRankRequest, 
    JobRankResponse
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/latest", response_model=list[JobOut])
async def get_latest_jobs(
    db: AsyncIOMotorDatabase = Depends(get_db),
    source: Optional[str] = Query(None, description="Filter by source (e.g., 'vollna', 'best_match')"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of jobs to return (default: 50)"),
):
    """
    Get latest jobs sorted by posted date.
    
    Returns latest jobs sorted by posted_at in descending order (newest first).
    This endpoint is designed for frontend polling every 10-15 seconds.
    
    Use this endpoint for:
    - Frontend chatbot polling for new jobs
    - Displaying latest available jobs
    - Real-time job updates
    
    Returns jobs from jobs_raw collection (all jobs, regardless of filter status).
    """
    repo = JobsRawRepo(db)
    
    query = {}
    if source:
        query["source"] = source
    
    docs = await repo.find_many(
        query,
        skip=0,
        limit=limit,
        sort=[("posted_at", -1), ("created_at", -1)]  # Newest first
    )
    
    jobs: list[JobOut] = []
    for doc in docs:
        jobs.append(
            JobOut(
                id=oid_str(doc["_id"]),
                title=doc.get("title") or "",
                description=doc.get("description") or "",
                url=doc.get("url") or "",
                source=doc.get("source") or "",
                region=doc.get("region"),
                posted_at=doc.get("posted_at"),
                skills=doc.get("skills") or [],
                budget=doc.get("budget"),
                proposals=doc.get("proposals"),
                client=doc.get("client") or {},
                created_at=doc.get("created_at") or datetime.utcnow(),
                updated_at=doc.get("updated_at") or datetime.utcnow(),
            )
        )
    
    return jobs


@router.get("", response_model=list[JobOut])
async def get_jobs(
    db: AsyncIOMotorDatabase = Depends(get_db),
    source: Optional[str] = Query(None, description="Filter by source (e.g., 'my_feed', 'best_match')"),
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of jobs to return"),
    use_filtered: bool = Query(True, description="Use filtered jobs (True) or raw jobs (False)"),
):
    """
    Get latest jobs sorted by posted_at DESC.
    
    Returns jobs from either the filtered collection (default) or raw collection.
    Jobs are sorted by posted_at in descending order (newest first).
    """
    if use_filtered:
        repo = JobsFilteredRepo(db)
    else:
        repo = JobsRawRepo(db)
    
    query = {}
    if source:
        query["source"] = source
    
    docs = await repo.find_many(
        query,
        skip=skip,
        limit=limit,
        sort=[("posted_at", -1), ("created_at", -1)]  # Newest first
    )
    
    jobs: list[JobOut] = []
    for doc in docs:
        jobs.append(
            JobOut(
                id=oid_str(doc["_id"]),
                title=doc.get("title") or "",
                description=doc.get("description") or "",
                url=doc.get("url") or "",
                source=doc.get("source") or "",
                region=doc.get("region"),
                posted_at=doc.get("posted_at"),
                skills=doc.get("skills") or [],
                budget=doc.get("budget"),
                proposals=doc.get("proposals"),
                client=doc.get("client") or {},
                created_at=doc.get("created_at") or datetime.utcnow(),
                updated_at=doc.get("updated_at") or datetime.utcnow(),
            )
        )
    
    return jobs


@router.post("/filter", response_model=JobFilterResponse)
async def filter_jobs(
    payload: JobFilterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Validate filters and return matching jobs.
    
    This endpoint allows you to test filter criteria against stored jobs
    to see how many jobs match and get sample results.
    """
    repo = JobsFilteredRepo(db)
    
    # Build query from filters
    query: dict[str, any] = {}  # type: ignore
    
    if payload.source:
        query["source"] = payload.source
    
    # Apply filters from payload
    filters = payload.filters
    
    # Skills filter
    if "skills" in filters and filters["skills"]:
        skills_list = filters["skills"] if isinstance(filters["skills"], list) else [filters["skills"]]
        query["skills"] = {"$in": skills_list}
    
    # Region filter
    if "region" in filters and filters["region"]:
        query["region"] = filters["region"]
    
    # Date range filter
    if "posted_after" in filters and filters["posted_after"]:
        if "posted_at" not in query:
            query["posted_at"] = {}
        query["posted_at"]["$gte"] = filters["posted_after"]
    
    if "posted_before" in filters and filters["posted_before"]:
        if "posted_at" not in query:
            query["posted_at"] = {}
        query["posted_at"]["$lte"] = filters["posted_before"]
    
    # Title/description search
    if "search" in filters and filters["search"]:
        search_term = filters["search"]
        query["$or"] = [
            {"title": {"$regex": search_term, "$options": "i"}},
            {"description": {"$regex": search_term, "$options": "i"}},
        ]
    
    # Count matches
    count = await repo.col.count_documents(query)
    
    # Get sample jobs
    sample_docs = await repo.find_many(
        query,
        skip=0,
        limit=payload.limit,
        sort=[("posted_at", -1)]
    )
    
    sample_jobs: list[JobOut] = []
    for doc in sample_docs:
        sample_jobs.append(
            JobOut(
                id=oid_str(doc["_id"]),
                title=doc.get("title") or "",
                description=doc.get("description") or "",
                url=doc.get("url") or "",
                source=doc.get("source") or "",
                region=doc.get("region"),
                posted_at=doc.get("posted_at"),
                skills=doc.get("skills") or [],
                budget=doc.get("budget"),
                proposals=doc.get("proposals"),
                client=doc.get("client") or {},
                created_at=doc.get("created_at") or datetime.utcnow(),
                updated_at=doc.get("updated_at") or datetime.utcnow(),
            )
        )
    
    return JobFilterResponse(
        matches=count,
        sample_jobs=sample_jobs,
        applied_filters=query
    )


@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(
    payload: JobSearchRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Search jobs with advanced filters.
    
    Returns both:
    - latest_jobs: All latest jobs from the source (from jobs_raw, no filters applied)
    - filtered_jobs: Jobs that match the applied filters (from jobs_filtered)
    
    Supports filtering by:
    - Budget range (min_budget, max_budget)
    - Maximum proposals (max_proposals)
    - Skills (job must have at least one)
    - Keywords (searches in title/description)
    - Source (best_matches, most_recent, saved_search, vollna, etc.)
    
    Results are sorted by newest first (posted_at DESC).
    """
    filtered_repo = JobsFilteredRepo(db)
    raw_repo = JobsRawRepo(db)
    
    # Build base query for source filter (applies to both latest and filtered)
    base_query: dict[str, any] = {}  # type: ignore
    if payload.source:
        base_query["source"] = payload.source
    
    # Get latest jobs from jobs_raw (all jobs from source, no filters)
    latest_query = base_query.copy()
    latest_total = await raw_repo.col.count_documents(latest_query)
    
    latest_docs = await raw_repo.find_many(
        latest_query,
        skip=payload.skip,
        limit=payload.limit,
        sort=[("posted_at", -1), ("created_at", -1)]
    )
    
    latest_jobs: list[JobOut] = []
    for doc in latest_docs:
        latest_jobs.append(
            JobOut(
                id=oid_str(doc["_id"]),
                title=doc.get("title") or "",
                description=doc.get("description") or "",
                url=doc.get("url") or "",
                source=doc.get("source") or "",
                region=doc.get("region"),
                posted_at=doc.get("posted_at"),
                skills=doc.get("skills") or [],
                budget=doc.get("budget"),
                proposals=doc.get("proposals"),
                client=doc.get("client") or {},
                created_at=doc.get("created_at") or datetime.utcnow(),
                updated_at=doc.get("updated_at") or datetime.utcnow(),
            )
        )
    
    # Build filtered query (with all filters applied)
    filtered_query = base_query.copy()
    
    # Budget filters
    if payload.min_budget is not None or payload.max_budget is not None:
        filtered_query["budget"] = {}
        if payload.min_budget is not None:
            filtered_query["budget"]["$gte"] = payload.min_budget
        if payload.max_budget is not None:
            filtered_query["budget"]["$lte"] = payload.max_budget
    
    # Proposals filter
    if payload.max_proposals is not None:
        filtered_query["proposals"] = {"$lte": payload.max_proposals}
    
    # Skills filter
    if payload.skills and len(payload.skills) > 0:
        filtered_query["skills"] = {"$in": payload.skills}
    
    # Keywords filter (search in title and description)
    if payload.keywords and len(payload.keywords) > 0:
        keyword_conditions = []
        for keyword in payload.keywords:
            keyword_conditions.append({"title": {"$regex": keyword, "$options": "i"}})
            keyword_conditions.append({"description": {"$regex": keyword, "$options": "i"}})
        
        if "$or" in filtered_query:
            # Combine with existing $or conditions
            filtered_query["$and"] = [
                {"$or": filtered_query.pop("$or")},
                {"$or": keyword_conditions}
            ]
        else:
            filtered_query["$or"] = keyword_conditions
    
    # Count filtered matches
    filtered_total = await filtered_repo.col.count_documents(filtered_query)
    
    # Get filtered jobs sorted by newest first
    filtered_docs = await filtered_repo.find_many(
        filtered_query,
        skip=payload.skip,
        limit=payload.limit,
        sort=[("posted_at", -1), ("created_at", -1)]
    )
    
    filtered_jobs: list[JobOut] = []
    for doc in filtered_docs:
        filtered_jobs.append(
            JobOut(
                id=oid_str(doc["_id"]),
                title=doc.get("title") or "",
                description=doc.get("description") or "",
                url=doc.get("url") or "",
                source=doc.get("source") or "",
                region=doc.get("region"),
                posted_at=doc.get("posted_at"),
                skills=doc.get("skills") or [],
                budget=doc.get("budget"),
                proposals=doc.get("proposals"),
                client=doc.get("client") or {},
                created_at=doc.get("created_at") or datetime.utcnow(),
                updated_at=doc.get("updated_at") or datetime.utcnow(),
            )
        )
    
    return JobSearchResponse(
        latest_jobs=latest_jobs,
        latest_jobs_count=latest_total,
        filtered_jobs=filtered_jobs,
        filtered_jobs_count=filtered_total,
        applied_filters=filtered_query
    )


@router.post("/recommend", response_model=JobRankResponse)
async def recommend_jobs(
    payload: JobSearchRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user_skills: Optional[list[str]] = None,
    prioritize_budget: bool = True,
    prioritize_low_competition: bool = True,
):
    """
    AI-powered job recommendations based on filtered search results.
    
    This endpoint:
    1. Filters jobs using the same criteria as /jobs/search
    2. Ranks filtered jobs using AI scoring
    3. Returns top recommendations with scores
    
    Use this endpoint from the chatbot to get personalized job recommendations.
    """
    # First, get filtered jobs
    search_result = await search_jobs(payload, db)
    
    if not search_result.filtered_jobs:
        return JobRankResponse(
            ranked_jobs=[],
            scoring_breakdown={
                "message": "No jobs found matching the criteria",
                "filters_applied": search_result.applied_filters
            }
        )
    
    # Extract job IDs from filtered jobs
    job_ids = [job.id for job in search_result.filtered_jobs]
    
    # Rank the jobs using AI
    rank_request = JobRankRequest(
        job_ids=job_ids,
        user_skills=user_skills or [],
        prioritize_budget=prioritize_budget,
        prioritize_low_competition=prioritize_low_competition
    )
    
    # Import and call AI ranking
    from ..routers.ai import rank_jobs
    return await rank_jobs(rank_request, db)

