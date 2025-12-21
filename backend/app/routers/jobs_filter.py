"""
Job filtering endpoint - accepts filter parameters and returns filtered jobs from Vollna.
"""
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from ..db.mongo import get_db
from ..repositories.vollna_jobs import VollnaJobsRepo
from ..core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["jobs-filter"])


class JobFilterRequest(BaseModel):
    """Filter parameters for job search."""
    # Platform
    platform: Optional[str] = Field(None, description="Platform filter (e.g., 'upwork')")
    
    # Budget
    budget_min: Optional[float] = Field(None, ge=0, description="Minimum budget")
    budget_max: Optional[float] = Field(None, ge=0, description="Maximum budget")
    budget_type: Optional[str] = Field(None, description="Budget type: 'hourly', 'fixed', or 'all'")
    
    # Keywords
    keywords: Optional[List[str]] = Field(None, description="Keywords to search in title/description")
    exclude_keywords: Optional[List[str]] = Field(None, description="Keywords to exclude")
    
    # Proposals
    proposals_min: Optional[int] = Field(None, ge=0, description="Minimum number of proposals")
    proposals_max: Optional[int] = Field(None, ge=0, description="Maximum number of proposals")
    
    # Client
    client_rating_min: Optional[float] = Field(None, ge=0, le=5, description="Minimum client rating (0-5)")
    client_verified_payment: Optional[bool] = Field(None, description="Client payment verified")
    client_verified_phone: Optional[bool] = Field(None, description="Client phone verified")
    
    # Geographic
    excluded_countries: Optional[List[str]] = Field(None, description="Countries to exclude")
    
    # Invite
    include_invite_sent: Optional[bool] = Field(None, description="Include jobs where invite is already sent")
    
    # Skills
    required_skills: Optional[List[str]] = Field(None, description="Required skills")
    
    # Date
    posted_after: Optional[datetime] = Field(None, description="Jobs posted after this date")
    posted_before: Optional[datetime] = Field(None, description="Jobs posted before this date")


