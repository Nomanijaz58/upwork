# How to Add Jobs to the Dashboard

## ✅ Current Status

The endpoint `/jobs/all` is **working correctly**! The "No jobs found" message is expected because the `vollna_jobs` collection is currently empty.

## 🚀 How Jobs Get Added

Jobs are added to the dashboard through the **Vollna webhook**. There are two ways:

### Option 1: Automatic (via Vollna + n8n)
If you have Vollna configured with n8n, jobs will be sent automatically when:
- New jobs match your saved searches
- Vollna detects new Upwork jobs
- Your n8n workflow triggers

### Option 2: Manual Test (Send a Test Job)

You can manually send a test job to verify everything works:

```bash
curl -X POST https://upwork-xxsc.onrender.com/webhook/vollna \
  -H "Content-Type: application/json" \
  -H "X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394" \
  -d '[{
    "title": "Python Developer Needed",
    "url": "https://www.upwork.com/jobs/~test123",
    "budget": 75.0,
    "client_name": "Tech Corp",
    "description": "Looking for an experienced Python developer"
  }]'
```

**Expected Response**:
```json
{
  "received": 1,
  "inserted": 1,
  "errors": 0,
  "error_details": null
}
```

### After Sending a Job:

1. **Wait 2-3 seconds** for processing
2. **Refresh your frontend** (`http://localhost:8080`)
3. **Jobs should appear** in the dashboard!

## 📋 Required Fields for Jobs

When sending jobs via webhook, include these fields:

- ✅ `title` (required) - Job title
- ✅ `url` (required) - Upwork job URL
- ✅ `budget` (required) - Budget amount (number)
- ✅ `client_name` (required) - Client name
- ⚪ `description` (optional) - Job description
- ⚪ `skills` (optional) - Array of skills
- ⚪ `proposals` (optional) - Number of proposals
- ⚪ Any other fields from Vollna

## 🔍 Verify Jobs Are Added

### Check via API:
```bash
curl https://upwork-xxsc.onrender.com/jobs/all
```

### Check in Frontend:
- Open `http://localhost:8080`
- Jobs should appear in the "JOB QUEUE" section
- Metrics cards should update (Jobs Fetched Today, etc.)

## 🎯 Next Steps

1. **Send a test job** (using the curl command above)
2. **Refresh frontend** - Jobs should appear
3. **Set up Vollna webhook** - For automatic job ingestion
4. **Configure n8n** - To forward Vollna jobs to your backend

---

**The system is working!** You just need to send jobs via the webhook. 🚀

