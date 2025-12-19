# Setup Real-Time Upwork Jobs from Vollna

## 🎯 Goal

Get **real Upwork jobs** flowing from Vollna → Backend → Frontend automatically.

## 📋 Current Situation

- ✅ Backend is ready and working
- ✅ Webhook endpoint is configured: `https://upwork-xxsc.onrender.com/webhook/vollna`
- ✅ Database is ready to receive jobs
- ⏳ **Need to configure Vollna to send real jobs**

## 🔄 Complete Workflow

```
Upwork Website → Vollna Extension → n8n Webhook → Backend → MongoDB → Frontend
```

## ✅ Step-by-Step Setup

### Step 1: Install Vollna Extension

1. **Install Vollna Chrome Extension**
   - Go to Chrome Web Store
   - Search for "Vollna"
   - Install the extension

2. **Login to Vollna**
   - Open Vollna extension
   - Login with your account

### Step 2: Configure Vollna to Monitor Upwork

1. **Go to Upwork** (https://www.upwork.com)
2. **Set up your job search**:
   - Go to "Find Work" → "Best Matches" or "Most Recent"
   - Apply your filters (keywords, budget, skills, etc.)
   - Save the search if needed

3. **Enable Vollna on Upwork page**:
   - Click Vollna extension icon
   - Enable "Monitor this page"
   - Vollna will detect new jobs on the page

### Step 3: Configure Vollna Webhook

**Option A: Direct to Backend (Simplest)**

1. **Get your webhook URL:**
   ```
   https://upwork-xxsc.onrender.com/webhook/vollna
   ```

2. **Get your secret:**
   ```
   9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394
   ```

3. **In Vollna Dashboard/Settings:**
   - Go to Integrations → Webhooks
   - Add new webhook:
     - **URL**: `https://upwork-xxsc.onrender.com/webhook/vollna`
     - **Method**: `POST`
     - **Headers**:
       - `X-N8N-Secret`: `9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394`
       - `Content-Type`: `application/json`
   - Enable "Send job alerts"
   - Save

**Option B: Via n8n (Recommended for flexibility)**

1. **Set up n8n workflow**:
   - Create webhook trigger in n8n
   - Forward to backend with authentication

2. **Configure Vollna to send to n8n**:
   - Vollna webhook URL: `https://your-n8n-instance.com/webhook/vollna`
   - n8n forwards to: `https://upwork-xxsc.onrender.com/webhook/vollna`

### Step 4: Verify Setup

1. **Check Vollna is monitoring**:
   - Go to Upwork jobs page
   - Vollna extension should show "Monitoring" status
   - Check Vollna dashboard for detected jobs

2. **Test webhook**:
   ```bash
   ./test_vollna_webhook.sh
   ```

3. **Monitor for real jobs**:
   ```bash
   python3 monitor_vollna_jobs.py
   ```

## 🔍 How to Verify Real Jobs Are Coming

### Method 1: Monitor in Terminal

```bash
python3 monitor_vollna_jobs.py
```

**What to look for:**
- New jobs appear with real Upwork titles
- Job URLs point to real Upwork job pages
- Jobs have real client names and budgets
- Jobs arrive as new Upwork jobs are posted

### Method 2: Check Render Logs

1. Go to Render Dashboard → Logs
2. Look for:
   ```
   INFO: Received Vollna webhook payload: dict
   INFO: Processing X jobs from Vollna
   DEBUG: Inserted job 0: [Real Upwork Job Title]
   ```

### Method 3: Check Database

```bash
./show_jobs.sh
```

**Real jobs will have:**
- Real Upwork URLs (e.g., `https://www.upwork.com/jobs/~abc123def456`)
- Real client names
- Real job titles from Upwork
- Real budgets and proposals

### Method 4: Check Frontend

1. Open `http://localhost:8080`
2. Jobs should appear automatically
3. Click "View" on a job → Should open real Upwork job page

## 🎯 Vollna Configuration Details

### Required Fields in Vollna Webhook Payload

Vollna should send jobs with these fields:
- `title` - Job title (required)
- `url` - Upwork job URL (required)
- `budget` - Budget amount (required)
- `client_name` - Client name (required)
- `description` - Job description (optional)
- `skills` - Array of skills (optional)
- `proposals` - Number of proposals (optional)
- `posted_at` or `postedOn` - Posting date (optional)

### Webhook Payload Format

Vollna can send jobs in these formats (all supported):

**Single Job:**
```json
{
  "title": "Python Developer Needed",
  "url": "https://www.upwork.com/jobs/~abc123",
  "budget": 75.0,
  "client_name": "Tech Corp"
}
```

**Multiple Jobs:**
```json
[
  {"title": "Job 1", "url": "...", "budget": 50, "client_name": "Client 1"},
  {"title": "Job 2", "url": "...", "budget": 75, "client_name": "Client 2"}
]
```

**Wrapped:**
```json
{
  "jobs": [
    {"title": "Job 1", "url": "...", "budget": 50, "client_name": "Client 1"}
  ]
}
```

## 🐛 Troubleshooting

### No Real Jobs Coming?

1. **Check Vollna Extension:**
   - Is extension enabled?
   - Is it monitoring the Upwork page?
   - Check Vollna dashboard for detected jobs

2. **Check Webhook Configuration:**
   - Verify webhook URL is correct
   - Verify secret header is set
   - Test webhook manually: `./test_vollna_webhook.sh`

3. **Check Render Logs:**
   - Look for webhook requests
   - Check for errors
   - Verify authentication

4. **Check Upwork:**
   - Are there new jobs on Upwork?
   - Is your search/filter active?
   - Are jobs matching your criteria?

### Jobs Not Appearing on Frontend?

1. **Check API:**
   ```bash
   curl https://upwork-xxsc.onrender.com/jobs/all
   ```
   - If jobs are here, frontend issue
   - If no jobs, backend/webhook issue

2. **Check Frontend Console:**
   - Open DevTools (F12)
   - Look for API errors
   - Check network requests

3. **Clear Filters:**
   - Go to Job Filters page
   - Click "Reset to Defaults"
   - Refresh dashboard

## 📊 Expected Behavior

### When Real Jobs Arrive:

1. **Vollna detects** new job on Upwork
2. **Vollna sends** job to webhook
3. **Backend receives** and stores job
4. **Frontend polls** `/jobs/all` every 10 seconds
5. **New job appears** in dashboard automatically

### Job Flow Timeline:

```
00:00 - New job posted on Upwork
00:05 - Vollna detects job
00:06 - Vollna sends to webhook
00:07 - Backend stores in database
00:10 - Frontend polls and displays job
```

## 🚀 Quick Start Commands

```bash
# 1. Show current jobs
./show_jobs.sh

# 2. Test webhook
./test_vollna_webhook.sh

# 3. Monitor for new jobs
python3 monitor_vollna_jobs.py

# 4. Check backend health
curl https://upwork-xxsc.onrender.com/health
```

## ✅ Next Steps

1. **Configure Vollna** to send jobs to your webhook
2. **Enable monitoring** on Upwork pages
3. **Watch for real jobs** using `python3 monitor_vollna_jobs.py`
4. **Verify jobs appear** on frontend dashboard

---

**Once Vollna is configured, real Upwork jobs will flow automatically!** 🎉

