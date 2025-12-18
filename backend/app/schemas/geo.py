from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GeoFiltersUpsert(BaseModel):
    excluded_countries: list[str] = Field(default_factory=list, description="Country names or codes")
    metadata: dict[str, Any] = Field(default_factory=dict)


class GeoFiltersOut(BaseModel):
    id: str
    excluded_countries: list[str]
    metadata: dict[str, Any]


