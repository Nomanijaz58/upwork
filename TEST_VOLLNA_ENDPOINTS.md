# Testing Vollna Integration - Complete Guide

## 🎯 Goal
Test all endpoints to verify they catch and process jobs from Vollna webhook.

## 📋 Testing Checklist

### Step 1: Verify Webhook is Receiving Data
- [ ] Check Vollna webhook shows "Recent Requests" with successful deliveries
- [ ] Verify webhook URL is correct: `https://upwork-xxsc.onrender.com/vollna/jobs`

### Step 2: Test Endpoints in Swagger
- [ ] Test `/vollna/jobs` - Direct webhook endpoint
- [ ] Test `/jobs` - Get latest jobs
- [ ] Test `/jobs/search` - Search with filters
- [ ] Test `/jobs/recommend` - AI recommendations
- [ ] Test `/feeds/status` - Check feed health

## 🔗 Swagger UI Links

**Main Swagger UI**: https://upwork-xxsc.onrender.com/docs

## 🧪 Step-by-Step Testing

### Test 1: Check Health
**Endpoint**: `GET /health`
**Expected**: `{"status": "ok", "database": "connected"}`

### Test 2: Check Feed Status
**Endpoint**: `GET /feeds/status?source=vollna`
**Expected**: Shows feed status with last fetch time

### Test 3: Get Latest Jobs
**Endpoint**: `GET /jobs?source=vollna&limit=10`
**Expected**: Returns latest jobs from Vollna

### Test 4: Search Jobs
**Endpoint**: `POST /jobs/search`
**Body**:
```json
{
  "source": "vollna",
  "limit": 10,
  "skip": 0
}
```

### Test 5: Test Vollna Webhook Directly
**Endpoint**: `POST /vollna/jobs`
**Headers**:
- `Authorization: Bearer 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394`
- `Content-Type: application/json`
**Body**:
```json
{
  "title": "Test Job from Vollna",
  "description": "This is a test job to verify the webhook is working",
  "url": "https://www.upwork.com/jobs/~test123",
  "budget": 50.0,
  "proposals": 5,
  "skills": ["Python", "FastAPI"],
  "postedOn": "2025-12-19T02:50:00Z"
}
```

### Test 6: Get Recommendations
**Endpoint**: `POST /jobs/recommend`
**Body**:
```json
{
  "source": "vollna",
  "limit": 5,
  "min_budget": 30.0,
  "max_proposals": 10
}
```

