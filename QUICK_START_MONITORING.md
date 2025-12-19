# Quick Start: Monitor Vollna Jobs

## ✅ Everything is Working!

The test script confirmed:
- ✅ Backend is healthy
- ✅ Webhook accepts jobs
- ✅ Jobs are stored in database
- ✅ Filter endpoint works
- ✅ **4 jobs currently in database**

## 🚀 How to Monitor Vollna in Real-Time

### Option 1: Python Monitor (Recommended)

Watch for new jobs as they arrive:

```bash
# Monitor new jobs only (shows only when new jobs arrive)
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
Refresh interval: 5 seconds
Watch mode: ON (shows only new jobs)
================================================================================

⏰ [2025-12-20 01:50:00] Job count changed: 4 → 5

🆕 Found 1 new job(s)!

================================================================================
Job #1
================================================================================
📋 Title:     New Job from Vollna
🆔 ID:        6945bde23d4433f799180f94
💰 Budget:    $75.0/hr
👤 Client:    Test Client
📅 Created:   2025-12-19T21:04:34.876000
🔗 URL:       https://www.upwork.com/jobs/~test123
🛠️  Skills:    Python, FastAPI, Testing
📊 Proposals:  5
================================================================================
```

### Option 2: Quick Test Script

Run a one-time test:

```bash
./test_vollna_webhook.sh
```

This will:
1. Check backend health
2. Show current jobs
3. Send a test job
4. Verify it was stored
5. Test filters

### Option 3: Manual API Checks

#### Check Current Jobs:
```bash
curl https://upwork-xxsc.onrender.com/jobs/all | python3 -m json.tool
```

#### View Job Titles and IDs:
```bash
curl -s https://upwork-xxsc.onrender.com/jobs/all | python3 -c "
import sys, json
d = json.load(sys.stdin)
jobs = d.get('jobs', [])
print(f'Total jobs: {len(jobs)}')
print('\nJobs:')
for i, j in enumerate(jobs, 1):
    print(f'{i}. {j.get(\"title\")} (ID: {j.get(\"_id\")})')
"
```

## 🔍 Enable Debug Logs

### Backend Logs (Render)

1. Go to https://dashboard.render.com
2. Select your service (`upwork-xxsc`)
3. Click **"Logs"** tab
4. You'll see real-time logs:
   - `Received Vollna webhook payload`
   - `Processing X jobs from Vollna`
   - `Inserted job X: [title]`
   - `GET /jobs/all - Returning X jobs`

### Local Backend (if running locally)

```bash
cd backend
LOG_LEVEL=DEBUG python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Console

1. Open browser: `http://localhost:8080`
2. Press **F12** (DevTools)
3. Go to **Console** tab
4. You'll see:
   - `Fetched X jobs from /jobs/all`
   - API calls and responses
   - Any errors

## ✅ Verification Checklist

### Backend Working:
- [x] Health endpoint: `{"status":"ok"}`
- [x] `/jobs/all` returns jobs
- [x] Webhook accepts POST requests
- [x] Jobs stored in database

### Vollna Webhook Working:
- [x] Test job sent successfully
- [x] Job appears in `/jobs/all`
- [x] Job has correct fields

### Frontend Working:
- [ ] Dashboard loads jobs (check `http://localhost:8080`)
- [ ] Jobs appear in Job Queue table
- [ ] Metrics show correct counts

## 🎯 What to Watch For

### When Vollna Sends a Job:

1. **Backend Logs (Render)**:
   ```
   INFO: Received Vollna webhook payload: dict
   INFO: Processing 1 jobs from Vollna
   DEBUG: Inserted job 0: Python Developer
   INFO: Vollna webhook processed: 1 received, 1 inserted, 0 errors
   ```

2. **Python Monitor**:
   ```
   🆕 Found 1 new job(s)!
   📋 Title: Python Developer
   🆔 ID: 6945bde23d4433f799180f94
   ```

3. **Frontend**:
   - Job appears in dashboard
   - Job count increases
   - Metrics update

## 🐛 Troubleshooting

### No Jobs Appearing?

1. **Check if jobs exist:**
   ```bash
   curl https://upwork-xxsc.onrender.com/jobs/all
   ```

2. **Check webhook is receiving:**
   - Look at Render logs
   - Check for `Received Vollna webhook payload`
   - Verify authentication

3. **Check frontend:**
   - Open browser console (F12)
   - Look for API errors
   - Check network tab

### Webhook Not Triggering?

1. **Verify Vollna/n8n setup:**
   - Check Vollna extension is active
   - Verify n8n workflow is running
   - Check webhook URL: `https://upwork-xxsc.onrender.com/webhook/vollna`

2. **Test manually:**
   ```bash
   ./test_vollna_webhook.sh
   ```

## 📊 Current Status

- ✅ **4 jobs** in database
- ✅ Webhook endpoint working
- ✅ Filter endpoint working
- ✅ Backend healthy

---

**Start monitoring now:** `python3 monitor_vollna_jobs.py` 🚀

