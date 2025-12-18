from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


ProposalStatus = Literal["generated", "reviewed", "approved", "submitted", "skipped"]


class ProposalGenerateRequest(BaseModel):
    job_url: Optional[str] = None
    job_id: Optional[str] = None
    prompt_template_id: Optional[str] = None
    portfolio_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProposalGenerateResponse(BaseModel):
    proposal_id: str
    status: ProposalStatus
    model: Optional[str] = None
    token_usage: dict[str, Any] = Field(default_factory=dict)
    proposal_text: str


class ProposalStatusUpdate(BaseModel):
    status: ProposalStatus
    bd_name: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProposalOut(BaseModel):
    id: str
    job_url: str
    job_title: Optional[str] = None
    status: ProposalStatus
    proposal_text: str
    model: Optional[str] = None
    token_usage: dict[str, Any] = Field(default_factory=dict)
    prompt_template_id: Optional[str] = None
    portfolio_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


