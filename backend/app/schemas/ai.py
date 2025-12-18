from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AISettingsUpsert(BaseModel):
    """
    Runtime LLM settings stored in MongoDB (model switching without code changes).
    """

    model: str
    temperature: float
    max_tokens: int
    extra: dict[str, Any] = Field(default_factory=dict, description="Any future OpenAI params")


class AISettingsOut(BaseModel):
    id: str
    model: str
    temperature: float
    max_tokens: int
    extra: dict[str, Any]
    updated_at: datetime


