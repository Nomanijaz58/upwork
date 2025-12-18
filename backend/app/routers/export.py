from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db.mongo import get_db
from ..repositories.collections import JobsFilteredRepo, ProposalsRepo


router = APIRouter(prefix="/export", tags=["export"])


def _csv_stream(rows: list[dict], fieldnames: list[str]):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    buf.seek(0)
    yield buf.getvalue()


@router.get("/proposals.csv")
async def export_proposals(db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = ProposalsRepo(db)
    docs = await repo.find_many({}, limit=5000, sort=[("created_at", -1)])
    rows = []
    for d in docs:
        rows.append(
            {
                "job_url": d.get("job_url"),
                "job_title": d.get("job_title"),
                "status": d.get("status"),
                "model": d.get("model"),
                "created_at": d.get("created_at"),
                "updated_at": d.get("updated_at"),
                "proposal_text": d.get("proposal_text"),
            }
        )

    fieldnames = ["job_url", "job_title", "status", "model", "created_at", "updated_at", "proposal_text"]
    return StreamingResponse(_csv_stream(rows, fieldnames), media_type="text/csv")


@router.get("/jobs_filtered.csv")
async def export_jobs_filtered(db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = JobsFilteredRepo(db)
    docs = await repo.find_many({}, limit=5000, sort=[("created_at", -1)])
    rows = []
    for d in docs:
        rows.append(
            {
                "url": d.get("url"),
                "title": d.get("title"),
                "source": d.get("source"),
                "region": d.get("region"),
                "posted_at": d.get("posted_at"),
                "filter_reasons": d.get("filter_reasons"),
                "created_at": d.get("created_at"),
            }
        )
    fieldnames = ["url", "title", "source", "region", "posted_at", "filter_reasons", "created_at"]
    return StreamingResponse(_csv_stream(rows, fieldnames), media_type="text/csv")


