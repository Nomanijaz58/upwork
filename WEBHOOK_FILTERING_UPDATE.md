# Webhook Filtering and Field Normalization Update

## ✅ Changes Implemented

### 1. Test Data Filtering

The webhook now automatically filters out:
- **Test webhook events**: `event == "webhook.test"`
- **Test jobs**: Jobs with "test" in the title (case-insensitive)
- **Incomplete jobs**: Jobs missing `title` or `url`

**Code Location**: `backend/app/routers/vollna_simple.py:120-145`

```python
# 🛑 Skip test messages and test jobs
if job.get("event") == "webhook.test":
    logger.info(f"Skipping test webhook payload (event: webhook.test)")
    continue

# Get title (check multiple possible fields)
job_title = job.get("title") or job.get("job_title") or job.get("name") or ""
if "test" in str(job_title).lower():
    logger.info(f"Skipping test job: {job_title}")
    continue

# ✅ Only process if it has a title and URL
job_url = job.get("url") or job.get("job_url") or job.get("link") or ""
if not job_title or not job_url:
    logger.warning(f"Skipping incomplete job payload (missing title or URL)")
    continue
```

### 2. Field Normalization

Vollna may send jobs with different field names. The webhook now normalizes them to standard fields:

| Vollna Field | Standard Field | Purpose |
|--------------|----------------|---------|
| `title` / `job_title` / `name` | `title` | Job heading |
| `url` / `job_url` / `link` | `url` | Link to Upwork |
| `formatted_budget` / `budget_value` / `hourly_rate` / `fixed_price` | `budget` | Budget value |
| `description` / `job_description` | `description` | Job details |
| `client.rating` / `client_rating` | `client_rating` | Client rating |
| `client.name` / `client_name` | `client_name` | Client name |
| `proposals` / `proposal_count` / `num_proposals` | `proposals` | Number of proposals |
| `skills` / `job_skills` | `skills` | Required skills |
| `posted_at` / `posted_on` / `created_at` | `posted_at` | Posting date |
| `location` / `country` / `region` | `location` | Job location |

**Code Location**: `backend/app/routers/vollna_simple.py:147-170`

```python
# Normalize job fields to standard format
doc = {
    "title": job_title,
    "url": job_url,
    "description": job.get("description") or job.get("job_description") or "",
    "budget": job.get("budget") or job.get("formatted_budget") or ...,
    "client_name": job.get("client_name") or (job.get("client", {}).get("name") if ...),
    # ... etc
    "raw": job,  # Preserve original payload
}
```

### 3. Enhanced Logging

The webhook now logs:
- ✅ Successful insertions with job title and URL preview
- ⚠️ Skipped test jobs with reason
- ⚠️ Skipped incomplete jobs with missing fields

**Example Log Output**:
```
🔹 Webhook hit! /webhook/vollna
✅ Bearer token authentication successful
Processing 3 jobs from Vollna
Skipping test job: Test Job from Vollna
Skipping incomplete job payload (missing title or URL): title=False, url=True
✅ Inserted job 0: Python Developer Needed... (URL: https://www.upwork.com/jobs/~abc123...)
Vollna webhook processed: 3 received, 1 inserted, 0 errors
```

---

## 🧹 Database Cleanup

### Clean Up Incomplete Jobs

Run this to remove jobs missing title or URL:

```python
# Using MongoDB shell or Python script
db.vollna_jobs.deleteMany({
    $or: [
        {title: {$exists: false}},
        {title: null},
        {title: ""},
        {url: {$exists: false}},
        {url: null},
        {url: ""}
    ]
})
```

Or use the provided script:
```bash
python3 delete_test_jobs.py  # Already handles test jobs
```

---

## 📊 What Gets Stored

### ✅ Jobs That Are Stored

- Real Upwork jobs with complete data (title + URL)
- Jobs from Vollna that pass validation
- Normalized field structure for consistent frontend display

### ❌ Jobs That Are Skipped

- Test webhook events (`event == "webhook.test"`)
- Jobs with "test" in title
- Jobs missing `title` or `url`
- Invalid payloads (not dictionaries)

---

## 🔍 Monitoring

### Check Render Logs

Look for these log messages:

**✅ Good Signs**:
```
🔹 Webhook hit! /webhook/vollna
✅ Bearer token authentication successful
✅ Inserted job X: [Real Upwork Job Title]... (URL: https://www.upwork.com/jobs/~...)
```

**⚠️ Warning Signs**:
```
Skipping test webhook payload (event: webhook.test)
Skipping test job: Test Job from Vollna
Skipping incomplete job payload (missing title or URL)
```

**❌ Error Signs**:
```
Authentication failed - no valid Bearer token
Error processing Vollna webhook: ...
```

---

## 🧪 Testing

### Test with Real Payload

```bash
python3 test_bearer_token.py
```

**Expected**: Test job is inserted (for testing purposes), but real Vollna test events will be filtered.

### Verify Filtering

Send a test webhook event:
```bash
curl -X POST https://upwork-xxsc.onrender.com/webhook/vollna \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"event": "webhook.test"}'
```

**Expected**: Job is skipped, not stored.

---

## ✅ Status

- ✅ Test data filtering implemented
- ✅ Field normalization implemented
- ✅ Enhanced logging added
- ✅ Incomplete job validation added
- ✅ Database cleanup script available

---

## 📝 Next Steps

1. **Deploy Changes**: Push to GitHub (Render will auto-deploy)
2. **Monitor Logs**: Watch Render logs for filtered jobs
3. **Verify Real Jobs**: Check that real Upwork jobs are being stored
4. **Clean Database**: Remove any existing incomplete jobs

---

## 🔄 Backward Compatibility

- ✅ Original payload preserved in `raw` field
- ✅ Standard fields always present (even if empty)
- ✅ Multiple field name variations supported
- ✅ Existing jobs in database unaffected

