"""
Vollna filter sync router - syncs Vollna filter configuration to backend filters.
"""
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Header
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.settings import settings
from ..core.logging import get_logger
from ..db.mongo import get_db
from ..repositories.collections import KeywordConfigRepo, GeoFiltersRepo
from ..schemas.keywords import KeywordCreate, KeywordSettingsUpsert
from ..schemas.geo import GeoFiltersUpsert

logger = get_logger(__name__)

router = APIRouter(prefix="/vollna/sync", tags=["vollna"])


def _check_n8n_secret(x_n8n_secret: Optional[str]) -> None:
    """Check n8n secret for authentication."""
    if settings.N8N_SHARED_SECRET is None:
        return  # not enforced if not configured
    if x_n8n_secret != settings.N8N_SHARED_SECRET:
        raise HTTPException(status_code=401, detail="invalid n8n secret")


@router.post("/filters")
async def sync_vollna_filters(
    vollna_config: dict[str, Any],
    db: AsyncIOMotorDatabase = Depends(get_db),
    x_n8n_secret: Optional[str] = Header(default=None, alias="X-N8N-Secret"),
):
    """
    Sync Vollna filter configuration to backend filters.
    
    This endpoint accepts Vollna filter configuration and syncs it to the backend's
    keyword and geo filter system.
    
    Expected Vollna Config Format:
    {
        "keywords": {
            "terms": ["python", "fastapi", "flask", "english language"],
            "match_mode": "any",  // "any" or "all"
            "search_in": ["title", "description", "skills"],  // where to search
            "exclude_keywords": false
        },
        "budget": {
            "hourly_rate_max": 50.0,
            "hourly_rate_min": null,
            "fixed_price_max": null,
            "fixed_price_min": null
        },
        "geo": {
            "excluded_countries": ["Country1", "Country2"],
            "preferred_countries": ["United States"]
        },
        "client": {
            "min_rating": 4.0,
            "payment_verified": true
        }
    }
    
    This will:
    1. Sync keywords to backend keyword_config collection
    2. Sync keyword settings (match_mode, search locations)
    3. Sync geo filters (excluded countries)
    4. Return sync summary
    """
    _check_n8n_secret(x_n8n_secret)
    
    keyword_repo = KeywordConfigRepo(db)
    geo_repo = GeoFiltersRepo(db)
    
    synced_keywords = 0
    synced_settings = False
    synced_geo = False
    errors: list[str] = []
    
    try:
        # 1. Sync Keywords
        if "keywords" in vollna_config:
            keywords_config = vollna_config["keywords"]
            
            # Extract keywords
            terms = keywords_config.get("terms") or keywords_config.get("keywords") or []
            if isinstance(terms, str):
                terms = [t.strip() for t in terms.split(",") if t.strip()]
            
            # Sync each keyword
            for term in terms:
                if not term or not term.strip():
                    continue
                
                term_lower = term.strip().lower()
                
                # Check if keyword already exists
                existing = await keyword_repo.find_one({
                    "doc_type": "keyword",
                    "term": term_lower
                })
                
                if existing:
                    # Update to ensure it's enabled
                    await keyword_repo.update_one(
                        {"_id": existing["_id"]},
                        {"$set": {"enabled": True, "updated_at": datetime.utcnow()}}
                    )
                else:
                    # Create new keyword
                    await keyword_repo.insert_one({
                        "doc_type": "keyword",
                        "term": term_lower,
                        "enabled": True,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "metadata": {
                            "source": "vollna",
                            "original_term": term
                        }
                    })
                
                synced_keywords += 1
            
            # 2. Sync Keyword Settings
            match_mode = keywords_config.get("match_mode", "any")
            search_in = keywords_config.get("search_in") or keywords_config.get("match_locations") or []
            
            # Map Vollna search locations to backend format
            match_locations = []
            if "title" in search_in or keywords_config.get("search_in_title"):
                match_locations.append("title")
            if "description" in search_in or keywords_config.get("search_in_description"):
                match_locations.append("description")
            if "skills" in search_in or keywords_config.get("search_in_skills"):
                match_locations.append("skills")
            
            # If no locations specified, default to all
            if not match_locations:
                match_locations = ["title", "description", "skills"]
            
            # Update keyword settings
            settings_doc = {
                "doc_type": "settings",
                "match_mode": match_mode,
                "match_locations": match_locations,
                "updated_at": datetime.utcnow(),
                "metadata": {
                    "source": "vollna",
                    "synced_at": datetime.utcnow().isoformat()
                }
            }
            
            await keyword_repo.update_one(
                {"doc_type": "settings"},
                {"$set": settings_doc},
                upsert=True
            )
            synced_settings = True
        
        # 3. Sync Geo Filters
        if "geo" in vollna_config:
            geo_config = vollna_config["geo"]
            excluded_countries = geo_config.get("excluded_countries") or []
            
            geo_doc = {
                "_key": "geo",
                "excluded_countries": excluded_countries,
                "updated_at": datetime.utcnow(),
                "metadata": {
                    "source": "vollna",
                    "synced_at": datetime.utcnow().isoformat(),
                    "preferred_countries": geo_config.get("preferred_countries", [])
                }
            }
            
            await geo_repo.update_one(
                {"_key": "geo"},
                {"$set": geo_doc},
                upsert=True
            )
            synced_geo = True
        
        logger.info(
            f"Vollna filters synced: keywords={synced_keywords}, "
            f"settings={synced_settings}, geo={synced_geo}"
        )
        
        return {
            "synced": True,
            "keywords_synced": synced_keywords,
            "settings_synced": synced_settings,
            "geo_synced": synced_geo,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Failed to sync Vollna filters: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync Vollna filters: {str(e)}"
        )


@router.get("/filters/status")
async def get_sync_status(
    db: AsyncIOMotorDatabase = Depends(get_db),
    x_n8n_secret: Optional[str] = Header(default=None, alias="X-N8N-Secret"),
):
    """
    Get current backend filter configuration status.
    
    Returns the current keyword and geo filter configuration so you can
    compare with Vollna filters.
    """
    _check_n8n_secret(x_n8n_secret)
    
    keyword_repo = KeywordConfigRepo(db)
    geo_repo = GeoFiltersRepo(db)
    
    # Get keywords
    keywords = await keyword_repo.find_many(
        {"doc_type": "keyword", "enabled": True},
        limit=500
    )
    
    # Get keyword settings
    settings_doc = await keyword_repo.find_one({"doc_type": "settings"})
    
    # Get geo filters
    geo_doc = await geo_repo.find_one({"_key": "geo"})
    
    return {
        "keywords": {
            "terms": [k.get("term") for k in keywords],
            "count": len(keywords)
        },
        "keyword_settings": {
            "match_mode": settings_doc.get("match_mode") if settings_doc else None,
            "match_locations": settings_doc.get("match_locations") if settings_doc else [],
        },
        "geo": {
            "excluded_countries": geo_doc.get("excluded_countries") if geo_doc else [],
        }
    }

