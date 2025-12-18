from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


ConfidenceLevel = Literal["high", "medium", "low", "unknown"]


class ScoreRequest(BaseModel):
    job_url: Optional[str] = None
    job_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScoreResult(BaseModel):
    passed: bool
    rejection_reasons: list[str] = Field(default_factory=list)
    competition_score: Optional[float] = None
    invite_bias_risk_score: Optional[float] = None
    bidworthiness_score: Optional[float] = None
    confidence: ConfidenceLevel = "unknown"
    confidence_details: dict[str, Any] = Field(default_factory=dict)


class JobScoreOut(BaseModel):
    id: str
    job_url: str
    job_id: Optional[str] = None
    result: ScoreResult
    created_at: datetime


