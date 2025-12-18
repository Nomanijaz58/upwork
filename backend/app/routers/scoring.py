from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db.mongo import get_db
from ..repositories.base import oid_str
from datetime import datetime

from ..repositories.collections import JobsFilteredRepo, JobScoresRepo
from ..schemas.scoring import JobScoreOut, ScoreRequest
from ..services.scoring_service import ScoringService
from ..services.audit import AuditService


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/score", response_model=JobScoreOut)
async def score_job(payload: ScoreRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    jobs = JobsFilteredRepo(db)
    scorer = ScoringService(db)
    audit = AuditService(db)

    job = None
    job_id = None
    if payload.job_id:
        job = await jobs.find_by_id(payload.job_id)
        job_id = payload.job_id
    if job is None and payload.job_url:
        job = await jobs.find_one({"url": payload.job_url})
        job_id = oid_str(job["_id"]) if job else None

    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    result = await scorer.score_job(job)
    score_id = await scorer.persist_score(job_url=job.get("url"), job_id=job_id, result=result)

    await audit.log(action="job_scored", entity="job_scores", entity_id=score_id, data={"job_url": job.get("url"), "passed": result.passed})

    return JobScoreOut(id=score_id, job_url=job.get("url"), job_id=job_id, result=result, created_at=datetime.utcnow())


@router.get("/scores")
async def list_scores(db: AsyncIOMotorDatabase = Depends(get_db), skip: int = 0, limit: int = 50):
    repo = JobScoresRepo(db)
    docs = await repo.find_many({}, skip=skip, limit=limit, sort=[("created_at", -1)])
    for d in docs:
        d["id"] = oid_str(d["_id"])
        d.pop("_id", None)
    return docs


