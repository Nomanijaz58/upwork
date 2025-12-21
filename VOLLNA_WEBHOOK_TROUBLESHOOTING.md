# Vollna Webhook Troubleshooting Guide

## Current Status

Your webhook is receiving requests, but jobs aren't being inserted because the payload structure doesn't contain job data with `title` and `url` fields.

**Log evidence:**
```
WARNING: Skipping incomplete job payload (missing title or URL): title=False, url=False
```

## Step 1: Check Render Logs for Payload Structure

### Option A: Via Render Dashboard

1. Go to https://dashboard.render.com
2. Navigate to your service: **upwork-proposal-bot**
3. Click on **"Logs"** in the left sidebar
4. Look for recent entries containing:
   - `🔹 Webhook hit! /webhook/vollna`
   - `🔹 Payload keys: [...]`
   - `First job structure - keys: [...]`
   - `Skipping incomplete job payload`

### Option B: Via Render API (if you have API access)

You can also stream logs via the Render API or web interface.

### What to Look For

Look for log entries that show:
- **Payload keys**: What fields are in the root payload
- **First job structure - keys**: What fields are in each job object
- **Sample job**: The actual job data structure

**Expected structure** (what we need):
```json
{
  "jobs": [
    {
      "title": "Job Title",
      "url": "https://www.upwork.com/jobs/~abc123",
      "description": "...",
      "budget": 50,
      "proposals": 5,
      "skills": ["Python"],
      "client_name": "Client Name",
      "posted_at": "2025-12-21T04:26:00Z"
    }
  ]
}
```

**Current structure** (what you're likely seeing):
```json
{
  "filter": {
    "id": 28281,
    "name": "JOB FILTER"
  },
  "event": "filter.match",  // or similar
  // Missing actual job data!
}
```

## Step 2: Verify Vollna Webhook Settings

### In Vollna Dashboard:

1. **Navigate to Filter Settings**
   - Go to your filter (the one showing +5, +4, +3 new jobs)
   - Click on the filter settings/edit

2. **Check Webhook Configuration**
   - Look for "Webhook" or "Integration" settings
   - Verify the webhook URL: `https://upwork-xxsc.onrender.com/webhook/vollna`
   - Verify authentication header is set:
     - Header: `X-N8N-Secret`
     - Value: `9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394`

3. **Check Payload/Data Format Settings**
   - Look for options like:
     - "Send job data" ✅ (should be enabled)
     - "Include job details" ✅ (should be enabled)
     - "Send job objects" ✅ (should be enabled)
     - "Test mode" ❌ (should be disabled)
   - Look for payload format options:
     - Should send actual job objects, not just notifications
     - Should include fields: `title`, `url`, `description`, `budget`, etc.

4. **Check Notification Settings**
   - Vollna might have separate notification settings vs webhook settings
   - Make sure webhooks send actual job data, not just filter match notifications
   - Look for options to send "full job payload" or "complete job data"

### Common Vollna Webhook Configurations:

**Option 1: Send Jobs Array**
```json
{
  "jobs": [
    {"title": "...", "url": "...", ...},
    {"title": "...", "url": "...", ...}
  ]
}
```

**Option 2: Send Individual Jobs**
Each webhook call sends one job:
```json
{
  "title": "Job Title",
  "url": "https://...",
  ...
}
```

**Option 3: Send Wrapped Format**
```json
{
  "data": {
    "jobs": [...]
  }
}
```

## Step 3: What the Updated Code Does

The updated webhook handler (`vollna_simple.py`) now:

1. **Better Payload Extraction**
   - Handles nested structures (`{"data": {"jobs": [...]}}`)
   - Handles filter metadata (`{"filter": {...}, "jobs": [...]}`)
   - Handles multiple formats (array, object, wrapped)

2. **Enhanced Logging**
   - Shows payload keys for debugging
   - Shows first job structure
   - Shows why jobs are being skipped

3. **Smart Filtering**
   - Skips test events (`event: "webhook.test"`)
   - Skips filter metadata objects
   - Only processes objects with `title` and `url`

## Step 4: Testing

### Test the Webhook Manually

Once you've configured Vollna correctly, you can test with:

```bash
curl -X POST https://upwork-xxsc.onrender.com/webhook/vollna \
  -H "Content-Type: application/json" \
  -H "X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f100b2aa394" \
  -d '{
    "jobs": [
      {
        "title": "Test Python Developer",
        "url": "https://www.upwork.com/jobs/~test123",
        "description": "Test job description",
        "budget": 50,
        "proposals": 5,
        "skills": ["Python"],
        "client_name": "Test Client",
        "posted_at": "2025-12-21T10:00:00Z"
      }
    ]
  }'
```

### Verify Jobs Are Being Inserted

```bash
curl https://upwork-xxsc.onrender.com/jobs/all | python3 -m json.tool
```

## Step 5: If Vollna Sends Different Format

If Vollna sends jobs in a format we're not handling, you'll see it in the logs. Share the log output showing:
- `Payload keys: [...]`
- `First job structure - keys: [...]`

And we can update the code to handle that specific format.

## Current Code Status

✅ Webhook endpoint is working  
✅ Authentication is working  
✅ Test events are being skipped correctly  
❌ Real job data structure needs to match what Vollna sends  
❌ Vollna configuration needs to send actual job objects

## Next Actions

1. **Check Render logs** to see the exact payload structure
2. **Update Vollna webhook settings** to send actual job data
3. **Monitor logs** after changes to see if jobs start inserting
4. **Share log output** if you need help adjusting the code for a specific format

