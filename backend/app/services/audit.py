from datetime import datetime
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.collections import AuditLogsRepo


class AuditService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = AuditLogsRepo(db)

    async def log(
        self,
        *,
        action: str,
        entity: Optional[str] = None,
        entity_id: Optional[str] = None,
        actor: Optional[str] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> str:
        doc = {
            "ts": datetime.utcnow(),
            "action": action,
            "entity": entity,
            "entity_id": entity_id,
            "actor": actor,
            "data": data or {},
        }
        return await self.repo.insert_one(doc)


