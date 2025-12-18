from datetime import datetime
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.collections import ClientRulesRepo, JobRulesRepo, JobScoresRepo, RiskRulesRepo
from ..schemas.scoring import ScoreResult
from .rule_engine import aggregate, eval_rule


class ScoringService:
    """
    DB-driven job scoring.
    All thresholds/weights come from MongoDB rule documents.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.client_rules = ClientRulesRepo(db)
        self.job_rules = JobRulesRepo(db)
        self.risk_rules = RiskRulesRepo(db)
        self.scores = JobScoresRepo(db)

    async def _load_ruleset(self, repo, key: str) -> Optional[dict[str, Any]]:
        return await repo.find_one({"_key": key})

    async def score_job(self, job: dict[str, Any]) -> ScoreResult:
        payload = {"job": job, "client": job.get("client") or {}}

        client_rs = await self._load_ruleset(self.client_rules, "client_rules") or {}
        job_rs = await self._load_ruleset(self.job_rules, "job_rules") or {}
        risk_rs = await self._load_ruleset(self.risk_rules, "risk_rules") or {}

        rejection_reasons: list[str] = []
        passed = True

        def apply_ruleset(ruleset: dict[str, Any], label: str) -> tuple[list[float], list[str], bool]:
            values: list[float] = []
            reasons: list[str] = []
            ok = True
            if not ruleset or not ruleset.get("enabled", True):
                return values, reasons, ok
            agg = ruleset.get("aggregation", "sum")
            for r_raw in ruleset.get("rules", []) or []:
                if not r_raw.get("enabled", True):
                    continue
                # Convert doc to schema-ish without enforcing fixed fields beyond Rule contract.
                from ..schemas.rules import Rule  # local import to avoid cycles

                rule = Rule(**r_raw)
                ev = eval_rule(rule, payload)
                if not ev.passed:
                    if rule.required:
                        ok = False
                    if ev.reason:
                        reasons.append(f"{label}:{ev.reason}")
                if ev.passed and rule.weight is not None:
                    values.append(float(rule.weight))
            return values, reasons, ok

        client_vals, client_reasons, client_ok = apply_ruleset(client_rs, "client")
        job_vals, job_reasons, job_ok = apply_ruleset(job_rs, "job")
        risk_vals, risk_reasons, risk_ok = apply_ruleset(risk_rs, "risk")

        if not client_ok or not job_ok or not risk_ok:
            passed = False

        rejection_reasons.extend(client_reasons)
        rejection_reasons.extend(job_reasons)
        rejection_reasons.extend(risk_reasons)

        # Scores are aggregated weights (fully configurable in DB).
        competition_score = aggregate(job_vals, (job_rs.get("aggregation") or "sum"))
        invite_bias_risk_score = aggregate(risk_vals, (risk_rs.get("aggregation") or "sum"))
        bidworthiness_score = aggregate(client_vals, (client_rs.get("aggregation") or "sum")) + competition_score

        # Confidence: if user didn't configure, we return unknown + details only.
        # Users can build their own confidence rules in Mongo via system_config if desired.
        confidence_details = {
            "missing_client_fields": [],
            "missing_job_fields": [],
        }

        return ScoreResult(
            passed=passed,
            rejection_reasons=rejection_reasons,
            competition_score=competition_score,
            invite_bias_risk_score=invite_bias_risk_score,
            bidworthiness_score=bidworthiness_score,
            confidence="unknown",
            confidence_details=confidence_details,
        )

    async def persist_score(self, *, job_url: str, job_id: Optional[str], result: ScoreResult) -> str:
        doc = {
            "job_url": job_url,
            "job_id": job_id,
            "result": result.model_dump(mode="json"),
            "created_at": datetime.utcnow(),
        }
        return await self.scores.insert_one(doc)


