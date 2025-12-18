from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class PromptTemplateCreate(BaseModel):
    name: str
    template: str
    is_default: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptTemplateUpdate(BaseModel):
    name: Optional[str] = None
    template: Optional[str] = None
    is_default: Optional[bool] = None
    metadata: Optional[dict[str, Any]] = None


class PromptTemplateOut(BaseModel):
    id: str
    name: str
    template: str
    is_default: bool
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


