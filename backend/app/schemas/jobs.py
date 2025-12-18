from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class JobIngestItem(BaseModel):
    title: str
    description: str
    url: str
    source: str
    region: Optional[str] = None
    posted_at: Optional[datetime] = None
    skills: list[str] = Field(default_factory=list)
    budget: Optional[float] = Field(None, description="Job budget in USD (hourly rate or fixed price)")
    proposals: Optional[int] = Field(None, description="Number of proposals received")
    client: dict[str, Any] = Field(default_factory=dict, description="Client metadata from feed if available")
    raw: dict[str, Any] = Field(default_factory=dict, description="Original source payload (unmodified)")


class JobIngestRequest(BaseModel):
    items: list[JobIngestItem]


class JobIngestResponse(BaseModel):
    received: int
    inserted_raw: int
    inserted_filtered: int
    deduped: int


class JobFilteredOut(BaseModel):
    id: str
    title: str
    description: str
    url: str
    source: str
    region: Optional[str] = None
    posted_at: Optional[datetime] = None
    skills: list[str]
    filter_reasons: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RSSConvertRequest(BaseModel):
    rss_xml: str = Field(..., description="The RSS XML content from Upwork feed (legacy support)")
    source: str = Field(default="my_feed", description="Source identifier (my_feed, best_match, etc.)")


class UpworkJsonConvertRequest(BaseModel):
    """
    Accepts Upwork's JSON job data format.
    
    Upwork discontinued RSS feeds in August 2024. This endpoint accepts
    the JSON format that Upwork's web interface uses.
    
    You can get this JSON by:
    1. Opening Upwork jobs page in browser
    2. Open DevTools (F12) → Network tab
    3. Filter by "XHR" or "Fetch"
    4. Look for API calls that return job listings
    5. Copy the JSON response
    """
    upwork_json: dict[str, Any] = Field(..., description="Upwork JSON response containing job listings")
    source: str = Field(default="my_feed", description="Source identifier (my_feed, best_match, etc.)")


class JobOut(BaseModel):
    """Job output model for GET /jobs endpoint"""
    id: str
    title: str
    description: str
    url: str
    source: str
    region: Optional[str] = None
    posted_at: Optional[datetime] = None
    skills: list[str] = Field(default_factory=list)
    budget: Optional[float] = Field(None, description="Job budget in USD")
    proposals: Optional[int] = Field(None, description="Number of proposals received")
    client: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class FeedStatusOut(BaseModel):
    """Feed status output model"""
    source: str
    last_fetch_at: Optional[datetime] = None
    last_successful_fetch_at: Optional[datetime] = None
    total_jobs: int
    new_jobs_last_fetch: int
    error_count: int = 0
    last_error: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class JobFilterRequest(BaseModel):
    """Job filter validation request"""
    filters: dict[str, Any] = Field(..., description="Filter criteria to validate")
    source: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100, description="Number of matching jobs to return")


class JobFilterResponse(BaseModel):
    """Job filter validation response"""
    matches: int
    sample_jobs: list[JobOut] = Field(default_factory=list)
    applied_filters: dict[str, Any]


class JobSearchRequest(BaseModel):
    """Job search request with filters"""
    min_budget: Optional[float] = Field(None, ge=0, description="Minimum budget in USD")
    max_budget: Optional[float] = Field(None, ge=0, description="Maximum budget in USD")
    max_proposals: Optional[int] = Field(None, ge=0, description="Maximum number of proposals")
    skills: Optional[list[str]] = Field(None, description="Required skills (job must have at least one)")
    keywords: Optional[list[str]] = Field(None, description="Keywords to search in title/description")
    source: Optional[str] = Field(None, description="Filter by source (best_matches, most_recent, saved_search, vollna, etc.)")
    skip: int = Field(0, ge=0, description="Number of jobs to skip")
    limit: int = Field(50, ge=1, le=200, description="Maximum number of jobs to return")


class JobSearchResponse(BaseModel):
    """Job search response"""
    total: int
    jobs: list[JobOut] = Field(default_factory=list)
    applied_filters: dict[str, Any]


class JobRankRequest(BaseModel):
    """Job ranking request"""
    job_ids: list[str] = Field(..., description="List of job IDs to rank")
    user_skills: Optional[list[str]] = Field(None, description="User's skills for relevance matching")
    prioritize_budget: bool = Field(True, description="Prioritize higher budgets")
    prioritize_low_competition: bool = Field(True, description="Prioritize jobs with fewer proposals")


class JobRankResponse(BaseModel):
    """Job ranking response"""
    ranked_jobs: list[dict[str, Any]] = Field(..., description="Ranked jobs with scores")
    scoring_breakdown: dict[str, Any] = Field(default_factory=dict, description="Scoring methodology")


class ProposalGenerateAIRequest(BaseModel):
    """AI proposal generation request with options"""
    job_id: Optional[str] = Field(None, description="Job ID from database")
    job_url: Optional[str] = Field(None, description="Job URL (alternative to job_id)")
    portfolio_id: Optional[str] = Field(None, description="Portfolio ID to use")
    tone: str = Field("professional", description="Proposal tone: professional, friendly, casual, formal")
    length: str = Field("medium", description="Proposal length: short, medium, long")
    custom_message: Optional[str] = Field(None, description="Custom message to include")
    prompt_template_id: Optional[str] = Field(None, description="Custom prompt template ID")


