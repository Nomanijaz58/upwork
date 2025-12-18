from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


ChannelType = Literal["slack", "webhook"]


class NotificationChannel(BaseModel):
    type: ChannelType
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict, description="Channel-specific config (e.g. webhook_url)")


class NotificationsConfigUpsert(BaseModel):
    enabled: bool = True
    channels: list[NotificationChannel] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class NotificationsConfigOut(BaseModel):
    id: str
    enabled: bool
    channels: list[NotificationChannel]
    metadata: dict[str, Any]
    updated_at: datetime


