# Vollna Filter Sync Guide

## 🔍 Problem

You've configured filters in Vollna (keywords: python, english language, fastapis, flask; hourly rate max 50; etc.), but the backend has its own separate filter system that is **NOT automatically synced** with Vollna.

**Current Situation:**
- ✅ Vollna filters jobs BEFORE sending them (only matching jobs are sent)
- ❌ Backend ALSO applies its own filters AFTER ingestion
- ❌ If backend filters don't match Vollna filters, jobs might fail backend filtering

## 🎯 Solution

I've created a **filter sync endpoint** that allows you to sync your Vollna filter configuration to the backend.

## 📋 How to Sync Vollna Filters

### Step 1: Get Your Vollna Filter Configuration

From your Vollna dashboard, extract your filter settings:

**Keywords:**
- `python`
- `english language`
- `fastapis`
- `flask`

**Search Locations:**
- ✅ Search in title
- ✅ Search in description
- ✅ Search in skills

**Match Mode:**
- "any" (job matches if it has ANY keyword)

**Budget:**
- Hourly rate max: `50`

**Other filters:**
- Client details, geo filters, etc.

### Step 2: Sync to Backend

Use the new sync endpoint to import your Vollna filters:

```bash
curl -X POST https://upwork-xxsc.onrender.com/vollna/sync/filters \
  -H "X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": {
      "terms": ["python", "english language", "fastapis", "flask"],
      "match_mode": "any",
      "search_in": ["title", "description", "skills"]
    },
    "budget": {
      "hourly_rate_max": 50.0
    },
    "geo": {
      "excluded_countries": []
    }
  }'
```

**Expected Response:**
```json
{
  "synced": true,
  "keywords_synced": 4,
  "settings_synced": true,
  "geo_synced": true,
  "errors": []
}
```

### Step 3: Verify Sync Status

Check what filters are currently configured in the backend:

```bash
curl -X GET https://upwork-xxsc.onrender.com/vollna/sync/filters/status \
  -H "X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394"
```

**Expected Response:**
```json
{
  "keywords": {
    "terms": ["python", "english language", "fastapis", "flask"],
    "count": 4
  },
  "keyword_settings": {
    "match_mode": "any",
    "match_locations": ["title", "description", "skills"]
  },
  "geo": {
    "excluded_countries": []
  }
}
```

## 🔧 API Endpoints

### POST `/vollna/sync/filters`

Syncs Vollna filter configuration to backend.

**Request Body:**
```json
{
  "keywords": {
    "terms": ["python", "fastapi", "flask"],
    "match_mode": "any",  // "any" or "all"
    "search_in": ["title", "description", "skills"]
  },
  "geo": {
    "excluded_countries": ["Country1", "Country2"],
    "preferred_countries": ["United States"]
  }
}
```

**Response:**
```json
{
  "synced": true,
  "keywords_synced": 3,
  "settings_synced": true,
  "geo_synced": true,
  "errors": []
}
```

### GET `/vollna/sync/filters/status`

Get current backend filter configuration.

**Response:**
```json
{
  "keywords": {
    "terms": ["python", "fastapi"],
    "count": 2
  },
  "keyword_settings": {
    "match_mode": "any",
    "match_locations": ["title", "description", "skills"]
  },
  "geo": {
    "excluded_countries": []
  }
}
```

## 📝 Manual Configuration (Alternative)

If you prefer to configure filters manually via the backend API:

### 1. Set Keyword Settings

```bash
curl -X PUT https://upwork-xxsc.onrender.com/config/keywords/settings \
  -H "Content-Type: application/json" \
  -d '{
    "match_mode": "any",
    "match_locations": ["title", "description", "skills"],
    "metadata": {}
  }'
```

### 2. Add Keywords

```bash
# Add "python"
curl -X POST https://upwork-xxsc.onrender.com/config/keywords \
  -H "Content-Type: application/json" \
  -d '{
    "term": "python",
    "enabled": true,
    "metadata": {}
  }'

# Add "fastapi"
curl -X POST https://upwork-xxsc.onrender.com/config/keywords \
  -H "Content-Type: application/json" \
  -d '{
    "term": "fastapi",
    "enabled": true,
    "metadata": {}
  }'

# Add "flask"
curl -X POST https://upwork-xxsc.onrender.com/config/keywords \
  -H "Content-Type: application/json" \
  -d '{
    "term": "flask",
    "enabled": true,
    "metadata": {}
  }'

# Add "english language"
curl -X POST https://upwork-xxsc.onrender.com/config/keywords \
  -H "Content-Type: application/json" \
  -d '{
    "term": "english language",
    "enabled": true,
    "metadata": {}
  }'
```

### 3. Configure Geo Filters (if needed)

```bash
curl -X PUT https://upwork-xxsc.onrender.com/config/geo \
  -H "Content-Type: application/json" \
  -d '{
    "excluded_countries": [],
    "metadata": {}
  }'
```

## ✅ After Syncing

Once filters are synced:

1. **Jobs from Vollna** will be filtered by backend using the same criteria
2. **Jobs that pass filters** will appear in `jobs_filtered` collection
3. **Jobs that fail filters** will only be in `jobs_raw` collection
4. **Search endpoint** will respect these filters

## 🧪 Testing

### Test 1: Sync Filters
```bash
curl -X POST https://upwork-xxsc.onrender.com/vollna/sync/filters \
  -H "X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": {
      "terms": ["python", "fastapi"],
      "match_mode": "any",
      "search_in": ["title", "description", "skills"]
    }
  }'
```

### Test 2: Check Status
```bash
curl -X GET https://upwork-xxsc.onrender.com/vollna/sync/filters/status \
  -H "X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394"
```

### Test 3: Create Test Job
```bash
curl -X POST https://upwork-xxsc.onrender.com/vollna/jobs \
  -H "Authorization: Bearer 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394" \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [
      {
        "title": "Python Developer Needed",
        "description": "Looking for experienced Python developer with FastAPI",
        "url": "https://www.upwork.com/jobs/~test123",
        "budget": 45.0,
        "proposals": 5,
        "skills": ["Python", "FastAPI"],
        "postedOn": "2025-12-19T03:00:00Z"
      }
    ]
  }'
```

**Expected**: `inserted_filtered: 1` (job should pass filters now)

## 🔄 Auto-Sync (Future Enhancement)

For automatic syncing, you could:
1. Create an n8n workflow that periodically syncs Vollna filters
2. Add a webhook in Vollna that triggers sync when filters change
3. Use the sync endpoint in your n8n workflow after receiving jobs

## 📊 Understanding the Flow

**Before Sync:**
```
Vollna (filters) → Jobs → Backend (no filters) → All jobs stored
```

**After Sync:**
```
Vollna (filters) → Jobs → Backend (matching filters) → Only matching jobs in jobs_filtered
```

## 🎯 Quick Start

1. **Extract your Vollna filter config** from the dashboard
2. **Run the sync endpoint** with your filter settings
3. **Verify sync status** to confirm filters are applied
4. **Test with a job** to ensure it passes filters

Your backend filters will now match your Vollna filters! 🎉

