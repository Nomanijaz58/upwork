"""
Repository for vollna_jobs collection - stores raw Vollna job data.
"""
from typing import Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from .base import BaseRepository


class VollnaJobsRepo(BaseRepository):
    """Repository for vollna_jobs collection - stores all jobs from Vollna webhook."""
    collection_name = "vollna_jobs"

