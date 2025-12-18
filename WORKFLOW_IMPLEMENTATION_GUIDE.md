# Complete Workflow Implementation Guide

## 🎯 Overview

This guide documents the complete implementation of the Upwork job automation workflow using Vollna webhooks, FastAPI backend, and frontend chatbot integration.

## 📋 Workflow Steps

```
1️⃣ Vollna → POST /webhook/vollna → Store in MongoDB (raw + filtered)
2️⃣ Frontend polls GET /jobs/latest every 10-15 seconds
3️⃣ User applies filters → POST /jobs/search → Returns matching jobs
4️⃣ Frontend calls POST /jobs/recommend → AI suggests best jobs
5️⃣ Frontend displays jobs in styled UI (job cards, budget, skills, Upwork link)
```

---

## 🔌 Backend Endpoints

### 1. POST `/webhook/vollna`

**Purpose**: Receive jobs from Vollna webhook, store in MongoDB, deduplicate by job URL.

**Request Headers**:
```
Authorization: Bearer <N8N_SHARED_SECRET>
Content-Type: application/json
```

**Request Body** (Vollna format):
```json
{
  "jobs": [
    {
      "title": "Python Developer Needed",
      "description": "Looking for experienced Python developer...",
      "url": "https://www.upwork.com/jobs/~abc123",
      "budget": 50.0,
      "proposals": 5,
      "skills": ["Python", "FastAPI", "MongoDB"],
      "postedOn": "2025-12-19T10:00:00Z"
    }
  ]
}
```

**Response**:
```json
{
  "received": 1,
  "inserted_raw": 1,
  "inserted_filtered": 1,
  "deduped": 0
}
```

**Features**:
- ✅ Automatic normalization of Vollna payload formats
- ✅ Field validation (title, description, url required)
- ✅ URL deduplication (prevents duplicate jobs)
- ✅ Stores in both `jobs_raw` and `jobs_filtered` collections
- ✅ Updates feed status tracking

**Alternative Endpoint**: `POST /vollna/jobs` (same functionality)

---

### 2. GET `/jobs/latest`

**Purpose**: Return latest jobs sorted by posted date, limit 50. Designed for frontend polling.

**Query Parameters**:
- `source` (optional): Filter by source (e.g., `vollna`, `best_match`)
- `limit` (optional, default: 50): Maximum number of jobs to return (1-200)

**Example Request**:
```
GET /jobs/latest?source=vollna&limit=50
```

