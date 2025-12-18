# Testing /jobs/search Endpoint - Complete Guide

## ✅ What Was Fixed

1. **Updated Response Schema**: Now returns both `latest_jobs` and `filtered_jobs`
2. **Database Verification**: Confirmed jobs are inserted into both `jobs_raw` and `jobs_filtered`
3. **Response Structure**: Includes counts for easy debugging

## 📋 New Response Format

```json
{
  "latest_jobs": [
    {
      "id": "...",
      "title": "Python Backend Developer",
      "description": "Fix API latency issues",
      "url": "https://www.upwork.com/jobs/~abc123",
      "budget": 500.0,
      "proposals": 5,
      "skills": ["Python", "FastAPI"],
      "source": "vollna",
      "posted_at": "2025-12-19T02:50:00Z"
    }
  ],
  "latest_jobs_count": 5,
  "filtered_jobs": [
    {
      "id": "...",
      "title": "Python Backend Developer",
      "description": "Fix API latency issues",
      "url": "https://www.upwork.com/jobs/~abc123",
      "budget": 500.0,
      "proposals": 5,
      "skills": ["Python", "FastAPI"],
      "source": "vollna",
      "posted_at": "2025-12-19T02:50:00Z"
    }
  ],
  "filtered_jobs_count": 2,
  "applied_filters": {
    "source": "vollna",
    "budget": {"$gte": 100},
    "skills": {"$in": ["Python"]}
  }
}
```

## 🧪 Test Cases

### Test 1: Without Filters (Empty/Broad Filters)

**Request**:
```bash
curl -X POST https://upwork-xxsc.onrender.com/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "source": "vollna",
    "limit": 10
  }'
```

**Expected**:
- `latest_jobs`: All jobs from vollna source
- `filtered_jobs`: Same as latest_jobs (no filters applied)
- Both arrays should have jobs if any exist

### Test 2: With Budget Filter

**Request**:
```bash
curl -X POST https://upwork-xxsc.onrender.com/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "source": "vollna",
    "min_budget": 100.0,
    "limit": 10
  }'
```

**Expected**:
- `latest_jobs`: All jobs from vollna
- `filtered_jobs`: Only jobs with budget >= 100
- `filtered_jobs_count` <= `latest_jobs_count`

### Test 3: With Skills Filter

**Request**:
```bash
curl -X POST https://upwork-xxsc.onrender.com/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "source": "vollna",
    "skills": ["Python", "FastAPI"],
    "limit": 10
  }'
```

**Expected**:
- `latest_jobs`: All jobs from vollna
- `filtered_jobs`: Only jobs with Python or FastAPI skills
- `filtered_jobs_count` <= `latest_jobs_count`

### Test 4: With Multiple Filters

**Request**:
```bash
curl -X POST https://upwork-xxsc.onrender.com/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "source": "vollna",
    "min_budget": 50.0,
    "max_proposals": 10,
    "skills": ["Python"],
    "keywords": ["backend", "API"],
    "limit": 10
  }'
```

**Expected**:
- `latest_jobs`: All jobs from vollna
- `filtered_jobs`: Jobs matching ALL criteria:
  - Budget >= 50
  - Proposals <= 10
  - Has Python skill
  - Contains "backend" or "API" in title/description

## 🔍 Verification Steps

### Step 1: Verify Database Insertion

1. **Check jobs_raw collection**:
   ```bash
   # In MongoDB Compass or shell
   db.jobs_raw.find({"source": "vollna"}).count()
   ```

2. **Check jobs_filtered collection**:
   ```bash
   db.jobs_filtered.find({"source": "vollna"}).count()
   ```

3. **Expected**: 
   - `jobs_raw` should have all jobs from Vollna
   - `jobs_filtered` should have jobs that passed keyword/geo filters

### Step 2: Test in Swagger UI

1. Go to: https://upwork-xxsc.onrender.com/docs
2. Find `POST /jobs/search`
3. Click "Try it out"
4. Test with empty filters first:
   ```json
   {
     "source": "vollna",
     "limit": 10
   }
   ```
5. Verify `latest_jobs` array has jobs
6. Verify `filtered_jobs` array has jobs (or is empty if filters are strict)

### Step 3: Test with Filters

1. Add filters:
   ```json
   {
     "source": "vollna",
     "min_budget": 30.0,
     "skills": ["Python"],
     "limit": 10
   }
   ```
2. Verify:
   - `latest_jobs_count` >= `filtered_jobs_count`
   - `filtered_jobs` only contains jobs matching filters

## 🚨 Troubleshooting

### Issue: Empty latest_jobs array

**Possible Causes**:
1. No jobs have been ingested from Vollna yet
2. Source filter is incorrect
3. Jobs are in `jobs_raw` but not in `jobs_filtered`

**Solution**:
1. Test webhook endpoint first to create a job
2. Check `GET /jobs?source=vollna` to see if jobs exist
3. Verify jobs are in `jobs_filtered` collection

### Issue: filtered_jobs is empty but latest_jobs has jobs

**Possible Causes**:
1. Filters are too strict
2. Jobs don't match filter criteria

**Solution**:
1. Test without filters first
2. Gradually add filters to see which one excludes jobs
3. Check `applied_filters` in response to see what was applied

### Issue: Jobs not appearing after webhook

**Possible Causes**:
1. Jobs failed keyword/geo filtering
2. Jobs were deduplicated
3. Database insertion failed

**Solution**:
1. Check webhook response: `inserted_raw` and `inserted_filtered` counts
2. Check feed status: `GET /feeds/status?source=vollna`
3. Verify in MongoDB directly

## ✅ Success Criteria

- [ ] `latest_jobs` array contains all jobs from source
- [ ] `filtered_jobs` array contains jobs matching filters
- [ ] `latest_jobs_count` >= `filtered_jobs_count`
- [ ] Empty arrays only appear when no jobs match (not due to errors)
- [ ] `applied_filters` shows correct filter criteria
- [ ] Jobs are sorted by newest first (posted_at DESC)

