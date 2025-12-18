from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SchedulerConfigUpsert(BaseModel):
    enabled: bool = False
    interval_seconds: int = Field(..., description="Execution interval in seconds")
    steps: list[str] = Field(default_factory=list, description="Enabled pipeline step names")
    metadata: dict[str, Any] = Field(default_factory=dict)


class SchedulerConfigOut(BaseModel):
    id: str
    enabled: bool
    interval_seconds: int
    steps: list[str]
    metadata: dict[str, Any]


