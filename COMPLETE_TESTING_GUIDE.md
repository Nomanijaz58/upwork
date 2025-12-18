# Complete Testing Guide - All Endpoints

## 🎯 Quick Start Testing

### Step 1: Verify Service is Running
```bash
curl https://upwork-xxsc.onrender.com/health
```
**Expected**: `{"status":"ok","database":"connected"}`

### Step 2: Open Swagger UI
**URL**: https://upwork-xxsc.onrender.com/docs

---

## 📋 Endpoint Testing Checklist

### ✅ Test 1: Health Check
- [ ] `GET /health` returns `{"status":"ok","database":"connected"}`

### ✅ Test 2: Feed Status
- [ ] `GET /feeds/status?source=vollna` shows feed information

### ✅ Test 3: Get Latest Jobs
- [ ] `GET /jobs?source=vollna&limit=10` returns jobs array

### ✅ Test 4: Vollna Webhook (Create Test Job)
- [ ] `POST /vollna/jobs` successfully stores a job
- [ ] Response shows `inserted_raw: 1` and `inserted_filtered: 1`

### ✅ Test 5: Search Jobs (New Format)
- [ ] `POST /jobs/search` returns both `latest_jobs` and `filtered_jobs`
- [ ] Counts match array lengths

### ✅ Test 6: Get Recommendations
- [ ] `POST /jobs/recommend` returns ranked jobs

---

## 🧪 Detailed Testing Steps

### Test 1: Health Check

**Swagger UI**:
1. Find `GET /health`
2. Click "Try it out" → "Execute"
3. Should return: `{"status":"ok","database":"connected"}`

**cURL**:
```bash
curl https://upwork-xxsc.onrender.com/health
```

---

### Test 2: Feed Status

**Swagger UI**:
1. Find `GET /feeds/status`
2. Click "Try it out"
3. Set parameter: `source` = `vollna`
4. Click "Execute"
5. Should show feed status with last fetch time

**cURL**:
```bash
curl "https://upwork-xxsc.onrender.com/feeds/status?source=vollna"
```

---

### Test 3: Get Latest Jobs

**Swagger UI**:
1. Find `GET /jobs`
2. Click "Try it out"
3. Set parameters:
   - `source` = `vollna`
   - `limit` = `10`
   - `skip` = `0`
4. Click "Execute"
5. Should return array of jobs (may be empty if no jobs yet)

**cURL**:
```bash
curl "https://upwork-xxsc.onrender.com/jobs?source=vollna&limit=10"
```

---

### Test 4: Vollna Webhook (Create Test Job) ⭐ IMPORTANT

This creates a test job so you can verify other endpoints work.

**Swagger UI**:
1. Find `POST /vollna/jobs`
2. Click "Authorize" (top right)
   - Enter: `9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394`
   - Click "Authorize"
3. Click "Try it out"
4. **Request Body** (IMPORTANT - wrap in "jobs" array):
```json
{
  "jobs": [
    {
      "title": "Python Backend Developer - Test Job",
      "description": "Looking for an experienced Python developer to build a REST API using FastAPI and MongoDB. Must have 3+ years experience. This is a test job to verify the webhook integration.",
      "url": "https://www.upwork.com/jobs/~test123",
      "budget": 75.0,
      "proposals": 8,
      "skills": ["Python", "FastAPI", "MongoDB", "REST API"],
      "postedOn": "2025-12-19T03:00:00Z"
    }
  ]
}
```
5. Click "Execute"
6. **Expected Response**:
```json
{
  "received": 1,
  "inserted_raw": 1,
  "inserted_filtered": 1,
  "deduped": 0
}
```

**cURL**:
```bash
curl -X POST https://upwork-xxsc.onrender.com/vollna/jobs \
  -H "Authorization: Bearer 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394" \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [
      {
        "title": "Python Backend Developer - Test Job",
        "description": "Looking for an experienced Python developer",
        "url": "https://www.upwork.com/jobs/~test123",
        "budget": 75.0,
        "proposals": 8,
        "skills": ["Python", "FastAPI", "MongoDB"],
        "postedOn": "2025-12-19T03:00:00Z"
      }
    ]
  }'
```

---

### Test 5: Search Jobs (New Format) ⭐ NEW

**Swagger UI**:
1. Find `POST /jobs/search`
2. Click "Try it out"
3. **Test A: Without Filters**
   ```json
   {
     "source": "vollna",
     "limit": 10
   }
   ```
   **Expected**:
   - `latest_jobs`: Array with your test job
   - `filtered_jobs`: Same as latest_jobs (no filters)
   - `latest_jobs_count`: 1 (or more)
   - `filtered_jobs_count`: 1 (or more)

4. **Test B: With Budget Filter**
   ```json
   {
     "source": "vollna",
     "min_budget": 50.0,
     "limit": 10
   }
   ```
   **Expected**:
   - `latest_jobs`: All jobs from vollna
   - `filtered_jobs`: Only jobs with budget >= 50
   - `filtered_jobs_count` <= `latest_jobs_count`

