# 🔍 Vollna Webhook Debug Guide

## ✅ What's Been Added

### 1. Enhanced Debug Logging
The webhook endpoint (`/webhook/vollna`) now logs:
- 🔹 **Webhook hit notification**
- 🔹 **Payload type** (dict, list, etc.)
- 🔹 **Full payload content** (what Vollna sends)
- 🔹 **Request headers** (for debugging auth issues)

### 2. Test Scripts
- `test_webhook.py` - Full test with sample job payload
- `test_webhook_oneliner.py` - Simple one-liner test

---

## 🧪 Quick Test (Python One-Liner)

### Option 1: Run the Script
```bash
python3 test_webhook_oneliner.py
```

### Option 2: Python Shell (Copy & Paste)
```python
import urllib.request
import json

url = "https://upwork-xxsc.onrender.com/webhook/vollna"
secret = "9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394"
test_payload = {"test": "hello"}

data = json.dumps(test_payload).encode('utf-8')
req = urllib.request.Request(
    url,
    data=data,
    headers={"Content-Type": "application/json", "X-N8N-Secret": secret},
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        print("Status code:", response.getcode())
        print("Response:", response.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)
```

---

## 📊 What You'll See

### In Backend Logs (Render Dashboard)
When a webhook is received, you'll see:
```
INFO: 🔹 Webhook hit! /webhook/vollna
INFO: 🔹 Payload type: dict
INFO: 🔹 Payload received: {'title': '...', 'url': '...', ...}
DEBUG: 🔹 Request headers: {'host': '...', 'x-n8n-secret': '...', ...}
INFO: Processing 1 jobs from Vollna
INFO: Vollna webhook processed: 1 received, 1 inserted, 0 errors
```

### In Test Script Output
```
✅ Status code: 200
📥 Response:
{
  "received": 1,
  "inserted": 1,
  "errors": 0,
  "error_details": null
}
```

---

## 🔍 How to View Real Vollna Payloads

### Step 1: Check Render Logs
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your service: `upwork-xxsc`
3. Click **Logs** tab
4. Watch for: `🔹 Webhook hit!` and `🔹 Payload received:`

### Step 2: Test with Real Vollna
1. Ensure Vollna is configured with webhook URL:
   ```
   https://upwork-xxsc.onrender.com/webhook/vollna
   ```
2. Enable Vollna to send jobs
3. Check Render logs for incoming payloads

### Step 3: Verify Jobs Were Stored
```bash
# Check all jobs
python3 analyze_jobs.py

# Or use curl
curl -s https://upwork-xxsc.onrender.com/jobs/all | python3 -m json.tool | head -50
```

---

## 🐛 Troubleshooting

### Webhook Not Receiving Requests
1. **Check URL**: Verify Vollna is pointing to correct endpoint
2. **Check Auth**: Ensure `X-N8N-Secret` header matches your `.env` value
3. **Check Logs**: Look for `🔹 Webhook hit!` in Render logs

### Payload Not Showing in Logs
- Check Render logs are enabled
- Verify webhook endpoint is `/webhook/vollna` (not `/vollna/jobs`)
- Check if requests are being blocked by CORS or auth

### Jobs Not Appearing in Database
- Check webhook response: `"inserted": 1` means success
- Run `python3 analyze_jobs.py` to see stored jobs
- Check for errors in webhook response: `"error_details"`

---

## 📝 Example: Real Vollna Payload Structure

When Vollna sends a job, the payload might look like:
```json
{
  "title": "Python Developer Needed",
  "url": "https://www.upwork.com/jobs/...",
  "description": "We need a Python developer...",
  "budget": 50.0,
  "client_name": "John Doe",
  "skills": ["Python", "Django"],
  "proposals": 3,
  "postedOn": "2025-12-19T10:00:00Z",
  "platform": "upwork"
}
```

The debug logs will show **exactly** what Vollna sends, so you can verify the structure matches your expectations.

---

## ✅ Next Steps

1. **Test the webhook**: Run `python3 test_webhook_oneliner.py`
2. **Check Render logs**: Verify debug output appears
3. **Configure Vollna**: Ensure it's sending to the correct URL
4. **Monitor for real jobs**: Watch logs for incoming Upwork jobs

