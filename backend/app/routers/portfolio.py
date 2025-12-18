from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db.mongo import get_db
from ..repositories.base import oid_str, to_object_id
from ..repositories.collections import PortfoliosRepo
from ..schemas.portfolio import PortfolioCreate, PortfolioOut, PortfolioUpdate
from ..services.audit import AuditService


router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("", response_model=PortfolioOut)
async def create_portfolio(payload: PortfolioCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = PortfoliosRepo(db)
    audit = AuditService(db)
    now = datetime.utcnow()
    doc = {**payload.model_dump(mode="json"), "created_at": now, "updated_at": now}
    _id = await repo.insert_one(doc)
    saved = await repo.find_by_id(_id)
    assert saved is not None
    await audit.log(action="portfolio_created", entity="portfolios", entity_id=_id, data={"name": saved.get("name")})
    return PortfolioOut(
        id=oid_str(saved["_id"]),
        name=saved["name"],
        is_default=saved.get("is_default", False),
        projects=saved.get("projects") or [],
        metadata=saved.get("metadata") or {},
        created_at=saved["created_at"],
        updated_at=saved["updated_at"],
    )


@router.get("", response_model=list[PortfolioOut])
async def list_portfolios(db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = PortfoliosRepo(db)
    docs = await repo.find_many({}, limit=200, sort=[("updated_at", -1)])
    return [
        PortfolioOut(
            id=oid_str(d["_id"]),
            name=d["name"],
            is_default=d.get("is_default", False),
            projects=d.get("projects") or [],
            metadata=d.get("metadata") or {},
            created_at=d.get("created_at"),
            updated_at=d.get("updated_at"),
        )
        for d in docs
    ]


@router.put("/{portfolio_id}", response_model=PortfolioOut)
async def update_portfolio(portfolio_id: str, payload: PortfolioUpdate, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = PortfoliosRepo(db)
    audit = AuditService(db)
    update = {k: v for k, v in payload.model_dump(mode="json").items() if v is not None}
    update["updated_at"] = datetime.utcnow()
    await repo.update_one({"_id": to_object_id(portfolio_id)}, {"$set": update})
    saved = await repo.find_by_id(portfolio_id)
    if not saved:
        raise HTTPException(status_code=404, detail="portfolio not found")
    await audit.log(action="portfolio_updated", entity="portfolios", entity_id=portfolio_id)
    return PortfolioOut(
        id=oid_str(saved["_id"]),
        name=saved["name"],
        is_default=saved.get("is_default", False),
        projects=saved.get("projects") or [],
        metadata=saved.get("metadata") or {},
        created_at=saved.get("created_at"),
        updated_at=saved.get("updated_at"),
    )


@router.delete("/{portfolio_id}")
async def delete_portfolio(portfolio_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = PortfoliosRepo(db)
    audit = AuditService(db)
    deleted = await repo.delete_one({"_id": to_object_id(portfolio_id)})
    if not deleted:
        raise HTTPException(status_code=404, detail="portfolio not found")
    await audit.log(action="portfolio_deleted", entity="portfolios", entity_id=portfolio_id)
    return {"deleted": True}


@router.put("/replace/{portfolio_id}", response_model=PortfolioOut)
async def replace_portfolio(portfolio_id: str, payload: PortfolioCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Replace an entire portfolio document (module 6 requirement).
    """
    repo = PortfoliosRepo(db)
    audit = AuditService(db)
    now = datetime.utcnow()
    doc = {**payload.model_dump(mode="json"), "updated_at": now}
    await repo.update_one({"_id": to_object_id(portfolio_id)}, {"$set": doc})
    saved = await repo.find_by_id(portfolio_id)
    if not saved:
        raise HTTPException(status_code=404, detail="portfolio not found")
    await audit.log(action="portfolio_replaced", entity="portfolios", entity_id=portfolio_id)
    return PortfolioOut(
        id=oid_str(saved["_id"]),
        name=saved["name"],
        is_default=saved.get("is_default", False),
        projects=saved.get("projects") or [],
        metadata=saved.get("metadata") or {},
        created_at=saved.get("created_at"),
        updated_at=saved.get("updated_at"),
    )