5. **Test C: With Skills Filter**
   ```json
   {
     "source": "vollna",
     "skills": ["Python", "FastAPI"],
     "limit": 10
   }
   ```
   **Expected**:
   - `latest_jobs`: All jobs from vollna
   - `filtered_jobs`: Only jobs with Python or FastAPI skills

**cURL**:
```bash
# Without filters
curl -X POST https://upwork-xxsc.onrender.com/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "source": "vollna",
    "limit": 10
  }'

# With filters
curl -X POST https://upwork-xxsc.onrender.com/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "source": "vollna",
    "min_budget": 50.0,
    "skills": ["Python"],
    "limit": 10
  }'
```

---

### Test 6: Get Recommendations

**Swagger UI**:
1. Find `POST /jobs/recommend`
2. Click "Try it out"
3. **Request Body**:
```json
{
  "source": "vollna",
  "min_budget": 30.0,
  "max_proposals": 10,
  "limit": 5
}
```
4. **Query Parameters** (optional):
   - `user_skills`: `Python,FastAPI,MongoDB`
   - `prioritize_budget`: `true`
   - `prioritize_low_competition`: `true`
5. Click "Execute"
6. **Expected**: Ranked jobs with scores

**cURL**:
```bash
curl -X POST "https://upwork-xxsc.onrender.com/jobs/recommend?user_skills=Python,FastAPI&prioritize_budget=true" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "vollna",
    "min_budget": 30.0,
    "limit": 5
  }'
```

---

## 🔍 Verification Steps

### Step 1: Verify Job Was Stored

After Test 4 (webhook), verify the job appears:

1. **Get Latest Jobs**:
   ```bash
   curl "https://upwork-xxsc.onrender.com/jobs?source=vollna&limit=1"
   ```
   Should show your test job

2. **Search Jobs**:
   ```bash
   curl -X POST https://upwork-xxsc.onrender.com/jobs/search \
     -H "Content-Type: application/json" \
     -d '{"source": "vollna", "limit": 1}'
   ```
   Should show job in both `latest_jobs` and `filtered_jobs`

### Step 2: Verify Database

**Option A: Using MongoDB Compass**
1. Connect to your Atlas cluster
2. Go to `upwork_proposal_bot` database
3. Check `jobs_raw` collection - should have your test job
4. Check `jobs_filtered` collection - should have your test job

**Option B: Using Verification Script**
```bash
cd backend
python3 ../verify_database_insertion.py
```

### Step 3: Test Filters Work

1. **Test with strict filter** (should return empty):
   ```json
   {
     "source": "vollna",
     "min_budget": 1000.0,
     "limit": 10
   }
   ```
   Expected: `filtered_jobs` is empty, but `latest_jobs` has jobs

2. **Test with matching filter**:
   ```json
   {
     "source": "vollna",
     "skills": ["Python"],
     "limit": 10
   }
   ```
   Expected: `filtered_jobs` contains jobs with Python skill

---

## 🚨 Troubleshooting

### Issue: Empty arrays in search response

**Check**:
1. Did you run Test 4 (webhook) first?
2. Check feed status: `GET /feeds/status?source=vollna`
3. Verify in MongoDB Compass

### Issue: Webhook returns error

**Check**:
1. Authorization token is correct
2. Payload is wrapped in `{"jobs": [...]}`
3. Required fields: title, description, url

### Issue: filtered_jobs is empty but latest_jobs has items

**This is normal if**:
- Filters are too strict
- Jobs don't match filter criteria

**To verify**:
- Test without filters first
- Gradually add filters to see which excludes jobs

---

## ✅ Success Criteria

- [ ] Health check returns OK
- [ ] Webhook successfully creates job
- [ ] Job appears in `GET /jobs`
- [ ] Search returns both `latest_jobs` and `filtered_jobs`
- [ ] Counts match array lengths
- [ ] Filters work correctly
- [ ] Recommendations return ranked jobs

---

## 📊 Expected Response Examples

### Search Without Filters
```json
{
  "latest_jobs": [{"id": "...", "title": "Test Job", ...}],
  "latest_jobs_count": 1,
  "filtered_jobs": [{"id": "...", "title": "Test Job", ...}],
  "filtered_jobs_count": 1,
  "applied_filters": {"source": "vollna"}
}
```

### Search With Filters
```json
{
  "latest_jobs": [{"id": "...", "title": "Test Job", ...}],
  "latest_jobs_count": 1,
  "filtered_jobs": [{"id": "...", "title": "Test Job", ...}],
  "filtered_jobs_count": 1,
  "applied_filters": {
    "source": "vollna",
    "budget": {"$gte": 50.0},
    "skills": {"$in": ["Python"]}
  }
}
```

---

## 🎯 Quick Test Sequence

Run these in order:

1. ✅ Health: `GET /health`
2. ✅ Create Job: `POST /vollna/jobs` (with test job)
3. ✅ Verify: `GET /jobs?source=vollna`
4. ✅ Search (no filters): `POST /jobs/search` with `{"source": "vollna"}`
5. ✅ Search (with filters): `POST /jobs/search` with filters
6. ✅ Recommendations: `POST /jobs/recommend`

All tests should pass! 🎉

