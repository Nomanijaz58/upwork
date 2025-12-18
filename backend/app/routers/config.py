from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db.mongo import get_db
from ..repositories.base import oid_str, to_object_id
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
)
from ..schemas.ai import AISettingsOut, AISettingsUpsert
from ..schemas.geo import GeoFiltersOut, GeoFiltersUpsert
from ..schemas.keywords import KeywordCreate, KeywordOut, KeywordSettingsUpsert, KeywordUpdate
from ..schemas.notifications import NotificationsConfigOut, NotificationsConfigUpsert
from ..schemas.prompts import PromptTemplateCreate, PromptTemplateOut, PromptTemplateUpdate
from ..schemas.rules import RulesetOut, RulesetUpsert
from ..schemas.scheduler import SchedulerConfigOut, SchedulerConfigUpsert


router = APIRouter(prefix="/config", tags=["config"])


# ---------- Keywords ----------


@router.post("/keywords", response_model=KeywordOut)
async def create_keyword(payload: KeywordCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = KeywordConfigRepo(db)
    doc = {"doc_type": "keyword", **payload.model_dump(mode="json"), "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
    _id = await repo.insert_one(doc)
    saved = await repo.find_by_id(_id)
    assert saved is not None
    return KeywordOut(id=oid_str(saved["_id"]), term=saved["term"], enabled=saved.get("enabled", True), metadata=saved.get("metadata") or {})


@router.get("/keywords", response_model=list[KeywordOut])
async def list_keywords(db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = KeywordConfigRepo(db)
    docs = await repo.find_many({"doc_type": "keyword"}, limit=1000, sort=[("term", 1)])
    return [KeywordOut(id=oid_str(d["_id"]), term=d["term"], enabled=d.get("enabled", True), metadata=d.get("metadata") or {}) for d in docs]


@router.patch("/keywords/{keyword_id}", response_model=KeywordOut)
async def update_keyword(keyword_id: str, payload: KeywordUpdate, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = KeywordConfigRepo(db)
    update = {k: v for k, v in payload.model_dump(mode="json").items() if v is not None}
    update["updated_at"] = datetime.utcnow()
    await repo.update_one({"_id": to_object_id(keyword_id)}, {"$set": update})
    doc = await repo.find_by_id(keyword_id)
    if not doc:
        raise HTTPException(status_code=404, detail="keyword not found")
    return KeywordOut(id=oid_str(doc["_id"]), term=doc["term"], enabled=doc.get("enabled", True), metadata=doc.get("metadata") or {})


@router.delete("/keywords/{keyword_id}")
async def delete_keyword(keyword_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = KeywordConfigRepo(db)
    deleted = await repo.delete_one({"_id": to_object_id(keyword_id)})
    if not deleted:
        raise HTTPException(status_code=404, detail="keyword not found")
    return {"deleted": True}


@router.put("/keywords/settings")
async def upsert_keyword_settings(payload: KeywordSettingsUpsert, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = KeywordConfigRepo(db)
    doc = {"doc_type": "settings", **payload.model_dump(mode="json"), "updated_at": datetime.utcnow()}
    await repo.update_one({"doc_type": "settings"}, {"$set": doc}, upsert=True)
    saved = await repo.find_one({"doc_type": "settings"})
    return {"id": oid_str(saved["_id"]), **payload.model_dump(mode="json")}


# ---------- Geo filters ----------


@router.put("/geo", response_model=GeoFiltersOut)
async def upsert_geo(payload: GeoFiltersUpsert, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = GeoFiltersRepo(db)
    doc = {"_key": "geo", **payload.model_dump(mode="json"), "updated_at": datetime.utcnow()}
    await repo.update_one({"_key": "geo"}, {"$set": doc}, upsert=True)
    saved = await repo.find_one({"_key": "geo"})
    assert saved is not None
    return GeoFiltersOut(id=oid_str(saved["_id"]), excluded_countries=saved.get("excluded_countries") or [], metadata=saved.get("metadata") or {})


@router.get("/geo", response_model=GeoFiltersOut)
async def get_geo(db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = GeoFiltersRepo(db)
    saved = await repo.find_one({"_key": "geo"})
    if not saved:
        raise HTTPException(status_code=404, detail="geo filters not configured")
    return GeoFiltersOut(id=oid_str(saved["_id"]), excluded_countries=saved.get("excluded_countries") or [], metadata=saved.get("metadata") or {})


# ---------- Scheduler ----------


@router.put("/scheduler", response_model=SchedulerConfigOut)
async def upsert_scheduler(payload: SchedulerConfigUpsert, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = SchedulerConfigRepo(db)
    doc = {"_key": "scheduler", **payload.model_dump(mode="json"), "updated_at": datetime.utcnow()}
    await repo.update_one({"_key": "scheduler"}, {"$set": doc}, upsert=True)
    saved = await repo.find_one({"_key": "scheduler"})
    assert saved is not None
    return SchedulerConfigOut(
        id=oid_str(saved["_id"]),
        enabled=saved.get("enabled", False),
        interval_seconds=saved["interval_seconds"],
        steps=saved.get("steps") or [],
        metadata=saved.get("metadata") or {},
    )


@router.get("/scheduler", response_model=SchedulerConfigOut)
async def get_scheduler(db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = SchedulerConfigRepo(db)
    saved = await repo.find_one({"_key": "scheduler"})
    if not saved:
        raise HTTPException(status_code=404, detail="scheduler config not configured")
    return SchedulerConfigOut(
        id=oid_str(saved["_id"]),
        enabled=saved.get("enabled", False),
        interval_seconds=saved["interval_seconds"],
        steps=saved.get("steps") or [],
        metadata=saved.get("metadata") or {},
    )


# ---------- Rulesets ----------


async def _upsert_ruleset(repo_cls, key: str, payload: RulesetUpsert, db: AsyncIOMotorDatabase):
    repo = repo_cls(db)
    doc = {"_key": key, **payload.model_dump(mode="json"), "updated_at": datetime.utcnow()}
    await repo.update_one({"_key": key}, {"$set": doc}, upsert=True)
    saved = await repo.find_one({"_key": key})
    assert saved is not None
    return saved


@router.put("/rules/client", response_model=RulesetOut)
async def upsert_client_rules(payload: RulesetUpsert, db: AsyncIOMotorDatabase = Depends(get_db)):
    saved = await _upsert_ruleset(ClientRulesRepo, "client_rules", payload, db)
    return RulesetOut(id=oid_str(saved["_id"]), enabled=saved.get("enabled", True), rules=saved.get("rules") or [], aggregation=saved.get("aggregation") or "sum", metadata=saved.get("metadata") or {})


@router.put("/rules/job", response_model=RulesetOut)
async def upsert_job_rules(payload: RulesetUpsert, db: AsyncIOMotorDatabase = Depends(get_db)):
    saved = await _upsert_ruleset(JobRulesRepo, "job_rules", payload, db)
    return RulesetOut(id=oid_str(saved["_id"]), enabled=saved.get("enabled", True), rules=saved.get("rules") or [], aggregation=saved.get("aggregation") or "sum", metadata=saved.get("metadata") or {})


@router.put("/rules/risk", response_model=RulesetOut)
async def upsert_risk_rules(payload: RulesetUpsert, db: AsyncIOMotorDatabase = Depends(get_db)):
    saved = await _upsert_ruleset(RiskRulesRepo, "risk_rules", payload, db)
    return RulesetOut(id=oid_str(saved["_id"]), enabled=saved.get("enabled", True), rules=saved.get("rules") or [], aggregation=saved.get("aggregation") or "sum", metadata=saved.get("metadata") or {})


# ---------- AI settings ----------


@router.put("/ai", response_model=AISettingsOut)
async def upsert_ai(payload: AISettingsUpsert, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = AISettingsRepo(db)
    doc = {"_key": "ai", **payload.model_dump(mode="json"), "updated_at": datetime.utcnow()}
    await repo.update_one({"_key": "ai"}, {"$set": doc}, upsert=True)
    saved = await repo.find_one({"_key": "ai"})
    assert saved is not None
    return AISettingsOut(id=oid_str(saved["_id"]), model=saved["model"], temperature=saved["temperature"], max_tokens=saved["max_tokens"], extra=saved.get("extra") or {}, updated_at=saved["updated_at"])


@router.get("/ai", response_model=AISettingsOut)
async def get_ai(db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = AISettingsRepo(db)
    saved = await repo.find_one({"_key": "ai"})
    if not saved:
        raise HTTPException(status_code=404, detail="ai settings not configured")
    return AISettingsOut(id=oid_str(saved["_id"]), model=saved["model"], temperature=saved["temperature"], max_tokens=saved["max_tokens"], extra=saved.get("extra") or {}, updated_at=saved["updated_at"])


# ---------- Prompt templates ----------


@router.post("/prompts", response_model=PromptTemplateOut)
async def create_prompt(payload: PromptTemplateCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = PromptTemplatesRepo(db)
    now = datetime.utcnow()
    doc = {**payload.model_dump(mode="json"), "created_at": now, "updated_at": now}
    _id = await repo.insert_one(doc)
    saved = await repo.find_by_id(_id)
    assert saved is not None
    return PromptTemplateOut(id=oid_str(saved["_id"]), name=saved["name"], template=saved["template"], is_default=saved.get("is_default", False), metadata=saved.get("metadata") or {}, created_at=saved["created_at"], updated_at=saved["updated_at"])


@router.get("/prompts", response_model=list[PromptTemplateOut])
async def list_prompts(db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = PromptTemplatesRepo(db)
    docs = await repo.find_many({}, limit=500, sort=[("updated_at", -1)])
    return [
        PromptTemplateOut(
            id=oid_str(d["_id"]),
            name=d["name"],
            template=d["template"],
            is_default=d.get("is_default", False),
            metadata=d.get("metadata") or {},
            created_at=d.get("created_at"),
            updated_at=d.get("updated_at"),
        )
        for d in docs
    ]


@router.patch("/prompts/{prompt_id}", response_model=PromptTemplateOut)
async def update_prompt(prompt_id: str, payload: PromptTemplateUpdate, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = PromptTemplatesRepo(db)
    update = {k: v for k, v in payload.model_dump(mode="json").items() if v is not None}
    update["updated_at"] = datetime.utcnow()
    from ..repositories.base import to_object_id

    await repo.update_one({"_id": to_object_id(prompt_id)}, {"$set": update})
    doc = await repo.find_by_id(prompt_id)
    if not doc:
        raise HTTPException(status_code=404, detail="prompt not found")
    return PromptTemplateOut(id=oid_str(doc["_id"]), name=doc["name"], template=doc["template"], is_default=doc.get("is_default", False), metadata=doc.get("metadata") or {}, created_at=doc.get("created_at"), updated_at=doc.get("updated_at"))


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = PromptTemplatesRepo(db)
    from ..repositories.base import to_object_id

    deleted = await repo.delete_one({"_id": to_object_id(prompt_id)})
    if not deleted:
        raise HTTPException(status_code=404, detail="prompt not found")
    return {"deleted": True}


# ---------- Notifications config ----------


@router.put("/notifications", response_model=NotificationsConfigOut)
async def upsert_notifications(payload: NotificationsConfigUpsert, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = NotificationsRepo(db)
    doc = {"_key": "notifications", **payload.model_dump(mode="json"), "updated_at": datetime.utcnow()}
    await repo.update_one({"_key": "notifications"}, {"$set": doc}, upsert=True)
    saved = await repo.find_one({"_key": "notifications"})
    assert saved is not None
    return NotificationsConfigOut(id=oid_str(saved["_id"]), enabled=saved.get("enabled", True), channels=saved.get("channels") or [], metadata=saved.get("metadata") or {}, updated_at=saved["updated_at"])


@router.get("/notifications", response_model=NotificationsConfigOut)
async def get_notifications(db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = NotificationsRepo(db)
    saved = await repo.find_one({"_key": "notifications"})
    if not saved:
        raise HTTPException(status_code=404, detail="notifications not configured")
    return NotificationsConfigOut(id=oid_str(saved["_id"]), enabled=saved.get("enabled", True), channels=saved.get("channels") or [], metadata=saved.get("metadata") or {}, updated_at=saved["updated_at"])