**Response**:
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "title": "Python Developer Needed",
    "description": "Looking for experienced Python developer...",
    "url": "https://www.upwork.com/jobs/~abc123",
    "source": "vollna",
    "region": "United States",
    "posted_at": "2025-12-19T10:00:00Z",
    "skills": ["Python", "FastAPI", "MongoDB"],
    "budget": 50.0,
    "proposals": 5,
    "client": {
      "payment_verified": true,
      "rating": 4.8
    },
    "created_at": "2025-12-19T10:05:00Z",
    "updated_at": "2025-12-19T10:05:00Z"
  }
]
```

**Features**:
- ✅ Sorted by `posted_at` DESC (newest first)
- ✅ Returns from `jobs_raw` collection (all jobs)
- ✅ Optimized for polling (fast queries with indexes)
- ✅ Default limit: 50 jobs

**Frontend Usage**:
```javascript
// Poll every 10-15 seconds
setInterval(async () => {
  const response = await fetch('/jobs/latest?source=vollna&limit=50');
  const jobs = await response.json();
  updateJobList(jobs);
}, 10000); // 10 seconds
```

---

### 3. POST `/jobs/search`

**Purpose**: Accept filters and return matching jobs. Called dynamically when user applies filters.

**Request Body**:
```json
{
  "budget_min": 100,
  "budget_max": 1000,
  "skills": ["Python", "FastAPI"],
  "proposals_max": 5,
  "source": "vollna",
  "keywords": ["backend", "API"],
  "skip": 0,
  "limit": 50
}
```

**Response**:
```json
{
  "latest_jobs": [
    {
      "id": "...",
      "title": "Python Developer",
      "budget": 150.0,
      "proposals": 3,
      "skills": ["Python", "FastAPI"],
      ...
    }
  ],
  "latest_jobs_count": 25,
  "filtered_jobs": [
    {
      "id": "...",
      "title": "Python Developer",
      "budget": 150.0,
      "proposals": 3,
      "skills": ["Python", "FastAPI"],
      ...
    }
  ],
  "filtered_jobs_count": 10,
  "applied_filters": {
    "source": "vollna",
    "budget": {"$gte": 100, "$lte": 1000},
    "proposals": {"$lte": 5},
    "skills": {"$in": ["Python", "FastAPI"]}
  }
}
```

**Filter Parameters**:
- `budget_min` (optional): Minimum budget in USD
- `budget_max` (optional): Maximum budget in USD
- `skills` (optional, array): Job must have at least one of these skills
- `proposals_max` (optional): Maximum number of proposals
- `keywords` (optional, array): Search in title/description
- `source` (optional): Filter by source
- `skip` (optional, default: 0): Pagination offset
- `limit` (optional, default: 50): Maximum results (1-200)

**Features**:
- ✅ Returns both `latest_jobs` (all jobs) and `filtered_jobs` (matching filters)
- ✅ Supports multiple filter combinations
- ✅ Sorted by newest first
- ✅ Efficient MongoDB queries with indexes

**Frontend Usage**:
```javascript
// When user applies filters
async function searchJobs(filters) {
  const response = await fetch('/jobs/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      budget_min: filters.minBudget,
      budget_max: filters.maxBudget,
      skills: filters.skills,
      proposals_max: filters.maxProposals,
      source: 'vollna',
      limit: 50
    })
  });
  const result = await response.json();
  displayJobs(result.filtered_jobs);
}
```

---

### 4. POST `/jobs/recommend`

**Purpose**: Accept filtered jobs and return AI-suggested best jobs to apply for.

**Request Body**:
```json
{
  "budget_min": 100,
  "budget_max": 1000,
  "skills": ["Python", "FastAPI"],
  "proposals_max": 5,
  "source": "vollna",
  "limit": 20
}
```

**Query Parameters** (optional):
- `user_skills`: Comma-separated user skills (e.g., `Python,FastAPI,MongoDB`)
- `prioritize_budget`: `true` to prioritize higher budget jobs
- `prioritize_low_competition`: `true` to prioritize jobs with fewer proposals

**Response**:
```json
{
  "ranked_jobs": [
    {
      "job": {
        "id": "...",
        "title": "Python Developer",
        "budget": 150.0,
        "proposals": 3,
        "skills": ["Python", "FastAPI"],
        ...
      },
      "score": 8.5,
      "reasons": [
        "High budget ($150/hr)",
        "Low competition (3 proposals)",
        "Skills match: Python, FastAPI"
      ]
    }
  ],
  "scoring_breakdown": {
    "total_jobs_ranked": 10,
    "average_score": 7.2
  }
}
```

**Features**:
- ✅ AI-powered scoring based on budget, proposals, skills, description quality
- ✅ Returns top recommended jobs with scores
- ✅ Explains why each job was recommended
- ✅ Can prioritize budget or low competition

**Frontend Usage**:
```javascript
// After filtering, get recommendations
async function getRecommendations(searchFilters) {
  const response = await fetch(
    `/jobs/recommend?user_skills=Python,FastAPI&prioritize_budget=true&prioritize_low_competition=true`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...searchFilters,
        limit: 20
      })
    }
  );
  const result = await response.json();
  displayRecommendedJobs(result.ranked_jobs);
}
```

---

## 🎨 Frontend Implementation

### Frontend Requirements

**Framework**: Vanilla JS / React / Vue

**Features**:
1. **Filter Form**: Input fields for budget, skills, proposals_max
2. **Job Cards**: Display title, budget, skills, description, Upwork link
3. **Auto-refresh**: Poll `/jobs/latest` every 10-15 seconds
4. **Dynamic Search**: Call `/jobs/search` when filters change
5. **AI Recommendations**: Call `/jobs/recommend` after filtering

### Example Frontend Code (Vanilla JS)

```html
<!DOCTYPE html>
<html>
<head>
  <title>Upwork Job Assistant</title>
  <style>
    .job-card {
      border: 1px solid #ddd;
      padding: 15px;
      margin: 10px 0;
      border-radius: 8px;
    }
    .job-title {
      font-size: 18px;
      font-weight: bold;
      color: #333;
    }
    .job-budget {
      color: #28a745;
      font-weight: bold;
    }
    .job-skills {
      display: flex;
      gap: 5px;
      flex-wrap: wrap;
    }
    .skill-tag {
      background: #007bff;
      color: white;
      padding: 3px 8px;
      border-radius: 3px;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <h1>Upwork Job Assistant</h1>
  
  <!-- Filter Form -->
  <div id="filters">
    <input type="number" id="budget_min" placeholder="Min Budget ($)">
    <input type="number" id="budget_max" placeholder="Max Budget ($)">
    <input type="number" id="proposals_max" placeholder="Max Proposals">
    <input type="text" id="skills" placeholder="Skills (comma-separated)">
    <button onclick="applyFilters()">Apply Filters</button>
    <button onclick="getRecommendations()">Get Recommendations</button>
  </div>
  
  <!-- Job List -->
  <div id="job-list"></div>
  
  <script>
    const API_URL = 'https://upwork-xxsc.onrender.com';
    
    // Poll latest jobs every 10 seconds
    setInterval(async () => {
      await loadLatestJobs();
    }, 10000);
    
    // Load latest jobs
    async function loadLatestJobs() {
      try {
        const response = await fetch(`${API_URL}/jobs/latest?source=vollna&limit=50`);
        const jobs = await response.json();
        displayJobs(jobs);
      } catch (error) {
        console.error('Error loading jobs:', error);
      }
    }
    
    // Apply filters and search
    async function applyFilters() {
      const filters = {
        budget_min: parseFloat(document.getElementById('budget_min').value) || undefined,
        budget_max: parseFloat(document.getElementById('budget_max').value) || undefined,
        proposals_max: parseInt(document.getElementById('proposals_max').value) || undefined,
        skills: document.getElementById('skills').value
          .split(',')
          .map(s => s.trim())
          .filter(s => s),
        source: 'vollna',
        limit: 50
      };
      
      try {
        const response = await fetch(`${API_URL}/jobs/search`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(filters)
        });
        const result = await response.json();
        displayJobs(result.filtered_jobs);
      } catch (error) {
        console.error('Error searching jobs:', error);
      }
    }
    
    // Get AI recommendations
    async function getRecommendations() {
      const filters = {
        budget_min: parseFloat(document.getElementById('budget_min').value) || undefined,
        budget_max: parseFloat(document.getElementById('budget_max').value) || undefined,
        proposals_max: parseInt(document.getElementById('proposals_max').value) || undefined,
        skills: document.getElementById('skills').value
          .split(',')
          .map(s => s.trim())
          .filter(s => s),
        source: 'vollna',
        limit: 20
      };
      
      try {
        const response = await fetch(
          `${API_URL}/jobs/recommend?user_skills=Python,FastAPI&prioritize_budget=true&prioritize_low_competition=true`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(filters)
          }
        );
        const result = await response.json();
        displayRecommendedJobs(result.ranked_jobs);
      } catch (error) {
        console.error('Error getting recommendations:', error);
      }
    }
    
    // Display jobs
    function displayJobs(jobs) {
      const container = document.getElementById('job-list');
      container.innerHTML = jobs.map(job => `
        <div class="job-card">
          <div class="job-title">${job.title}</div>
          <div class="job-budget">$${job.budget || 'Not specified'}/hr</div>
          <div class="job-skills">
            ${job.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
          </div>
          <p>${job.description.substring(0, 200)}...</p>
          <div>Proposals: ${job.proposals || 'N/A'}</div>
          <a href="${job.url}" target="_blank">View on Upwork</a>
        </div>
      `).join('');
    }
    
    // Display recommended jobs
    function displayRecommendedJobs(rankedJobs) {
      const container = document.getElementById('job-list');
      container.innerHTML = rankedJobs.map(item => {
        const job = item.job;
        return `
          <div class="job-card" style="border-left: 4px solid #28a745;">
            <div style="display: flex; justify-content: space-between;">
              <div class="job-title">${job.title}</div>
              <div style="background: #28a745; color: white; padding: 5px 10px; border-radius: 5px;">
                Score: ${item.score.toFixed(1)}
              </div>
            </div>
            <div class="job-budget">$${job.budget || 'Not specified'}/hr</div>
            <div class="job-skills">
              ${job.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
            </div>
            <p>${job.description.substring(0, 200)}...</p>
            <div>Proposals: ${job.proposals || 'N/A'}</div>
            <div style="margin-top: 10px;">
              <strong>Why recommended:</strong>
              <ul>
                ${item.reasons.map(r => `<li>${r}</li>`).join('')}
              </ul>
            </div>
            <a href="${job.url}" target="_blank">View on Upwork</a>
          </div>
        `;
      }).join('');
    }
    
    // Load initial jobs
    loadLatestJobs();
  </script>
