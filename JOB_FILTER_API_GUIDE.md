# Job Filter API Guide

## ✅ New Endpoint Created

A single API endpoint that accepts filter parameters and returns filtered jobs from Vollna.

## 📋 Endpoint Details

### `POST /jobs/filter`

**Description**: Apply filters to jobs from Vollna and return matching jobs.

**Request Body**:
```json
{
  "platform": "upwork",
  "budget_min": 50.0,
  "budget_max": 100.0,
  "budget_type": "hourly",
  "keywords": ["Python", "FastAPI"],
  "exclude_keywords": ["scraping"],
  "proposals_min": 0,
  "proposals_max": 10,
  "client_rating_min": 4.0,
  "client_verified_payment": true,
  "client_verified_phone": false,
  "excluded_countries": ["India", "Pakistan"],
  "include_invite_sent": false,
  "required_skills": ["Python", "MongoDB"],
  "posted_after": "2025-12-01T00:00:00Z",
  "posted_before": "2025-12-20T00:00:00Z"
}
```

**Response**:
```json
{
  "count": 15,
  "jobs": [
    {
      "_id": "...",
      "title": "Python Developer",
      "url": "https://www.upwork.com/jobs/~xxx",
      "budget": 75.0,
      "client_name": "Tech Corp",
      "description": "...",
      "skills": ["Python", "FastAPI"],
      "proposals": 5,
      "source": "vollna",
      "created_at": "...",
      "received_at": "..."
    }
  ],
  "filters_applied": {
    "budget_min": 50.0,
    "budget_max": 100.0,
    "keywords": ["Python", "FastAPI"]
  }
}
```

## 🎯 How It Works

1. **Frontend applies filters** (from Job Filters page)
2. **Calls `POST /jobs/filter`** with filter parameters
3. **Backend queries `vollna_jobs` collection** with MongoDB filters
4. **Returns filtered jobs** sorted by most recent first
5. **Frontend displays** filtered jobs on dashboard

## 📊 Filter Parameters

### Platform
- `platform`: "upwork", "freelancer", etc.

### Budget
- `budget_min`: Minimum budget (number)
- `budget_max`: Maximum budget (number)
- `budget_type`: "hourly", "fixed", or "all"

### Keywords
- `keywords`: Array of keywords to search in title/description
- `exclude_keywords`: Array of keywords to exclude

### Proposals
- `proposals_min`: Minimum number of proposals
- `proposals_max`: Maximum number of proposals

### Client
- `client_rating_min`: Minimum client rating (0-5)
- `client_verified_payment`: true/false
- `client_verified_phone`: true/false

### Geographic
- `excluded_countries`: Array of country names to exclude

### Skills
- `required_skills`: Array of required skills

### Date
- `posted_after`: ISO datetime string
- `posted_before`: ISO datetime string

### Invite
- `include_invite_sent`: true/false (if false, excludes jobs with invite_sent=true)

## 🧪 Example Usage

### Example 1: Basic Budget Filter
```bash
curl -X POST https://upwork-xxsc.onrender.com/jobs/filter \
  -H "Content-Type: application/json" \
  -d '{
    "budget_min": 50.0,
    "budget_max": 100.0
  }'
```

### Example 2: Keywords + Proposals
```bash
curl -X POST https://upwork-xxsc.onrender.com/jobs/filter \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["Python", "FastAPI"],
    "proposals_max": 5
  }'
```

### Example 3: Full Filter Set
```bash
curl -X POST https://upwork-xxsc.onrender.com/jobs/filter \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "upwork",
    "budget_min": 50.0,
    "budget_max": 150.0,
    "keywords": ["Python", "Backend"],
    "exclude_keywords": ["scraping", "automation"],
    "proposals_min": 0,
    "proposals_max": 10,
    "client_rating_min": 4.0,
    "client_verified_payment": true,
    "excluded_countries": ["India"],
    "include_invite_sent": false,
    "required_skills": ["Python", "MongoDB"]
  }'
```

## 🔍 Preview Endpoint

### `GET /jobs/filter/preview`

Get statistics and available filter options.

**Response**:
```json
{
  "total_jobs": 150,
  "available_platforms": ["upwork"],
  "available_skills": ["Python", "FastAPI", "MongoDB", ...],
  "budget_range": {
    "min_budget": 20.0,
    "max_budget": 200.0,
    "avg_budget": 75.5
  },
  "sample_jobs": 10
}
```

## 🔄 Frontend Integration

### When User Applies Filters:

```javascript
// Frontend code (example)
const applyFilters = async (filters) => {
  const response = await fetch('https://upwork-xxsc.onrender.com/jobs/filter', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(filters)
  });
  
  const data = await response.json();
  
  // Update dashboard with filtered jobs
  setJobs(data.jobs);
  setJobCount(data.count);
};
```

## 📝 Important Notes

1. **All filters are optional** - Send only the filters you want to apply
2. **Jobs come from `vollna_jobs` collection** - All jobs received via webhook
3. **Results are sorted** by most recent first (created_at, received_at)
4. **Limit is 1000 jobs** by default (can be adjusted with `limit` query param)
5. **No webhook triggering** - This endpoint only filters existing jobs, it doesn't trigger Vollna to send new jobs

## 🚀 Next Steps

1. **Update frontend** to call `/jobs/filter` when filters are applied
2. **Test with sample filters** to verify results
3. **Deploy to Render** (code is ready, just push)

---

**The filter API is ready!** It filters jobs from Vollna based on your criteria. 🎉

