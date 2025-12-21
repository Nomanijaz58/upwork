"""
AI router - provides AI-powered job ranking and proposal generation.
"""
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..db.mongo import get_db
from ..repositories.base import oid_str
from ..repositories.collections import JobsFilteredRepo
from ..schemas.jobs import JobRankRequest, JobRankResponse, JobOut
from ..schemas.jobs import ProposalGenerateAIRequest
from ..services.openai_service import OpenAIService
from ..core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/rank-jobs", response_model=JobRankResponse)
async def rank_jobs(
    payload: JobRankRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    AI-powered job ranking based on multiple factors.
    
    Scores jobs based on:
    - Budget (higher = better, if prioritize_budget is True)
    - Proposal count (lower = better, if prioritize_low_competition is True)
    - Skill relevance (matches with user_skills)
    - Description quality (AI analysis)
    
    Returns ranked jobs with scores and breakdown.
    """
    repo = JobsFilteredRepo(db)
    
    # Fetch all jobs
    jobs: list[dict[str, Any]] = []
    for job_id in payload.job_ids:
        doc = await repo.find_by_id(job_id)
        if doc:
            jobs.append(doc)
    
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found with provided IDs")
    
    # Score each job
    ranked_results: list[dict[str, Any]] = []
    
    for job in jobs:
        score = 0.0
        breakdown: dict[str, Any] = {
            "budget_score": 0.0,
            "competition_score": 0.0,
            "skill_relevance_score": 0.0,
            "description_quality_score": 0.0,
        }
        
        # 1. Budget scoring (0-30 points)
        budget = job.get("budget")
        if budget is not None and payload.prioritize_budget:
            # Normalize budget: higher budget = higher score
            # Assuming typical range: $10-$200/hour
            normalized_budget = min(budget / 200.0, 1.0)  # Cap at $200
            budget_score = normalized_budget * 30.0
            breakdown["budget_score"] = budget_score
            score += budget_score
        elif budget is not None:
            # Still give some points for having budget info
            breakdown["budget_score"] = 5.0
            score += 5.0
        
        # 2. Competition scoring (0-25 points)
        proposals = job.get("proposals")
        if proposals is not None and payload.prioritize_low_competition:
            # Lower proposals = higher score
            # Normalize: 0 proposals = 25 points, 50+ proposals = 0 points
            if proposals == 0:
                competition_score = 25.0
            elif proposals <= 50:
                competition_score = 25.0 * (1.0 - (proposals / 50.0))
            else:
                competition_score = 0.0
            breakdown["competition_score"] = competition_score
            score += competition_score
        elif proposals is not None:
            # Still give some points for having proposal info
            breakdown["competition_score"] = 5.0
            score += 5.0
        
        # 3. Skill relevance scoring (0-25 points)
        job_skills = [s.lower() for s in (job.get("skills") or [])]
        user_skills = [s.lower() for s in (payload.user_skills or [])]
        
        if user_skills and job_skills:
            # Count matching skills
            matches = len(set(user_skills) & set(job_skills))
            total_user_skills = len(user_skills)
            if total_user_skills > 0:
                relevance_ratio = matches / total_user_skills
                skill_score = relevance_ratio * 25.0
                breakdown["skill_relevance_score"] = skill_score
                breakdown["matched_skills"] = list(set(user_skills) & set(job_skills))
                score += skill_score
        else:
            breakdown["skill_relevance_score"] = 0.0
        
        # 4. Description quality scoring (0-20 points) - AI analysis
        description = job.get("description", "")
        if description:
            # Simple heuristic: longer, more detailed descriptions score higher
            # In production, you could use AI to analyze description quality
            word_count = len(description.split())
            if word_count < 50:
                quality_score = 5.0
            elif word_count < 200:
                quality_score = 10.0
            elif word_count < 500:
                quality_score = 15.0
            else:
                quality_score = 20.0
            
            # Check for key indicators of quality
            quality_indicators = ["experience", "requirements", "skills", "project", "deliverables"]
            indicator_count = sum(1 for indicator in quality_indicators if indicator.lower() in description.lower())
            quality_score += min(indicator_count * 1.0, 5.0)  # Up to 5 bonus points
            
            breakdown["description_quality_score"] = min(quality_score, 20.0)
            score += min(quality_score, 20.0)
        else:
            breakdown["description_quality_score"] = 0.0
        
        # Total score (0-100)
        breakdown["total_score"] = min(score, 100.0)
        
        ranked_results.append({
            "job_id": oid_str(job["_id"]),
            "job_url": job.get("url", ""),
            "title": job.get("title", ""),
            "score": min(score, 100.0),
            "breakdown": breakdown,
            "budget": budget,
            "proposals": proposals,
            "skills": job.get("skills", []),
        })
    
    # Sort by score (highest first)
    ranked_results.sort(key=lambda x: x["score"], reverse=True)
    
    return JobRankResponse(
        ranked_jobs=ranked_results,
        scoring_breakdown={
            "max_score": 100.0,
            "factors": {
                "budget": "0-30 points (higher budget = higher score)",
                "competition": "0-25 points (fewer proposals = higher score)",
                "skill_relevance": "0-25 points (more matching skills = higher score)",
                "description_quality": "0-20 points (detailed descriptions = higher score)",
            },
            "prioritize_budget": payload.prioritize_budget,
            "prioritize_low_competition": payload.prioritize_low_competition,
        }
    )


@router.post("/generate-proposal")
async def generate_proposal_ai(
    payload: ProposalGenerateAIRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Generate AI-powered custom proposals with tone and length options.
    
    Uses job description + user profile to generate personalized proposals.
    Supports different tones (professional, friendly, casual, formal) and
    lengths (short, medium, long).
    """
    from ..repositories.collections import JobsFilteredRepo, PortfoliosRepo, PromptTemplatesRepo, AISettingsRepo, ProposalsRepo
    from ..services.audit import AuditService
    
    repo = JobsFilteredRepo(db)
    portfolios = PortfoliosRepo(db)
    prompts = PromptTemplatesRepo(db)
    ai_settings = AISettingsRepo(db)
    proposals = ProposalsRepo(db)
    audit = AuditService(db)
    
    # Get job
    job: Optional[dict[str, Any]] = None
    if payload.job_id:
        job = await repo.find_by_id(payload.job_id)
    elif payload.job_url:
        job = await repo.find_one({"url": payload.job_url})
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get portfolio
    portfolio: Optional[dict[str, Any]] = None
    if payload.portfolio_id:
        portfolio = await portfolios.find_by_id(payload.portfolio_id)
    else:
        portfolio = await portfolios.find_one({"is_default": True})
    
    # Get AI settings
    ai_doc = await ai_settings.find_one({"_key": "ai"})
    if not ai_doc:
        raise HTTPException(status_code=400, detail="AI settings not configured")
    
    model = ai_doc.get("model", "gpt-4")
    temperature = ai_doc.get("temperature", 0.7)
    max_tokens = ai_doc.get("max_tokens", 2000)
    
    # Build prompt based on tone and length
    job_title = job.get("title", "")
    job_description = job.get("description", "")
    job_skills = ", ".join(job.get("skills", []))
    
    portfolio_name = portfolio.get("name", "") if portfolio else ""
    portfolio_projects = portfolio.get("projects", []) if portfolio else []
    
    # Tone instructions
    tone_instructions = {
        "professional": "Write in a professional, business-like tone. Be respectful and formal.",
        "friendly": "Write in a warm, friendly tone. Be approachable and personable.",
        "casual": "Write in a casual, conversational tone. Be relaxed and easy-going.",
        "formal": "Write in a very formal, corporate tone. Use formal language and structure.",
    }
    tone_instruction = tone_instructions.get(payload.tone.lower(), tone_instructions["professional"])
    
    # Length targets
    length_targets = {
        "short": "Keep it brief (2-3 paragraphs, ~150 words). Get straight to the point.",
        "medium": "Write a medium-length proposal (4-5 paragraphs, ~300 words). Provide good detail.",
        "long": "Write a comprehensive proposal (6+ paragraphs, ~500+ words). Include extensive detail.",
    }
    length_target = length_targets.get(payload.length.lower(), length_targets["medium"])
    
    # Build the prompt
    prompt = f"""You are an expert Upwork proposal writer. Write a custom proposal for this job posting.

JOB TITLE: {job_title}

JOB DESCRIPTION:
{job_description}

REQUIRED SKILLS: {job_skills}

MY PORTFOLIO:
Name: {portfolio_name}
Projects: {len(portfolio_projects)} projects completed

INSTRUCTIONS:
- {tone_instruction}
- {length_target}
- Highlight relevant experience from my portfolio
- Show understanding of the job requirements
- Demonstrate value I can bring
- Be specific and avoid generic statements
"""
    
    if payload.custom_message:
        prompt += f"\nCUSTOM MESSAGE TO INCLUDE: {payload.custom_message}\n"
    
    prompt += "\nWrite the proposal now:"
    
    # Generate proposal using AI service (OpenAI or Gemini)
    try:
        model_str = str(model).lower()
        if 'gemini' in model_str or model_str == 'gemini-pro' or model_str == 'gemini':
            from ..services.gemini_service import GeminiService
            ai_service = GeminiService()
        else:
            ai_service = OpenAIService()
        
        proposal_text, meta = await ai_service.generate(
            model=str(model),
            temperature=float(temperature),
            max_tokens=int(max_tokens),
            prompt=prompt,
        )
    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate proposal: {str(e)}")
    
    # Store proposal
    now = datetime.utcnow()
    proposal_doc = {
        "job_url": job.get("url"),
        "job_title": job_title,
        "status": "generated",
        "proposal_text": proposal_text,
        "model": meta.get("model"),
        "token_usage": meta.get("usage", {}),
        "prompt_template_id": payload.prompt_template_id,
        "portfolio_id": payload.portfolio_id,
        "metadata": {
            "tone": payload.tone,
            "length": payload.length,
            "custom_message": payload.custom_message,
        },
        "created_at": now,
        "updated_at": now,
    }
    
    proposal_id = await proposals.insert_one(proposal_doc)
    
    # Audit log
    await audit.log(
        action="proposal_generated_ai",
        entity="proposals",
        entity_id=proposal_id,
        data={
            "job_id": payload.job_id,
            "job_url": payload.job_url,
            "tone": payload.tone,
            "length": payload.length,
        }
    )
    
    return {
        "proposal_id": proposal_id,
        "job_url": job.get("url"),
        "job_title": job_title,
        "proposal_text": proposal_text,
        "tone": payload.tone,
        "length": payload.length,
        "model": meta.get("model"),
        "token_usage": meta.get("usage", {}),
        "created_at": now.isoformat(),
    }

