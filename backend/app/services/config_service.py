from datetime import datetime
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.collections import (
    AISettingsRepo,
    ClientRulesRepo,
    GeoFiltersRepo,
    JobRulesRepo,
    KeywordConfigRepo,
    NotificationsRepo,
    PromptTemplatesRepo,
    RiskRulesRepo,
    SchedulerConfigRepo,
    SystemConfigRepo,
)


class ConfigService:
    """
    Central access to configuration stored in MongoDB.
    All business behavior should come from these collections.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.system = SystemConfigRepo(db)
        self.keywords = KeywordConfigRepo(db)
        self.geo = GeoFiltersRepo(db)
        self.scheduler = SchedulerConfigRepo(db)
        self.client_rules = ClientRulesRepo(db)
        self.job_rules = JobRulesRepo(db)
        self.risk_rules = RiskRulesRepo(db)
        self.prompts = PromptTemplatesRepo(db)
        self.ai = AISettingsRepo(db)
        self.notifications = NotificationsRepo(db)

    async def get_singleton(self, repo, key: str) -> Optional[dict[str, Any]]:
        return await repo.find_one({"_key": key})

    async def upsert_singleton(self, repo, key: str, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.utcnow()
        payload = {**payload, "_key": key, "updated_at": now}
        await repo.update_one({"_key": key}, {"$set": payload}, upsert=True)
        doc = await repo.find_one({"_key": key})
        assert doc is not None
        return doc


