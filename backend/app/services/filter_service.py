from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.collections import GeoFiltersRepo, KeywordConfigRepo


class FilterService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.keywords = KeywordConfigRepo(db)
        self.geo = GeoFiltersRepo(db)

    async def load_keyword_settings(self) -> dict[str, Any]:
        doc = await self.keywords.find_one({"doc_type": "settings"})
        return doc or {}

    async def load_keywords(self) -> list[dict[str, Any]]:
        return await self.keywords.find_many({"doc_type": "keyword", "enabled": True}, limit=500)

    async def load_geo(self) -> dict[str, Any]:
        doc = await self.geo.find_one({"_key": "geo"})
        return doc or {}

    def keyword_match(self, job: dict[str, Any], *, settings: dict[str, Any], keywords: list[dict[str, Any]]) -> tuple[bool, list[str]]:
        """
        Applies keyword rules from Mongo.
        No keyword/threshold is hard-coded.
        """
        match_mode = settings.get("match_mode")
        locations = settings.get("match_locations") or []

        # If user didn't configure, we don't reject jobs based on keywords.
        if not match_mode or not locations or not keywords:
            return True, []

        haystacks: list[str] = []
        if "title" in locations:
            haystacks.append(str(job.get("title") or ""))
        if "description" in locations:
            haystacks.append(str(job.get("description") or ""))
        if "skills" in locations:
            skills = job.get("skills") or []
            haystacks.append(" ".join(str(s) for s in skills))

        blob = " \n ".join(haystacks).lower()
        terms = [str(k.get("term") or "").lower() for k in keywords if k.get("term")]

        if match_mode == "all":
            missing = [t for t in terms if t not in blob]
            if missing:
                return False, [f"missing_keywords:{missing}"]
            return True, []

        # match_mode == "any"
        if any(t in blob for t in terms):
            return True, []
        return False, ["no_keywords_matched"]

    def geo_match(self, job: dict[str, Any], geo: dict[str, Any]) -> tuple[bool, list[str]]:
        excluded = geo.get("excluded_countries") or []
        region = (job.get("region") or "").strip()
        if not excluded or not region:
            return True, []
        if region in excluded:
            return False, [f"excluded_region:{region}"]
        return True, []


