# Vollna Debug Checklist - Verify Everything is Working

## ✅ Quick Verification

### 1. Check Current Jobs
```bash
./show_jobs.sh
```

**Expected Output:**
```
📊 Current Jobs in Database
============================

Total jobs: 4

1. Test Job from Vollna Monitor 1766178273
   ID: 6945bde23d4433f799180f94
   Budget: $75.0/hr
   Client: Test Client

2. Full Stack Developer
   ID: 6945b1d6a95fdc350f9ae31c
   Budget: $90.0/hr
   Client: Enterprise Co

3. React Frontend Developer
   ID: 6945b1d5a95fdc350f9ae31b
   Budget: $60.0/hr
   Client: Startup Inc

4. Python Developer Needed
   ID: 6945b1b2a95fdc350f9ae31a
   Budget: $75.0/hr
   Client: Tech Corp
```

### 2. Test Webhook
```bash
./test_vollna_webhook.sh
```

**What to Look For:**
- ✅ Backend health: `{"status":"ok"}`
- ✅ Jobs count increases after sending test job
- ✅ Webhook returns: `{"received":1,"inserted":1,"errors":0}`

### 3. Monitor in Real-Time
```bash
python3 monitor_vollna_jobs.py
```

**What to Watch:**
- Job count changes
- New jobs appear with titles and IDs
- Timestamps show when jobs arrive

## 🔍 Enable Debug Mode

### Backend (Render)

1. Go to Render Dashboard
2. Select service → Environment
3. Add/Update: `LOG_LEVEL=DEBUG`
4. Save and redeploy

### View Logs

**Render Dashboard → Logs Tab**

You'll see:
```
INFO: Received Vollna webhook payload: dict
INFO: Processing 1 jobs from Vollna
DEBUG: Inserted job 0: Python Developer Needed
INFO: Vollna webhook processed: 1 received, 1 inserted, 0 errors
INFO: GET /jobs/all - Fetching all Vollna jobs
INFO: GET /jobs/all - Returning 4 jobs
```

## ✅ Verification Steps

### Step 1: Backend Health
```bash
curl https://upwork-xxsc.onrender.com/health
```
**Expected:** `{"status":"ok","database":"connected"}`

### Step 2: Jobs Endpoint
```bash
curl https://upwork-xxsc.onrender.com/jobs/all
```
**Expected:** `{"count":4,"jobs":[...]}`

### Step 3: Webhook Test
```bash
curl -X POST https://upwork-xxsc.onrender.com/webhook/vollna \
  -H "Content-Type: application/json" \
  -H "X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394" \
  -d '[{"title": "Test", "url": "https://upwork.com/jobs/~test", "budget": 50, "client_name": "Test"}]'
```
**Expected:** `{"received":1,"inserted":1,"errors":0}`

### Step 4: Frontend Check
1. Open `http://localhost:8080`
2. Press F12 (DevTools)
3. Check Console for:
   - `Fetched X jobs from /jobs/all`
   - No errors
4. Check Network tab:
   - Request to `/jobs/all` returns 200
   - Response shows jobs array

## 🎯 What Indicates Vollna is Working

### ✅ Good Signs:
- Jobs appear in `/jobs/all` endpoint
- Job count increases over time
- Render logs show webhook requests
- Frontend displays jobs
- Job titles and IDs are visible

### ❌ Problem Signs:
- Job count stays at 0
- No webhook requests in logs
- Frontend shows "No jobs found"
- Webhook returns errors

## 🚀 Next Steps

1. **Monitor jobs:**
   ```bash
   python3 monitor_vollna_jobs.py
   ```

2. **Check Render logs** for webhook activity

3. **Verify frontend** shows jobs at `http://localhost:8080`

4. **Test filters** on Job Filters page

---

**Use these tools to verify Vollna is working!** 🎉

