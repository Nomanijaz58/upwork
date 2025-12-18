# Swagger UI Testing Guide - /jobs/search Endpoint

## 🎯 Updated Response Format

The `/jobs/search` endpoint now returns:

```json
{
  "latest_jobs": [...],           // All latest jobs from source
  "latest_jobs_count": 5,          // Total count of latest jobs
  "filtered_jobs": [...],          // Jobs matching filters
  "filtered_jobs_count": 2,        // Total count of filtered jobs
  "applied_filters": {...}         // Filters that were applied
}
```

## 📋 Testing in Swagger UI

### Step 1: Open Swagger UI
https://upwork-xxsc.onrender.com/docs

### Step 2: Find POST /jobs/search
- Scroll to "jobs" section
- Find `POST /jobs/search`
- Click "Try it out"

### Step 3: Test Without Filters

**Request Body**:
```json
{
  "source": "vollna",
  "limit": 10,
  "skip": 0
}
```

**Expected Response**:
- `latest_jobs`: Array with all jobs from vollna
- `filtered_jobs`: Same as latest_jobs (no filters = all jobs)
- `latest_jobs_count` >= 0
- `filtered_jobs_count` >= 0

### Step 4: Test With Budget Filter

**Request Body**:
```json
{
  "source": "vollna",
  "min_budget": 30.0,
  "limit": 10
}
```

**Expected Response**:
- `latest_jobs`: All jobs from vollna
- `filtered_jobs`: Only jobs with budget >= 30
- `filtered_jobs_count` <= `latest_jobs_count`

### Step 5: Test With Skills Filter

**Request Body**:
```json
{
  "source": "vollna",
  "skills": ["Python", "FastAPI"],
  "limit": 10
}
```

**Expected Response**:
- `latest_jobs`: All jobs from vollna
- `filtered_jobs`: Only jobs with Python or FastAPI skills
- `filtered_jobs_count` <= `latest_jobs_count`

### Step 6: Test With Multiple Filters

**Request Body**:
```json
{
  "source": "vollna",
  "min_budget": 50.0,
  "max_proposals": 10,
  "skills": ["Python"],
  "keywords": ["backend"],
  "limit": 10
}
```

**Expected Response**:
- `latest_jobs`: All jobs from vollna
- `filtered_jobs`: Jobs matching ALL criteria
- `applied_filters`: Shows all filters applied

## ✅ Verification Checklist

- [ ] `latest_jobs` array is not empty (if jobs exist)
- [ ] `filtered_jobs` array shows filtered results
- [ ] `latest_jobs_count` matches number of items in `latest_jobs`
- [ ] `filtered_jobs_count` matches number of items in `filtered_jobs`
- [ ] `filtered_jobs_count` <= `latest_jobs_count`
- [ ] `applied_filters` shows correct filter criteria
- [ ] Jobs are sorted by newest first

## 🚨 Common Issues

### Empty Arrays
- **If both are empty**: No jobs from vollna yet - test webhook first
- **If latest_jobs has items but filtered_jobs is empty**: Filters are too strict

### Count Mismatch
- **If counts don't match array lengths**: This is a bug - report it
- **If filtered_count > latest_count**: This shouldn't happen - report it