</body>
</html>
```

---

## 🗄️ Database Schema

### Collections

**`jobs_raw`**: All ingested jobs (regardless of filter status)
- Indexed on: `url` (unique), `posted_at`, `source`, `budget`, `proposals`

**`jobs_filtered`**: Jobs that passed keyword/geo filters
- Indexed on: `url` (unique), `posted_at`, `source`, `budget`, `proposals`, `skills`

### Job Document Structure

```json
{
  "_id": ObjectId("..."),
  "title": "Python Developer Needed",
  "description": "Looking for experienced Python developer...",
  "url": "https://www.upwork.com/jobs/~abc123",
  "source": "vollna",
  "region": "United States",
  "posted_at": ISODate("2025-12-19T10:00:00Z"),
  "skills": ["Python", "FastAPI", "MongoDB"],
  "budget": 50.0,
  "proposals": 5,
  "client": {
    "payment_verified": true,
    "rating": 4.8
  },
  "created_at": ISODate("2025-12-19T10:05:00Z"),
  "updated_at": ISODate("2025-12-19T10:05:00Z")
}
```

---

## 🔐 Authentication

**Webhook Endpoint** (`/webhook/vollna`):
- Requires `Authorization: Bearer <N8N_SHARED_SECRET>` header
- Or `X-N8N-Secret: <N8N_SHARED_SECRET>` header

**Other Endpoints**:
- Currently no authentication required (can add JWT/Session auth later)
- For production, consider adding authentication

---

## 📊 API Endpoints Summary

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/webhook/vollna` | POST | Receive Vollna jobs | Bearer Token |
| `/jobs/latest` | GET | Get latest jobs (polling) | None |
| `/jobs/search` | POST | Filter jobs dynamically | None |
| `/jobs/recommend` | POST | AI job recommendations | None |
| `/vollna/jobs` | POST | Alternative webhook endpoint | Bearer Token |
| `/jobs` | GET | Get jobs (with filters) | None |

