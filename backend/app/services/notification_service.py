from datetime import datetime
from typing import Any, Optional

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.collections import NotificationsRepo, ProposalsRepo


class NotificationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.notifications = NotificationsRepo(db)
        self.proposals = ProposalsRepo(db)

    async def _get_config(self) -> Optional[dict[str, Any]]:
        return await self.notifications.find_one({"_key": "notifications"})

    async def notify_proposal(self, proposal_id: str) -> dict[str, Any]:
        cfg = await self._get_config()
        if not cfg or not cfg.get("enabled", True):
            return {"sent": 0, "skipped": True, "reason": "notifications_disabled"}

        proposal = await self.proposals.find_by_id(proposal_id)
        if not proposal:
            raise RuntimeError("proposal not found")

        channels = cfg.get("channels") or []
        sent = 0

        async with httpx.AsyncClient(timeout=15) as client:
            for ch in channels:
                if not ch.get("enabled", True):
                    continue
                ctype = ch.get("type")
                conf = ch.get("config") or {}
                if ctype == "slack":
                    url = conf.get("webhook_url")
                    if not url:
                        continue
                    payload = {"text": f"Proposal generated for: {proposal.get('job_title') or proposal.get('job_url')}"}
                    await client.post(url, json=payload)
                    sent += 1
                elif ctype == "webhook":
                    url = conf.get("url")
                    if not url:
                        continue
                    await client.post(url, json={"proposal_id": proposal_id, "proposal": proposal})
                    sent += 1

        return {"sent": sent, "skipped": False}


