# What Makes a Job "Valid" for `jobs_raw`?

## ✅ Validation Requirements

A job is considered **"valid"** and stored in `jobs_raw` if it passes these checks:

### 1. Required Fields Validation

**Title** (Required):
- ✅ Must exist
- ✅ Must not be empty (after trimming whitespace)
- ❌ Rejected if: `title` is missing, `null`, empty string, or only whitespace

**Description** (Required):
- ✅ Must exist
- ✅ Must not be empty (after trimming whitespace)
- ❌ Rejected if: `description` is missing, `null`, empty string, or only whitespace

**URL** (Required):
- ✅ Must exist
- ✅ Must not be empty (after trimming whitespace)
- ✅ Must start with `http://` or `https://`
- ❌ Rejected if: `url` is missing, `null`, empty, or invalid format

### 2. URL Format Validation

**Valid URL Examples**:
- ✅ `https://www.upwork.com/jobs/~123`
- ✅ `http://www.upwork.com/jobs/~123`
- ✅ `https://upwork.com/jobs/~test123`

**Invalid URL Examples**:
- ❌ `www.upwork.com/jobs/~123` (missing protocol)
- ❌ `upwork.com/jobs/~123` (missing protocol)
- ❌ `/jobs/~123` (relative URL)
- ❌ Empty string or null

### 3. Optional Fields (Not Validated)

These fields are **optional** and don't affect validity:
- `source` - Defaults to provided value
- `region` - Can be `null`
- `posted_at` - Can be `null`
- `skills` - Can be empty array `[]`
- `budget` - Can be `null`
- `proposals` - Can be `null`
- `client` - Can be empty object `{}`
- `raw` - Can be empty object `{}`

## 🔍 Validation Code

Here's the exact validation logic from `backend/app/routers/ingest.py`:

```python
for idx, item in enumerate(payload.items):
    try:
        # ✅ VALIDATION 1: Title
        if not item.title or not item.title.strip():
            errors.append(f"Job {idx}: Missing or empty title")
            continue  # ❌ Skip this job
        
        # ✅ VALIDATION 2: Description
        if not item.description or not item.description.strip():
            errors.append(f"Job {idx}: Missing or empty description")
            continue  # ❌ Skip this job
        
        # ✅ VALIDATION 3: URL exists
        if not item.url or not item.url.strip():
            errors.append(f"Job {idx}: Missing or empty URL")
            continue  # ❌ Skip this job
        
        # ✅ VALIDATION 4: URL format
        if not item.url.startswith(("http://", "https://")):
            errors.append(f"Job {idx}: Invalid URL format: {item.url}")
            continue  # ❌ Skip this job
        
        # ✅ All validations passed - store in jobs_raw
        normalized_url = item.url.rstrip("/")
        raw_doc = {
            "title": item.title.strip(),
            "description": item.description.strip(),
            "url": normalized_url,
            # ... other fields
        }
        await raw_repo.insert_one(raw_doc)  # ✅ Stored!
        
    except Exception as e:
        errors.append(f"Job {idx}: Error processing job - {str(e)}")
        continue  # ❌ Skip this job
```

## 📊 Validation Flow

```
Job Received
    ↓
Check Title?
    ├─ ❌ Missing/Empty → Skip (add to errors)
    └─ ✅ Valid → Continue
        ↓
Check Description?
    ├─ ❌ Missing/Empty → Skip (add to errors)
    └─ ✅ Valid → Continue
        ↓
Check URL?
    ├─ ❌ Missing/Empty → Skip (add to errors)
    └─ ✅ Exists → Continue
        ↓
Check URL Format?
    ├─ ❌ Invalid (no http/https) → Skip (add to errors)
    └─ ✅ Valid → Continue
        ↓
✅ ALL VALIDATIONS PASSED
    ↓
Store in jobs_raw ✅
```

## 🎯 What Happens to Invalid Jobs?

**Invalid jobs are:**
- ❌ **NOT stored** in `jobs_raw`
- ❌ **NOT stored** in `jobs_filtered`
- ✅ **Logged** in the `errors` array
- ✅ **Returned** in the API response under `errors` field

**Example Response**:
```json
{
  "received": 5,
  "inserted_raw": 3,
  "inserted_filtered": 2,
  "deduped": 0,
  "errors": [
    "Job 1: Missing or empty title",
    "Job 3: Invalid URL format: www.upwork.com/jobs/~123"
  ]
}
```

## 📋 Pydantic Schema Validation

Before the code validation, Pydantic also validates the request structure:

**Required by Schema** (`JobIngestItem`):
- ✅ `title: str` - Required string
- ✅ `description: str` - Required string
- ✅ `url: str` - Required string
- ✅ `source: str` - Required string

**Optional by Schema**:
- `region: Optional[str]` - Can be `None`
- `posted_at: Optional[datetime]` - Can be `None`
- `skills: list[str]` - Defaults to `[]`
- `budget: Optional[float]` - Can be `None`
- `proposals: Optional[int]` - Can be `None`
- `client: dict[str, Any]` - Defaults to `{}`
- `raw: dict[str, Any]` - Defaults to `{}`

## 🎯 Summary

**A job is "valid" if it has:**
1. ✅ **Title** (non-empty string)
2. ✅ **Description** (non-empty string)
3. ✅ **URL** (valid HTTP/HTTPS URL)

**That's it!** All other fields are optional.

**Invalid jobs are:**
- Skipped (not stored)
- Logged in errors
- Returned in API response

---

**Think of it like a bouncer at a club:**
- ✅ Has ID (title) → Check
- ✅ Has description → Check
- ✅ Has valid URL → Check
- ✅ All checks pass → Welcome to `jobs_raw`! 🎉

