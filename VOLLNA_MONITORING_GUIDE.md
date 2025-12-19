# Vollna Monitoring & Debugging Guide

## 🔍 How to Check if Vollna is Working

### Method 1: Quick Test Script

Run the test script to verify everything is working:

```bash
./test_vollna_webhook.sh
```

**What it does:**
1. ✅ Checks backend health
2. ✅ Shows current jobs count
3. ✅ Sends a test job via webhook
4. ✅ Verifies job was stored
5. ✅ Tests filter endpoint

**Expected output:**
```
🔍 Vollna Webhook Testing & Monitoring
======================================

1️⃣  Backend Health Check
Checking Backend health... ✅ OK
{"status":"ok","database":"connected"}

2️⃣  Current Jobs in Database
Checking All jobs from Vollna... ✅ OK
{"count":3,"jobs":[...]}

3️⃣  Sending Test Job via Webhook
Sending job...
✅ Webhook accepted job
{"received":1,"inserted":1,"errors":0}

4️⃣  Verifying Job Was Stored
Checking All jobs (should include new test job)... ✅ OK
{"count":4,"jobs":[...]}
```

### Method 2: Real-Time Monitoring

Monitor jobs in real-time and see new jobs as they arrive:

```bash
# Watch for new jobs only (recommended)
python3 monitor_vollna_jobs.py

# Show all jobs every 10 seconds
python3 monitor_vollna_jobs.py 10 all

# Custom interval (5 seconds)
python3 monitor_vollna_jobs.py 5
```

**What you'll see:**
```
🔍 Vollna Jobs Monitor
================================================================================
API URL: https://upwork-xxsc.onrender.com
Refresh interval: 10 seconds
Watch mode: ON (shows only new jobs)
================================================================================

⏰ [2025-12-20 01:50:00] Job count changed: 3 → 4

🆕 Found 1 new job(s)!

================================================================================
Job #1
================================================================================
📋 Title:     Python Developer Needed
🆔 ID:        6945b1b2a95fdc350f9ae31a
💰 Budget:    $75.0/hr
👤 Client:    Tech Corp
📅 Created:   2025-12-19T20:12:34.495000
🔗 URL:       https://www.upwork.com/jobs/~test123
🛠️  Skills:    Python, FastAPI
📊 Proposals:  5
================================================================================
```

### Method 3: Manual API Testing

#### Check Current Jobs:
```bash
curl https://upwork-xxsc.onrender.com/jobs/all | python3 -m json.tool
```

#### Send Test Job:
```bash
curl -X POST https://upwork-xxsc.onrender.com/webhook/vollna \
  -H "Content-Type: application/json" \
  -H "X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394" \
  -d '[{
    "title": "Test Job",
    "url": "https://www.upwork.com/jobs/~test",
    "budget": 50.0,
    "client_name": "Test Client"
  }]'
```

#### Check Filter Endpoint:
```bash
curl -X POST https://upwork-xxsc.onrender.com/api/jobs/filter/vollna \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["Python"]}'
```

## 🐛 Enable Debug Logs

### Backend Logs (Render)

1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. You'll see real-time logs including:
   - Webhook requests
   - Job insertions
   - Filter queries
   - Errors

### Local Backend Logs

If running locally:
```bash
cd backend
LOG_LEVEL=DEBUG python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Console

Open browser DevTools (F12) → Console tab to see:
- API calls
- Job fetching
- Filter requests
- Errors

## ✅ Verification Checklist

### Backend Working:
- [ ] Health endpoint returns `{"status":"ok"}`
- [ ] `/jobs/all` returns jobs
- [ ] Webhook accepts POST requests
- [ ] Jobs are stored in database

### Vollna Webhook Working:
- [ ] Test job sent via webhook is stored
- [ ] Job appears in `/jobs/all` response
- [ ] Job has correct fields (title, budget, client_name, etc.)

### Frontend Working:
- [ ] Dashboard loads jobs
- [ ] Jobs appear in Job Queue table
- [ ] Metrics cards show correct counts
- [ ] Filters apply correctly

## 🔍 Troubleshooting

### No Jobs Appearing?

1. **Check if jobs exist:**
   ```bash
   curl https://upwork-xxsc.onrender.com/jobs/all
   ```

2. **Check webhook is receiving:**
   - Look at Render logs
   - Check for webhook POST requests
   - Verify authentication (X-N8N-Secret header)

3. **Check frontend:**
   - Open browser console (F12)
   - Look for API errors
   - Check network tab for failed requests

### Webhook Not Triggering?

1. **Verify Vollna/n8n setup:**
   - Check Vollna extension is active
   - Verify n8n workflow is running
   - Check webhook URL is correct: `https://upwork-xxsc.onrender.com/webhook/vollna`

2. **Check authentication:**
   - Verify `X-N8N-Secret` header matches
   - Check Render environment variable `N8N_SHARED_SECRET`

3. **Test manually:**
   ```bash
   ./test_vollna_webhook.sh
   ```

### Jobs Not Showing on Frontend?

1. **Check API endpoint:**
   - Frontend calls `/jobs/all`
   - Verify response format: `{count: number, jobs: [...]}`

2. **Check CORS:**
   - Verify `CORS_ORIGINS` includes your frontend URL
   - Check browser console for CORS errors

3. **Check filters:**
   - Clear localStorage: `localStorage.removeItem('bd-filtered-jobs')`
   - Refresh page
   - Apply filters again

## 📊 Monitoring Commands

### Watch Jobs in Real-Time:
```bash
python3 monitor_vollna_jobs.py
```

### Test Webhook:
```bash
./test_vollna_webhook.sh
```

### Check Job Count:
```bash
curl -s https://upwork-xxsc.onrender.com/jobs/all | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'Total jobs: {d.get(\"count\", 0)}')"
```

### View Latest Jobs:
```bash
curl -s https://upwork-xxsc.onrender.com/jobs/all | python3 -c "import sys, json; d=json.load(sys.stdin); [print(f'{i+1}. {j.get(\"title\")} - ${j.get(\"budget\")} - {j.get(\"client_name\")}') for i, j in enumerate(d.get('jobs', [])[:10])]"
```

---

**Use these tools to monitor and debug your Vollna integration!** 🚀