---

## ✅ Implementation Checklist

- [x] **Webhook Endpoint**: `POST /webhook/vollna` receives Vollna jobs
- [x] **Latest Jobs**: `GET /jobs/latest` returns latest jobs sorted by date
- [x] **Search Jobs**: `POST /jobs/search` accepts filters and returns matching jobs
- [x] **Recommendations**: `POST /jobs/recommend` returns AI-suggested jobs
- [x] **MongoDB Storage**: Jobs stored in `jobs_raw` and `jobs_filtered` collections
- [x] **Deduplication**: Jobs deduplicated by URL
- [x] **Indexes**: MongoDB indexes on `url`, `posted_at`, `source`, `budget`, `proposals`, `skills`
- [x] **Feed Status**: Tracks feed health and last fetch time

---

## 🧪 Testing

### Test Webhook
```bash
curl -X POST https://upwork-xxsc.onrender.com/webhook/vollna \
  -H "Authorization: Bearer 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394" \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [{
      "title": "Python Developer",
      "description": "Test job",
      "url": "https://www.upwork.com/jobs/~test123",
      "budget": 50.0,
      "proposals": 5,
      "skills": ["Python", "FastAPI"],
      "postedOn": "2025-12-19T10:00:00Z"
    }]
  }'
```

### Test Latest Jobs
```bash
curl "https://upwork-xxsc.onrender.com/jobs/latest?source=vollna&limit=10"
```

### Test Search
```bash
curl -X POST https://upwork-xxsc.onrender.com/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "budget_min": 100,
    "budget_max": 1000,
    "skills": ["Python", "FastAPI"],
    "proposals_max": 5,
    "source": "vollna",
    "limit": 50
  }'
```

### Test Recommendations
```bash
curl -X POST "https://upwork-xxsc.onrender.com/jobs/recommend?user_skills=Python,FastAPI&prioritize_budget=true" \
  -H "Content-Type: application/json" \
  -d '{
    "budget_min": 100,
    "budget_max": 1000,
    "skills": ["Python"],
    "proposals_max": 5,
    "source": "vollna",
    "limit": 20
  }'
```

---

## 🚀 Deployment

**Backend**: Deployed on Render at `https://upwork-xxsc.onrender.com`

**Frontend**: Can be deployed on:
- Render (static site)
- Vercel
- Netlify
- GitHub Pages

**Environment Variables**:
- `MONGODB_URI`: MongoDB connection string
- `N8N_SHARED_SECRET`: Secret for webhook authentication
- `OPENAI_API_KEY`: For AI recommendations (optional)

---

## 📝 Notes

1. **Vollna Webhook**: Ensure Vollna is configured to send jobs to `/webhook/vollna`
2. **MongoDB Indexes**: Indexes are automatically created on startup
3. **Polling Interval**: Frontend should poll `/jobs/latest` every 10-15 seconds
4. **AI Recommendations**: Uses OpenAI API for job scoring (optional, can use custom algorithm)

---

## 🎯 Next Steps

1. ✅ Deploy backend (already done)
2. ⏳ Create frontend chatbot UI
3. ⏳ Connect Vollna webhook to `/webhook/vollna`
4. ⏳ Test end-to-end workflow
5. ⏳ Add authentication for production

---

## 📚 Additional Resources

- **Swagger UI**: https://upwork-xxsc.onrender.com/docs
- **Health Check**: https://upwork-xxsc.onrender.com/health
- **Vollna Integration Guide**: `VOLLNA_N8N_INTEGRATION.md`
- **Testing Guide**: `COMPLETE_TESTING_GUIDE.md`

