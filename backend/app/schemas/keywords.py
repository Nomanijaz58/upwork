from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


KeywordMatchMode = Literal["any", "all"]
KeywordMatchLocation = Literal["title", "description", "skills"]


class KeywordCreate(BaseModel):
    term: str = Field(..., description="Keyword text")
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict, description="User-defined properties")


class KeywordUpdate(BaseModel):
    term: Optional[str] = None
    enabled: Optional[bool] = None
    metadata: Optional[dict[str, Any]] = None


class KeywordOut(BaseModel):
    id: str
    term: str
    enabled: bool
    metadata: dict[str, Any]


class KeywordSettingsUpsert(BaseModel):
    """
    Global keyword matching behavior. Stored in Mongo.
    """

    match_mode: KeywordMatchMode
    match_locations: list[KeywordMatchLocation]
    metadata: dict[str, Any] = Field(default_factory=dict)


