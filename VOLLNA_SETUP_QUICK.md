# Quick Setup: Get Real Upwork Jobs from Vollna

## 🎯 What You Need

1. **Vollna Extension** installed in Chrome
2. **Webhook URL** configured in Vollna
3. **Upwork page** being monitored

## ⚡ Quick Setup (5 Minutes)

### Step 1: Install Vollna Extension

1. Go to Chrome Web Store
2. Search "Vollna"
3. Install extension
4. Login to Vollna

### Step 2: Configure Webhook in Vollna

**Webhook URL:**
```
https://upwork-xxsc.onrender.com/webhook/vollna
```

**Headers:**
```
X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394
Content-Type: application/json
```

**How to add:**
1. Open Vollna extension
2. Go to Settings → Integrations
3. Add Webhook
4. Paste URL and headers above
5. Enable "Send job alerts"
6. Save

### Step 3: Enable Monitoring on Upwork

1. Go to https://www.upwork.com/nx/find-work/best-matches
2. Click Vollna extension icon
3. Enable "Monitor this page"
4. Vollna will now send jobs to your backend

### Step 4: Monitor Jobs

```bash
# Watch for new jobs in real-time
python3 monitor_vollna_jobs.py
```

## ✅ Verification

### Check if Jobs Are Coming:

```bash
# Show current jobs
./show_jobs.sh

# Check backend
curl https://upwork-xxsc.onrender.com/jobs/all
```

### Check Render Logs:

1. Go to Render Dashboard
2. Select service → Logs
3. Look for: `Received Vollna webhook payload`

### Check Frontend:

1. Open `http://localhost:8080`
2. Jobs should appear automatically
3. New jobs appear within 10-15 seconds

## 🎯 What Real Jobs Look Like

**Real Upwork jobs will have:**
- ✅ Real Upwork URLs: `https://www.upwork.com/jobs/~abc123def456`
- ✅ Real client names from Upwork
- ✅ Real job titles
- ✅ Real budgets and proposals
- ✅ Real skills and descriptions

**Test jobs have:**
- ❌ Test URLs: `https://www.upwork.com/jobs/~test123`
- ❌ Test client names: "Test Client"
- ❌ Test titles: "Test Job from Vollna Monitor"

## 🐛 Troubleshooting

### No Jobs Coming?

1. **Check Vollna extension is active**
2. **Check webhook URL is correct**
3. **Check Render logs for webhook requests**
4. **Verify Upwork has new jobs**

### Jobs Not Appearing?

1. **Check database:** `./show_jobs.sh`
2. **Check frontend console** (F12)
3. **Clear filters** on Job Filters page

---

**Configure Vollna webhook and real jobs will start flowing!** 🚀

