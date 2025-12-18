from datetime import datetime
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.collections import AISettingsRepo, JobsFilteredRepo, PortfoliosRepo, PromptTemplatesRepo, ProposalsRepo
from ..schemas.proposals import ProposalGenerateRequest, ProposalGenerateResponse, ProposalStatus
from .openai_service import OpenAIService


class ProposalService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.jobs_filtered = JobsFilteredRepo(db)
        self.portfolios = PortfoliosRepo(db)
        self.prompts = PromptTemplatesRepo(db)
        self.ai = AISettingsRepo(db)
        self.proposals = ProposalsRepo(db)

    async def _get_ai_settings(self) -> dict[str, Any]:
        doc = await self.ai.find_one({"_key": "ai"})
        if not doc:
            raise RuntimeError("AI settings not configured in ai_settings (_key='ai')")
        return doc

    async def _get_prompt_template(self, template_id: Optional[str]) -> dict[str, Any]:
        if template_id:
            doc = await self.prompts.find_by_id(template_id)
            if not doc:
                raise RuntimeError("Prompt template not found")
            return doc
        # fallback to default
        doc = await self.prompts.find_one({"is_default": True})
        if not doc:
            raise RuntimeError("No default prompt template configured")
        return doc

    async def _get_portfolio(self, portfolio_id: Optional[str]) -> Optional[dict[str, Any]]:
        if portfolio_id:
            return await self.portfolios.find_by_id(portfolio_id)
        return await self.portfolios.find_one({"is_default": True})

    async def _get_job(self, req: ProposalGenerateRequest) -> dict[str, Any]:
        if req.job_id:
            doc = await self.jobs_filtered.find_by_id(req.job_id)
            if doc:
                return doc
        if req.job_url:
            doc = await self.jobs_filtered.find_one({"url": req.job_url})
            if doc:
                return doc
        raise RuntimeError("Job not found")

    def _render_prompt(self, *, template: str, job: dict[str, Any], portfolio: Optional[dict[str, Any]]) -> str:
        """
        No hard-coded prompt logic: we do plain string formatting with provided template.
        Users control the template in Mongo.
        """
        return template.format(job=job, portfolio=portfolio or {})

    async def generate(self, req: ProposalGenerateRequest) -> ProposalGenerateResponse:
        job = await self._get_job(req)
        prompt_doc = await self._get_prompt_template(req.prompt_template_id)
        portfolio_doc = await self._get_portfolio(req.portfolio_id)

        ai = await self._get_ai_settings()
        model = ai.get("model")
        temperature = ai.get("temperature")
        max_tokens = ai.get("max_tokens")
        extra = ai.get("extra") or {}

        if model is None or temperature is None or max_tokens is None:
            raise RuntimeError("ai_settings is missing required fields (model/temperature/max_tokens)")

        prompt = self._render_prompt(template=str(prompt_doc.get("template")), job=job, portfolio=portfolio_doc)

        client = OpenAIService()
        text, meta = await client.generate(
            model=str(model),
            temperature=float(temperature),
            max_tokens=int(max_tokens),
            prompt=prompt,
        )

        now = datetime.utcnow()
        doc = {
            "job_url": job.get("url"),
            "job_title": job.get("title"),
            "status": "generated",
            "proposal_text": text,
            "model": meta.get("model"),
            "token_usage": meta.get("usage") or {},
            "prompt_template_id": str(prompt_doc.get("_id")) if prompt_doc.get("_id") else None,
            "portfolio_id": str(portfolio_doc.get("_id")) if portfolio_doc and portfolio_doc.get("_id") else None,
            "metadata": req.metadata or {},
            "created_at": now,
            "updated_at": now,
        }
        proposal_id = await self.proposals.insert_one(doc)

        return ProposalGenerateResponse(
            proposal_id=proposal_id,
            status="generated",
            model=doc.get("model"),
            token_usage=doc.get("token_usage") or {},
            proposal_text=text,
        )


