from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class MongoId(BaseModel):
    id: str = Field(..., description="MongoDB document id as string")


class Pagination(BaseModel):
    skip: int = 0
    limit: int = 100


class Timestamped(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FlexibleDocument(BaseModel):
    """
    Generic document wrapper for configs that should be fully user-defined.
    """

    name: str = Field(..., description="Human-readable name")
    enabled: bool = True
    data: dict[str, Any] = Field(default_factory=dict, description="Arbitrary user data")


class ApiStatus(BaseModel):
    status: Literal["ok", "error"]
    message: str


