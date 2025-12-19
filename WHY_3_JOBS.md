# Why Backend Shows Only 3 Jobs

## 📊 Current Status

The backend is showing **3 jobs** because there are only **3 jobs in the database** with `source=vollna`.

## 🔍 How the Backend Works

### Endpoint: `GET /api/jobs?source=vollna&limit=1000`

**Query Logic**:
1. Queries `jobs_raw` collection (all ingested jobs)
2. Filters by `source=vollna` 
3. Sorts by `posted_at` DESC (newest first)
4. Returns up to `limit` jobs (default: 200, max: 1000)

**Code** (`backend/app/routers/jobs.py`):
```python
@api_router.get("/jobs")
async def get_jobs_api(
    source: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
):
    repo = JobsRawRepo(db)
    
    query = {}
    if source:
        query["source"] = source  # Filters to source=vollna
    
    docs = await repo.find_many(
        query,
        skip=0,
        limit=limit,  # Up to 1000
        sort=[("posted_at", -1), ("created_at", -1)]  # Newest first
    )
    
    return jobs
```

## 📋 The 3 Jobs

From the API response:
1. **"Python Developer Test Job 1766099897"** - Posted: 2025-12-18T23:18:17
2. **"Python Developer Test Job 1766099376"** - Posted: 2025-12-18T23:09:36
3. **"Test Job from Vollna"** - Posted: 2025-12-18T22:04:37

All have `source: "vollna"`.

## ✅ Backend is Working Correctly

The backend is **not limiting** the results - it's returning all jobs that match the criteria:
- ✅ Querying `jobs_raw` collection (all jobs)
- ✅ Filtering by `source=vollna` (as requested)
- ✅ Limit set to 1000 (not limiting)
- ✅ Sorting by newest first

**The issue is**: There are only 3 jobs in the database with `source=vollna`.

## 🔍 How to Verify

### Check Total Jobs (All Sources):
```bash
curl 'http://localhost:8000/api/jobs?limit=1000'
```

### Check Vollna Jobs Only:
```bash
curl 'http://localhost:8000/api/jobs?source=vollna&limit=1000'
```

### Check Feed Status:
```bash
curl 'http://localhost:8000/feeds/status'
```

## 📥 How to Get More Jobs

### Option 1: Send Jobs via Vollna Webhook
1. Configure Vollna to send jobs to: `POST /webhook/vollna`
2. Jobs will be automatically ingested
3. Check feed status: `GET /feeds/status`

### Option 2: Manual Ingestion
Send jobs via `POST /ingest/upwork`:
```bash
curl -X POST http://localhost:8000/ingest/upwork \
  -H "Content-Type: application/json" \
  -H "X-N8N-Secret: YOUR_SECRET" \
  -d '{
    "jobs": [
      {
        "title": "New Job",
        "description": "Job description",
        "url": "https://www.upwork.com/jobs/~test123",
        "source": "vollna",
        "postedOn": "2025-12-19T12:00:00",
        "skills": ["Python"],
        "budget": 100,
        "proposals": 5
      }
    ]
  }'
```

### Option 3: Check MongoDB Directly
```bash
# Connect to MongoDB and check
mongosh "your-mongodb-uri"
use your-database
db.jobs_raw.countDocuments({ source: "vollna" })
db.jobs_raw.find({ source: "vollna" }).count()
```

## 🎯 Summary

- **Backend is correct**: Returns all jobs matching criteria
- **Only 3 jobs exist**: In database with `source=vollna`
- **To get more jobs**: Configure Vollna webhook or manually ingest

The backend is working as expected - you just need more jobs in the database! 🚀

