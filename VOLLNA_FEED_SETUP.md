# Vollna Feed Setup - Display All Upwork Jobs

## 🎯 Goal

Display ALL jobs from your Vollna/Upwork feed on the frontend dashboard.

## 📋 Current Situation

Your frontend is showing test jobs because:
1. Vollna webhook needs to be configured to send jobs to your backend
2. Jobs need to be sent from Vollna → n8n → Backend → Frontend

## 🔗 Complete Workflow

```
Upwork Jobs → Vollna Extension → n8n Webhook → POST /webhook/vollna → MongoDB → Frontend
```

## ✅ Step-by-Step Setup

### Step 1: Configure Vollna Webhook in n8n

1. **Open n8n** (your n8n instance)
2. **Create a new workflow** or edit existing one
3. **Add Webhook Trigger**:
   - Method: `POST`
   - Path: `/vollna` (or your custom path)
   - Response Mode: `When Last Node Finishes`
   - Authentication: `None` (we use header secret)

4. **Add HTTP Request Node** (to forward to backend):
   - Method: `POST`
   - URL: `https://upwork-xxsc.onrender.com/webhook/vollna`
   - Headers:
     - `X-N8N-Secret`: `9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394`
     - `Content-Type`: `application/json`
   - Body: `{{ $json }}` (pass through Vollna payload)

### Step 2: Configure Vollna Extension

1. **Install Vollna Extension** in Chrome
2. **Go to Vollna Dashboard**: https://vollna.com/dashboard
3. **Set up Job Filters** (as shown in your screenshots):
   - Keywords: python, english language, fastapis, flask
   - Budget: Max $50/hr
   - Other filters as needed

4. **Configure Webhook**:
   - Go to Vollna Settings → Integrations
   - Add webhook URL: `https://your-n8n-instance.com/webhook/vollna`
   - Enable "Send job alerts"

### Step 3: Verify Jobs Are Being Sent

**Check n8n Webhook Logs**:
- Go to n8n workflow
- Check "Recent Executions"
- Should see webhook requests from Vollna

**Check Backend Logs** (Render):
- Go to Render dashboard → Your service → Logs
- Should see: `Received Vollna webhook payload`
- Should see: `inserted_raw: X` (number of jobs)

**Test Manually**:
```bash
curl -X POST https://upwork-xxsc.onrender.com/webhook/vollna \
  -H "Authorization: Bearer 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394" \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [{
      "title": "Test Job from Vollna",
      "description": "Test description",
      "url": "https://www.upwork.com/jobs/~test123",
      "budget": 50.0,
      "proposals": 5,
      "skills": ["Python", "FastAPI"],
      "postedOn": "2025-12-19T10:00:00Z"
    }]
  }'
```

### Step 4: Frontend Configuration

**Make sure your frontend calls the API correctly**:

```javascript
// ✅ Correct - Get ALL jobs from Vollna
const API_URL = 'https://upwork-xxsc.onrender.com';

async function loadAllJobs() {
  try {
    // Get all jobs from Vollna (up to 1000)
    const response = await fetch(`${API_URL}/api/jobs?source=vollna&limit=1000`);
    const jobs = await response.json();
    console.log(`Loaded ${jobs.length} jobs from Vollna`);
    displayJobs(jobs);
  } catch (error) {
    console.error('Error loading jobs:', error);
  }
}

// Poll every 10-15 seconds for new jobs
setInterval(loadAllJobs, 10000);
```

## 🔍 Troubleshooting

### Issue: No jobs appearing

**Check 1: Are jobs being sent from Vollna?**
- Check Vollna dashboard → Job Filters → Should show jobs
- Check Vollna webhook settings → Is it enabled?

**Check 2: Is n8n receiving webhooks?**
- Check n8n workflow executions
- Should see webhook triggers

**Check 3: Is backend receiving jobs?**
```bash
# Check feed status
curl "https://upwork-xxsc.onrender.com/feeds/status?source=vollna"

# Check jobs in database
curl "https://upwork-xxsc.onrender.com/api/jobs?source=vollna&limit=10"
```

**Check 4: Are jobs in MongoDB?**
- Connect to MongoDB Atlas
- Check `jobs_raw` collection
- Filter by `source: "vollna"`
- Should see your jobs

### Issue: Only test jobs showing

**Solution**: Real jobs from Vollna haven't been sent yet. You need to:
1. Configure Vollna webhook to send to n8n
2. Configure n8n to forward to backend
3. Wait for Vollna to send job alerts

### Issue: Jobs not matching filters

**Solution**: Jobs are stored in `jobs_raw` but may not pass filters. The `/api/jobs` endpoint returns ALL jobs from `jobs_raw`, so they should appear regardless of filter status.

## 📊 Endpoints for Getting All Jobs

### Get All Vollna Jobs (Recommended)

```bash
GET /api/jobs?source=vollna&limit=1000
```

**Response**: Array of all jobs from Vollna (up to 1000)

### Get Latest Jobs

```bash
GET /jobs/latest?source=vollna&limit=1000
```

**Response**: Same as above (alternative endpoint)

### Search Jobs (with filters)

```bash
POST /jobs/search
{
  "source": "vollna",
  "limit": 1000
}
```

**Response**: 
```json
{
  "latest_jobs": [...],  // All jobs from Vollna
  "filtered_jobs": [...], // Jobs matching filters
  "latest_jobs_count": 150,
  "filtered_jobs_count": 50
}
```

## 🎯 Quick Checklist

- [ ] Vollna extension installed and enabled
- [ ] Vollna job filters configured (keywords, budget, etc.)
- [ ] Vollna webhook configured to send to n8n
- [ ] n8n workflow created with webhook trigger
- [ ] n8n HTTP request node forwards to backend
- [ ] Backend endpoint `/webhook/vollna` is accessible
- [ ] Frontend calls `/api/jobs?source=vollna&limit=1000`
- [ ] Jobs appear in MongoDB `jobs_raw` collection
- [ ] Jobs display on frontend

## 📝 Notes

1. **Limit increased**: `/api/jobs` now returns up to 1000 jobs (was 50)
2. **All jobs shown**: Endpoint returns ALL jobs from `jobs_raw`, not just filtered ones
3. **Source filter**: Use `?source=vollna` to get only Vollna jobs
4. **Real-time**: Jobs appear as soon as Vollna sends them via webhook

## 🚀 Next Steps

1. **Set up Vollna webhook** → n8n
2. **Configure n8n** → Backend
3. **Test with one job** → Verify it appears
4. **Enable Vollna alerts** → Jobs will start flowing
5. **Check frontend** → Should see all jobs

Once Vollna starts sending jobs, they will automatically appear on your frontend! 🎉

