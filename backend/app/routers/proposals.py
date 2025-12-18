from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db.mongo import get_db
from ..repositories.base import oid_str, to_object_id
from ..repositories.collections import ProposalsRepo
from ..schemas.proposals import ProposalGenerateRequest, ProposalGenerateResponse, ProposalOut, ProposalStatusUpdate
from ..services.audit import AuditService
from ..services.notification_service import NotificationService
from ..services.proposal_service import ProposalService


router = APIRouter(prefix="/proposals", tags=["proposals"])


@router.post("/generate", response_model=ProposalGenerateResponse)
async def generate_proposal(payload: ProposalGenerateRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    svc = ProposalService(db)
    audit = AuditService(db)
    notif = NotificationService(db)

    try:
        res = await svc.generate(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    await audit.log(action="proposal_generated", entity="proposals", entity_id=res.proposal_id, data={"job_id": payload.job_id, "job_url": payload.job_url})

    # Module 9: trigger notifications after generation (configurable).
    try:
        await notif.notify_proposal(res.proposal_id)
    except Exception:
        # notification failures should not block proposal creation
        pass

    return res


@router.get("", response_model=list[ProposalOut])
async def list_proposals(db: AsyncIOMotorDatabase = Depends(get_db), skip: int = 0, limit: int = 50):
    repo = ProposalsRepo(db)
    docs = await repo.find_many({}, skip=skip, limit=limit, sort=[("created_at", -1)])
    out: list[ProposalOut] = []
    for d in docs:
        out.append(
            ProposalOut(
                id=oid_str(d["_id"]),
                job_url=d.get("job_url") or "",
                job_title=d.get("job_title"),
                status=d.get("status") or "generated",
                proposal_text=d.get("proposal_text") or "",
                model=d.get("model"),
                token_usage=d.get("token_usage") or {},
                prompt_template_id=d.get("prompt_template_id"),
                portfolio_id=d.get("portfolio_id"),
                created_at=d.get("created_at"),
                updated_at=d.get("updated_at"),
            )
        )
    return out


@router.get("/{proposal_id}", response_model=ProposalOut)
async def get_proposal(proposal_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = ProposalsRepo(db)
    d = await repo.find_by_id(proposal_id)
    if not d:
        raise HTTPException(status_code=404, detail="proposal not found")
    return ProposalOut(
        id=oid_str(d["_id"]),
        job_url=d.get("job_url") or "",
        job_title=d.get("job_title"),
        status=d.get("status") or "generated",
        proposal_text=d.get("proposal_text") or "",
        model=d.get("model"),
        token_usage=d.get("token_usage") or {},
        prompt_template_id=d.get("prompt_template_id"),
        portfolio_id=d.get("portfolio_id"),
        created_at=d.get("created_at"),
        updated_at=d.get("updated_at"),
    )


@router.patch("/{proposal_id}/status")
async def update_proposal_status(proposal_id: str, payload: ProposalStatusUpdate, db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = ProposalsRepo(db)
    audit = AuditService(db)
    update = {"status": payload.status, "updated_at": datetime.utcnow(), "status_metadata": payload.metadata}
    await repo.update_one({"_id": to_object_id(proposal_id)}, {"$set": update})
    d = await repo.find_by_id(proposal_id)
    if not d:
        raise HTTPException(status_code=404, detail="proposal not found")
    await audit.log(action="proposal_status_updated", entity="proposals", entity_id=proposal_id, actor=payload.bd_name, data={"status": payload.status})
    return {"updated": True, "status": payload.status}


@router.post("/{proposal_id}/notify")
async def notify_proposal(proposal_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    notif = NotificationService(db)
    try:
        res = await notif.notify_proposal(proposal_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return res


