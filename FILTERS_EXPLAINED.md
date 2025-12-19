# Filters Applied to Return 3 Jobs

## 🔍 Current Filter Applied

The `/api/jobs?source=vollna&limit=1000` endpoint applies **ONLY ONE FILTER**:

### ✅ Source Filter
- **Filter**: `source = "vollna"`
- **Collection**: `jobs_raw` (all ingested jobs, regardless of keyword/geo filters)
- **Query**: `{ "source": "vollna" }`

## 📊 Why Only 3 Jobs?

The endpoint queries the `jobs_raw` collection, which contains **ALL jobs that were successfully ingested**, regardless of whether they passed keyword or geo filters.

**The 3 jobs are:**
1. "Python Developer Test Job 1766099897" - source: vollna
2. "Python Developer Test Job 1766099376" - source: vollna  
3. "Test Job from Vollna" - source: vollna

## 🔄 Two-Stage Filtering System

### Stage 1: During Ingestion (Keyword & Geo Filters)
When jobs are ingested via `/ingest/upwork` or `/webhook/vollna`:

1. **All jobs** → Stored in `jobs_raw` collection ✅
2. **Filtered jobs** → Stored in `jobs_filtered` collection (only if they pass both):
   - ✅ Keyword match (must match keywords in title/description/skills)
   - ✅ Geo match (must NOT be in excluded countries)

### Stage 2: API Endpoint Filtering

**`GET /api/jobs?source=vollna`**:
- Queries: `jobs_raw` collection
- Filter: `source = "vollna"` only
- Returns: **ALL jobs from vollna** (regardless of keyword/geo filters)

**`GET /jobs?use_filtered=true`**:
- Queries: `jobs_filtered` collection  
- Filter: `source = "vollna"` + keyword/geo filters already applied
- Returns: **Only jobs that passed keyword AND geo filters**

## 📋 Current Configuration

### Keyword Filters
Check: `GET /config/keywords`
- Keywords configured in database
- Match mode: "any" or "all"
- Match locations: title, description, skills

### Geo Filters  
Check: `GET /config/geo`
- Excluded countries configured in database
- Jobs from excluded countries are filtered out

## 🎯 Summary

**The 3 jobs are returned because:**
1. ✅ They have `source = "vollna"`
2. ✅ They are in the `jobs_raw` collection (all ingested jobs)
3. ❌ **NO other filters are applied** by `/api/jobs` endpoint

**To see filtered jobs only:**
- Use: `GET /jobs?use_filtered=true&source=vollna`
- This returns only jobs that passed keyword AND geo filters

**To see all jobs (no filters):**
- Use: `GET /api/jobs?source=vollna` (current endpoint)
- Returns all jobs from vollna source

---

**The `/api/jobs` endpoint shows ALL jobs from vollna, not just filtered ones!** 🚀

