# Swagger UI Testing Guide - Fixed

## 🔧 Fixed Issues

1. **Webhook Payload Format**: Now accepts both single job objects and arrays
2. **Recommend Endpoint**: Fixed parameter structure

## 📋 Correct Testing Steps

### Test 1: Health Check ✅
- **Endpoint**: `GET /health`
- **Expected**: `{"status": "ok", "database": "connected"}`

### Test 2: Get Latest Jobs ✅
- **Endpoint**: `GET /jobs?source=vollna&limit=10`
- **Expected**: Array of jobs (may be empty if no jobs yet)

### Test 3: Test Vollna Webhook (FIXED) ✅

**Endpoint**: `POST /vollna/jobs`

**Authorization**: 
- Click "Authorize" button (top right)
- Enter Bearer token: `9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394`
- Click "Authorize"

**Request Body** (IMPORTANT - Use one of these formats):

**Format 1: Wrapped in "jobs" array (Recommended)**
```json
{
  "jobs": [
    {
      "title": "Test Job from Vollna",
      "description": "This is a test job to verify the webhook integration",
      "url": "https://www.upwork.com/jobs/~test123",
      "budget": 50.0,
      "proposals": 5,
      "skills": ["Python", "FastAPI", "MongoDB"],
      "postedOn": "2025-12-19T02:50:00Z"
    }
  ]
}
```

**Format 2: Direct array**
```json
[
  {
    "title": "Test Job from Vollna",
    "description": "This is a test job to verify the webhook integration",
    "url": "https://www.upwork.com/jobs/~test123",
    "budget": 50.0,
    "proposals": 5,
    "skills": ["Python", "FastAPI", "MongoDB"],
    "postedOn": "2025-12-19T02:50:00Z"
  }
]
```

**Expected Response**:
```json
{
  "received": 1,
  "inserted_raw": 1,
  "inserted_filtered": 1,
  "deduped": 0
}
```

### Test 4: Verify Job Was Stored ✅
- **Endpoint**: `GET /jobs?source=vollna&limit=1`
- **Expected**: Should show the test job you just created

### Test 5: Search Jobs ✅
- **Endpoint**: `POST /jobs/search`
- **Request Body**:
```json
{
  "source": "vollna",
  "min_budget": 30.0,
  "max_proposals": 10,
  "skills": ["Python"],
  "limit": 10,
  "skip": 0
}
```

### Test 6: Get Recommendations ✅
- **Endpoint**: `POST /jobs/recommend`
- **Request Body** (put directly in body, NOT in "payload" field):
```json
{
  "source": "vollna",
  "min_budget": 30.0,
  "max_proposals": 10,
  "limit": 5
}
```
- **Query Parameters** (optional, in the parameters section):
  - `user_skills`: `Python,FastAPI,MongoDB`
  - `prioritize_budget`: `true`
  - `prioritize_low_competition`: `true`

**Note**: If Swagger shows a "payload" field, ignore it and put the JSON directly in the body.

## 🚨 Common Errors & Fixes

### Error: "Invalid Vollna payload: expected 'jobs' array"
**Fix**: Wrap your job in a `"jobs"` array or send as an array directly

### Error: "Field required: payload"
**Fix**: Put the JSON directly in the request body, not in a "payload" field

### Error: Empty jobs array
**Fix**: 
1. First test the webhook endpoint to create a job
2. Then check `/jobs` endpoint
3. Make sure `source=vollna` parameter is set

## ✅ Success Checklist

- [ ] Health endpoint returns `{"status": "ok"}`
- [ ] Webhook accepts job and returns success
- [ ] `/jobs` endpoint shows the test job
- [ ] `/jobs/search` returns filtered results
- [ ] `/jobs/recommend` returns ranked jobs

