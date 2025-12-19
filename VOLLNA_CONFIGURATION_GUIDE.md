# Vollna Configuration Guide - Get Real Upwork Jobs

## 🎯 Goal

Configure Vollna to send **real Upwork jobs** (not test jobs) to your backend.

## ✅ STEP 1️⃣: Check Vollna Webhook Config

### Required Settings:

**Webhook URL:**
```
https://upwork-xxsc.onrender.com/webhook/vollna
```

**Headers:**
```
X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394
Content-Type: application/json
```

**Status:**
- ✅ **Enabled**: `true`
- ✅ **Method**: `POST`

### How to Verify:

1. **Open Vollna Extension** (click extension icon in Chrome)
2. **Go to**: Settings → Integrations → Webhooks
3. **Check**: 
   - Webhook URL matches above
   - "Send job alerts" is enabled
   - Headers are configured

---

## ✅ STEP 2️⃣: Disable Test Scripts

### ❌ Stop Running These:

```bash
./test_vollna_webhook.sh  # Creates fake test jobs
```

### ✅ Use These Instead (Read-Only):

```bash
./show_jobs.sh            # Shows current jobs (doesn't create new ones)
python3 analyze_jobs.py   # Analyzes jobs (identifies test vs real)
python3 monitor_vollna_jobs.py  # Monitors for NEW jobs (read-only)
```

### Why?

Test scripts create jobs with:
- URLs: `https://www.upwork.com/jobs/~test123` ❌
- Clients: "Test Client" ❌
- Titles: "Test Job from Vollna Monitor" ❌

These pollute your database and hide real jobs.

---

## ✅ STEP 3️⃣: Enable REAL Upwork Feeds

### Vollna Extension Settings:

#### 1. Keywords:
- ✅ **Add 1-2 keywords** (e.g., "Python", "React")
- ⚠️ **Don't over-filter** - Start simple
- ✅ **Use broad terms** to get more jobs initially

#### 2. Sections:
- ✅ **Best Match**: Enable
- ✅ **Most Recent**: Enable
- ✅ **Saved Searches**: Enable if you have any

#### 3. Country Filters:
- ⚠️ **TEMPORARILY DISABLE** all country exclusions
- ✅ **Allow all locations** for now
- ✅ **Re-enable later** once jobs are flowing

#### 4. Budget Filters:
- ⚠️ **Start with no filter** or very broad (e.g., $0-$200)
- ✅ **Narrow down later** once confirmed working

### Configuration Steps:

1. **Open Vollna Extension**
2. **Go to**: Filters/Settings
3. **Set**:
   - Keywords: 1-2 keywords (e.g., "Python")
   - Country exclusions: **DISABLED** (temporarily)
   - Sections: **ALL enabled**
4. **Save**

---

## ✅ STEP 4️⃣: Watch Vollna Logs

### What You Should See:

#### ✅ Good Signs (Vollna is Working):

In **Vollna Extension Logs**:
```
✅ "Fetched job from Upwork"
✅ "Sending job to webhook"
✅ "Webhook response: 200 OK"
✅ "Job sent successfully"
```

In **Render Backend Logs**:
```
✅ "Received Vollna webhook payload"
✅ "Processing X jobs from Vollna"
✅ "Inserted job X: [Real Job Title]"
```

#### ❌ Problem Signs:

```
❌ "Webhook failed"
❌ "No jobs found"
❌ "Webhook URL not configured"
❌ "Authentication failed"
❌ No webhook activity in logs
```

### Where to Check:

#### Option 1: Vollna Extension
1. Click Vollna extension icon
2. Check "Activity" or "Logs" tab
3. Look for "Sending job to webhook" messages

#### Option 2: Render Backend Logs
1. Go to: https://dashboard.render.com
2. Select: `upwork-xxsc` service
3. Click: "Logs" tab
4. Look for: `Received Vollna webhook payload`

#### Option 3: Terminal Monitor
```bash
python3 monitor_vollna_jobs.py
```
Watch for new jobs appearing in real-time.

---

## 🔍 How to Identify Real vs Test Jobs

### Real Upwork Jobs:
- ✅ **URLs**: `https://www.upwork.com/jobs/~abc123def456` (long alphanumeric)
- ✅ **Clients**: Real company/person names
- ✅ **Titles**: Actual job titles from Upwork
- ✅ **Budgets**: Real hourly/fixed rates
- ✅ **Skills**: Skills from actual postings

### Test Jobs:
- ❌ **URLs**: `https://www.upwork.com/jobs/~test123`
- ❌ **Clients**: "Test Client", "Tech Corp" (generic)
- ❌ **Titles**: "Test Job from Vollna Monitor"
- ❌ **Created by**: Test scripts

---

## 🧪 Quick Verification

### Analyze Current Jobs:
```bash
python3 analyze_jobs.py
```

This will show:
- How many real jobs vs test jobs
- Which jobs are real
- Which jobs are test (to ignore)

### Monitor for New Jobs:
```bash
python3 monitor_vollna_jobs.py
```

Watch for new real jobs as they arrive.

---

## 📋 Complete Checklist

- [ ] **Vollna webhook URL**: `https://upwork-xxsc.onrender.com/webhook/vollna`
- [ ] **Webhook enabled**: `true`
- [ ] **X-N8N-Secret header**: Configured
- [ ] **Test scripts stopped**: Not running `test_vollna_webhook.sh`
- [ ] **Keywords configured**: At least 1 keyword
- [ ] **Sections enabled**: Best Match, Most Recent
- [ ] **Country filters**: Temporarily disabled
- [ ] **Vollna extension active**: Monitoring Upwork
- [ ] **Vollna logs show**: "Sending job to webhook"
- [ ] **Render logs show**: "Received Vollna webhook payload"
- [ ] **Real jobs appearing**: Not just test jobs

---

## 🚀 Expected Flow

1. **New job posted** on Upwork
2. **Vollna detects** it (if matches your keywords)
3. **Vollna sends** to webhook: `https://upwork-xxsc.onrender.com/webhook/vollna`
4. **Backend receives** and stores in `vollna_jobs` collection
5. **Frontend polls** `/jobs/all` every 10 seconds
6. **Job appears** on dashboard automatically

**Timeline**: Usually 10-30 seconds from Upwork posting to frontend display.

---

**Follow this guide to get real Upwork jobs flowing!** 🎉