@router.post("/filter/vollna")
async def filter_jobs(
    filters: JobFilterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    limit: int = Query(1000, ge=1, le=1000, description="Maximum number of jobs to return"),
):
    """
    Apply filters to jobs from Vollna and return matching jobs.
    
    This endpoint:
    1. Accepts filter parameters
    2. Queries the vollna_jobs collection
    3. Applies all specified filters
    4. Returns filtered jobs sorted by most recent first
    
    Jobs are fetched from the vollna_jobs collection (all jobs received via webhook).
    """
    logger.info(f"Filtering jobs with parameters: {filters.model_dump(exclude_none=True)}")
    
    try:
        repo = VollnaJobsRepo(db)
        
        # Build MongoDB query
        query = {}
        and_conditions = []  # All filter conditions should be ANDed together
        
        # Platform filter
        if filters.platform:
            # Check if platform field exists and matches, or if platform field doesn't exist (default to upwork)
            and_conditions.append({
                "$or": [
                    {"platform": filters.platform.lower()},
                    {"platform": {"$exists": False}}  # If no platform field, allow (defaults to upwork)
                ]
            })
        # If no platform specified, don't filter by platform (show all)
        
        # Budget filters
        budget_query = {}
        if filters.budget_min is not None:
            budget_query["$gte"] = filters.budget_min
        if filters.budget_max is not None:
            budget_query["$lte"] = filters.budget_max
        if budget_query:
            # Check both 'budget' and 'budget_value' fields - use OR within budget check
            and_conditions.append({
                "$or": [
                    {"budget": budget_query},
                    {"budget_value": budget_query},
                    {"hourly_rate": budget_query},
                    {"fixed_price": budget_query}
                ]
            })
        
        # Keywords search (in title, description, or skills)
        if filters.keywords:
            # Build OR conditions for each keyword (search in title, description, or skills)
            keyword_conditions = []
            for keyword in filters.keywords:
                keyword_conditions.extend([
                    {"title": {"$regex": keyword, "$options": "i"}},
                    {"description": {"$regex": keyword, "$options": "i"}},
                    {"skills": {"$elemMatch": {"$regex": keyword, "$options": "i"}}}  # Search in skills array
                ])
            
            and_conditions.append({
                "$or": keyword_conditions
            })
        
        # Exclude keywords
        if filters.exclude_keywords:
            exclude_regex = "|".join(filters.exclude_keywords)
            and_conditions.append({
                "$and": [
                    {"title": {"$not": {"$regex": exclude_regex, "$options": "i"}}},
                    {"description": {"$not": {"$regex": exclude_regex, "$options": "i"}}}
                ]
            })
        
        # Proposals filter
        if filters.proposals_min is not None or filters.proposals_max is not None:
            proposals_query = {}
            if filters.proposals_min is not None:
                proposals_query["$gte"] = filters.proposals_min
            if filters.proposals_max is not None:
                proposals_query["$lte"] = filters.proposals_max
            if proposals_query:
                query["proposals"] = proposals_query
        
        # Client rating
        if filters.client_rating_min is not None:
            # Check various possible field names for client rating
            and_conditions.append({
                "$or": [
                    {"client.rating": {"$gte": filters.client_rating_min}},
                    {"client_rating": {"$gte": filters.client_rating_min}},
                    {"rating": {"$gte": filters.client_rating_min}}
                ]
            })
        
        # Client verification
        if filters.client_verified_payment is not None:
            if filters.client_verified_payment:
                # If requiring verified payment, check if field exists and is true
                and_conditions.append({
                    "$or": [
                        {"client.payment_verified": True},
                        {"client_payment_verified": True},
                        {"payment_verified": True}
                    ]
                })
            else:
                # If NOT requiring verified payment, allow jobs without the field or with false
                and_conditions.append({
                    "$or": [
                        {"client.payment_verified": {"$exists": False}},
                        {"client.payment_verified": False},
                        {"client_payment_verified": {"$exists": False}},
                        {"client_payment_verified": False},
                        {"payment_verified": {"$exists": False}},
                        {"payment_verified": False}
                    ]
                })
        
        if filters.client_verified_phone is not None:
            if filters.client_verified_phone:
                # If requiring verified phone, check if field exists and is true
                and_conditions.append({
                    "$or": [
                        {"client.phone_verified": True},
                        {"client_phone_verified": True},
                        {"phone_verified": True}
                    ]
                })
            else:
                # If NOT requiring verified phone, allow jobs without the field or with false
                and_conditions.append({
                    "$or": [
                        {"client.phone_verified": {"$exists": False}},
                        {"client.phone_verified": False},
                        {"client_phone_verified": {"$exists": False}},
                        {"client_phone_verified": False},
                        {"phone_verified": {"$exists": False}},
                        {"phone_verified": False}
                    ]
                })
        
        # Geographic filters (excluded countries)
        if filters.excluded_countries:
            # Job should NOT be from excluded countries (check multiple possible fields)
            # Use $or so if any field matches excluded country, exclude the job
            # If field doesn't exist, it won't match (which is what we want)
            and_conditions.append({
                "$or": [
                    {"country": {"$exists": False}},  # No country field = allow
                    {"country": {"$nin": filters.excluded_countries}},  # Country not in excluded list
                    {"location": {"$exists": False}},  # No location field = allow
                    {"location": {"$nin": filters.excluded_countries}},  # Location not in excluded list
                    {"client.country": {"$exists": False}},  # No client.country = allow
                    {"client.country": {"$nin": filters.excluded_countries}}  # Client country not in excluded list
                ]
            })
        
        # Skills filter
        if filters.required_skills:
            query["skills"] = {"$in": filters.required_skills}
        
        # Date filters
        if filters.posted_after or filters.posted_before:
            date_query = {}
            if filters.posted_after:
                date_query["$gte"] = filters.posted_after
            if filters.posted_before:
                date_query["$lte"] = filters.posted_before
            if date_query:
                and_conditions.append({
                    "$or": [
                        {"posted_at": date_query},
                        {"posted_on": date_query},
                        {"created_at": date_query}
                    ]
                })
        
        # Invite filter (if include_invite_sent is False, exclude jobs with invite_sent=true)
        if filters.include_invite_sent is False:
            query["invite_sent"] = {"$ne": True}
        
        # Combine all AND conditions
        if and_conditions:
            if query:
                # If we have both direct query fields and AND conditions, combine them
                query["$and"] = and_conditions
            else:
                # If only AND conditions, use them directly
                if len(and_conditions) == 1:
                    query.update(and_conditions[0])
                else:
                    query["$and"] = and_conditions
        
        logger.debug(f"MongoDB query: {query}")
        
        # Execute query
        docs = await repo.col.find(query).sort([
            ("created_at", -1),
            ("received_at", -1),
            ("_id", -1)
        ]).limit(limit).to_list(length=limit)
        
        # Convert ObjectId to string
        jobs = []
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            jobs.append(doc)
        
        count = len(jobs)
        logger.info(f"Filter returned {count} jobs matching criteria")
        
        return {
            "count": count,
            "jobs": jobs,
            "filters_applied": filters.model_dump(exclude_none=True),
        }
        
    except Exception as e:
        logger.error(f"Error filtering jobs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/filter/preview")
async def preview_filters(
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get a preview of available filter options and job statistics.
    """
    try:
        repo = VollnaJobsRepo(db)
        
        # Get total count
        total_count = await repo.col.count_documents({})
        
        # Get sample jobs for preview
        sample_jobs = await repo.col.find({}).limit(10).to_list(length=10)
        
        # Extract unique values for filter suggestions
        platforms = await repo.col.distinct("platform")
        skills = await repo.col.distinct("skills")
        
        # Get budget range
        budget_stats = await repo.col.aggregate([
            {
                "$group": {
                    "_id": None,
                    "min_budget": {"$min": "$budget"},
                    "max_budget": {"$max": "$budget"},
                    "avg_budget": {"$avg": "$budget"}
                }
            }
        ]).to_list(length=1)
        
        return {
            "total_jobs": total_count,
            "available_platforms": platforms or ["upwork"],
            "available_skills": skills[:50],  # Limit to 50 most common
            "budget_range": budget_stats[0] if budget_stats else {
                "min_budget": 0,
                "max_budget": 0,
                "avg_budget": 0
            },
            "sample_jobs": len(sample_jobs)
        }
        
    except Exception as e:
        logger.error(f"Error getting filter preview: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

