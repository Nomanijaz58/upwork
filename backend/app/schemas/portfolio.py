from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class PortfolioProject(BaseModel):
    title: str
    description: Optional[str] = None
    links: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict, description="Arbitrary user fields")


class PortfolioCreate(BaseModel):
    name: str
    is_default: bool = False
    projects: list[PortfolioProject] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    is_default: Optional[bool] = None
    projects: Optional[list[PortfolioProject]] = None
    metadata: Optional[dict[str, Any]] = None


class PortfolioOut(BaseModel):
    id: str
    name: str
    is_default: bool
    projects: list[PortfolioProject]
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


