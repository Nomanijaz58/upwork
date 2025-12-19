# Quick Vollna Check - Get Real Jobs

## ✅ Run This First

```bash
python3 analyze_jobs.py
```

This will show you:
- How many **real jobs** vs **test jobs** you have
- Which jobs are real (from Upwork)
- Which jobs are test (from scripts - ignore these)

## 📋 Complete Checklist

### STEP 1️⃣: Vollna Webhook Config

**Check in Vollna Extension/Dashboard:**
- ✅ URL: `https://upwork-xxsc.onrender.com/webhook/vollna`
- ✅ Enabled: `true`
- ✅ Header: `X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394`

### STEP 2️⃣: Stop Test Scripts

**Don't run:**
```bash
./test_vollna_webhook.sh  # Creates fake jobs
```

**Use instead:**
```bash
python3 analyze_jobs.py      # Analyze jobs (read-only)
python3 monitor_vollna_jobs.py  # Monitor for new jobs (read-only)
```

### STEP 3️⃣: Enable Real Upwork Feeds

**In Vollna Extension:**
- ✅ Keywords: Add 1-2 keywords (e.g., "Python")
- ✅ Sections: Enable "Best Match" and "Most Recent"
- ⚠️ Country filters: **DISABLE** temporarily
- ⚠️ Budget filters: Start with no filter or very broad

### STEP 4️⃣: Watch Vollna Logs

**Check Vollna Extension Logs:**
- Look for: "Sending job to webhook"
- Look for: "Webhook response: 200"

**Check Render Backend Logs:**
- Go to: https://dashboard.render.com → Your service → Logs
- Look for: "Received Vollna webhook payload"

**If you DON'T see "sending to webhook" in Vollna logs:**
- Real jobs will never arrive
- Check webhook configuration
- Verify Vollna is monitoring Upwork pages

## 🎯 What Real Jobs Look Like

**Real Upwork Jobs:**
- URL: `https://www.upwork.com/jobs/~abc123def456` (long alphanumeric)
- Client: Real company/person names
- Title: Actual job titles from Upwork

**Test Jobs (ignore these):**
- URL: `https://www.upwork.com/jobs/~test123`
- Client: "Test Client", "Tech Corp"
- Title: "Test Job from Vollna Monitor"

## 🚀 Quick Commands

```bash
# Analyze jobs (test vs real)
python3 analyze_jobs.py

# Monitor for new jobs
python3 monitor_vollna_jobs.py

# Show current jobs
./show_jobs.sh
```

---

**Run `python3 analyze_jobs.py` to see what you have!** 🎉

