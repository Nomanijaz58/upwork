# Vollna + n8n + Backend Integration Guide

Complete guide for integrating Vollna job alerts with n8n workflows and the backend API.

## 📋 Overview

**Workflow Flow:**
```
Vollna Extension → n8n Webhook → POST /vollna/jobs → Normalize → POST /ingest/upwork → MongoDB → Chatbot
```

## 🔧 1. Vollna Integration

### Vollna Extension Setup

1. **Install Vollna Extension** in your browser
2. **Configure Upwork Alerts**:
   - Set up saved searches in Upwork
   - Enable Vollna alerts for new jobs
   - Vollna will send job data to n8n webhook

### Vollna Payload Format

Vollna sends job data in various formats. The backend automatically normalizes:

**Format 1: Single Job**
```json
{
  "title": "Python Developer Needed",
  "description": "Looking for experienced Python developer...",
  "url": "https://www.upwork.com/jobs/~abc123",
  "budget": 50.0,
  "proposals": 5,
  "skills": ["Python", "FastAPI", "MongoDB"],
  "postedAt": "2025-01-15T10:00:00Z",
  "country": "United States"
}
```

**Format 2: Multiple Jobs**
```json
[
  {
    "title": "Job 1",
    "description": "...",
    "url": "...",
    "budget": 50,
    "proposals": 5,
    "skills": ["Python"],
    "postedOn": "2025-01-15T10:00:00Z"
  },
  {
    "title": "Job 2",
    "description": "...",
    "url": "...",
    "budget": 75,
    "proposals": 3,
    "skills": ["React"],
    "postedOn": "2025-01-15T11:00:00Z"
  }
]
```

**Format 3: Wrapped**
```json
{
  "jobs": [
    {"title": "...", "url": "...", ...}
  ]
}
```

## 🔗 2. n8n Workflow Setup

### Step 1: Create Webhook Trigger

1. **Create new n8n workflow**
2. **Add "Webhook" node**:
   - Method: `POST`
   - Path: `/vollna/jobs` (or your custom path)
   - Response Mode: `When Last Node Finishes`
   - Authentication: `None` (we'll use header secret)

### Step 2: Normalize Payload (Optional)

If Vollna sends data in a non-standard format, add a **"Code" node** to normalize:

```javascript
// Normalize Vollna payload
const payload = $input.item.json;

// Handle different formats
let jobs = [];
if (Array.isArray(payload)) {
  jobs = payload;
} else if (payload.jobs) {
  jobs = payload.jobs;
} else if (payload.data) {
  jobs = payload.data;
} else {
  jobs = [payload]; // Single job
}

// Ensure all jobs have required fields
const normalized = jobs.map(job => ({
  title: job.title || job.jobTitle || "",
  description: job.description || job.snippet || "",
  url: job.url || job.jobUrl || job.link || "",
  budget: job.budget || job.hourlyRate || job.fixedPrice || null,
  proposals: job.proposals || job.proposalCount || null,
  skills: job.skills || job.categories || [],
  postedOn: job.postedOn || job.posted_at || job.createdAt || null,
  source: "vollna"
}));

return normalized.map(job => ({ json: job }));
```

### Step 3: Forward to Backend

Add **"HTTP Request" node**:

- **Method**: `POST`
- **URL**: `http://localhost:8000/vollna/jobs` (or your backend URL)
- **Authentication**: `Generic Credential Type`
- **Header Name**: `X-N8N-Secret`
- **Header Value**: `{{ $env.N8N_SHARED_SECRET }}` (or your secret from `.env`)

**Request Body**:
```json
{{ $json }}
```

### Step 4: Error Handling

Add **"IF" node** to check response status:
- If status code = 200: Success
- Else: Log error and send notification

### Complete n8n Workflow

```
Webhook → Code (Normalize) → HTTP Request (Backend) → IF (Check Status) → Success/Error
```

## 🚀 3. Backend Endpoints

### POST `/vollna/jobs`

**Purpose**: Receive Vollna job payloads via n8n webhook

**Headers**:
```
X-N8N-Secret: <your-secret-from-env>
Content-Type: application/json
```

**Request Body** (any Vollna format):
```json
{
  "title": "Python Developer",
  "description": "...",
  "url": "https://www.upwork.com/jobs/~abc123",
  "budget": 50.0,
  "proposals": 5,
  "skills": ["Python", "FastAPI"],
  "postedOn": "2025-01-15T10:00:00Z"
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
- ✅ Automatic normalization of various Vollna formats
- ✅ Field validation (title, description, url required)
- ✅ URL deduplication
- ✅ Budget and proposals extraction
- ✅ Skills array normalization
- ✅ Feed status tracking

### POST `/ingest/upwork`

**Purpose**: Direct ingestion endpoint (used internally by `/vollna/jobs`)

**Request Body**:
```json
{
  "items": [
    {
      "title": "Python Developer",
      "description": "...",
      "url": "https://www.upwork.com/jobs/~abc123",
      "source": "vollna",
      "budget": 50.0,
      "proposals": 5,
      "skills": ["Python", "FastAPI"],
      "posted_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

### POST `/jobs/search`

**Purpose**: Search and filter jobs (used by chatbot)

**Request Body**:
```json
{
  "min_budget": 30.0,
  "max_budget": 100.0,
  "max_proposals": 10,
  "skills": ["Python", "FastAPI"],
  "keywords": ["backend", "API"],
  "source": "vollna",
  "skip": 0,
  "limit": 50
}
```

**Response**:
```json
{
  "total": 25,
  "jobs": [
    {
      "id": "...",
      "title": "...",
      "description": "...",
      "url": "...",
      "budget": 50.0,
      "proposals": 5,
      "skills": ["Python", "FastAPI"],
      "posted_at": "2025-01-15T10:00:00Z"
    }
  ],
  "applied_filters": {...}
}
```

### POST `/jobs/recommend`

**Purpose**: AI-powered job recommendations (used by chatbot)

**Request Body**:
```json
{
  "min_budget": 30.0,
  "max_proposals": 10,
  "skills": ["Python", "FastAPI"],
  "keywords": ["backend"],
  "source": "vollna",
  "limit": 20
}
```

**Query Parameters** (optional):
- `user_skills`: `["Python", "FastAPI", "MongoDB"]`
- `prioritize_budget`: `true`
- `prioritize_low_competition`: `true`

**Response**:
```json
{
  "ranked_jobs": [
    {
      "job_id": "...",
      "job_url": "...",
      "title": "...",
      "score": 85.5,
      "breakdown": {
        "budget_score": 25.0,
        "competition_score": 20.0,
        "skill_relevance_score": 25.0,
        "description_quality_score": 15.5
      },
      "budget": 50.0,
      "proposals": 5,
      "skills": ["Python", "FastAPI"]
    }
  ],
  "scoring_breakdown": {...}
}
```

### POST `/ai/generate-proposal`

**Purpose**: Generate AI proposal for a job (used by chatbot)

**Request Body**:
```json
{
  "job_id": "...",
  "portfolio_id": "...",
  "tone": "professional",
  "length": "medium",
  "custom_message": "I have 5+ years experience..."
}
```

## 🤖 4. Chatbot Integration

### Chatbot Workflow

1. **User sets filters** (budget, skills, keywords)
2. **Chatbot calls** `POST /jobs/search` with filters
3. **Chatbot displays** filtered jobs
4. **User selects job** → Chatbot calls `POST /jobs/recommend` for AI ranking
5. **User requests proposal** → Chatbot calls `POST /ai/generate-proposal`

### Example Chatbot Code (JavaScript)

```javascript
// Search jobs
async function searchJobs(filters) {
  const response = await fetch('http://localhost:8000/jobs/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userToken}` // JWT token
    },
    body: JSON.stringify({
      min_budget: filters.minBudget,
      max_proposals: filters.maxProposals,
      skills: filters.skills,
      keywords: filters.keywords,
      source: 'vollna',
      limit: 50
    })
  });
  return await response.json();
}

// Get AI recommendations
async function getRecommendations(searchFilters, userSkills) {
  const response = await fetch('http://localhost:8000/jobs/recommend', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userToken}`
    },
    body: JSON.stringify(searchFilters)
  });
  
  // Add user skills as query param
  const url = new URL(response.url);
  url.searchParams.set('user_skills', JSON.stringify(userSkills));
  
  return await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userToken}`
    },
    body: JSON.stringify(searchFilters)
  }).then(r => r.json());
}

// Generate proposal
async function generateProposal(jobId, portfolioId, tone = 'professional') {
  const response = await fetch('http://localhost:8000/ai/generate-proposal', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userToken}`
    },
    body: JSON.stringify({
      job_id: jobId,
      portfolio_id: portfolioId,
      tone: tone,
      length: 'medium'
    })
  });
  return await response.json();
}
```

## 🔒 5. Security

### n8n Secret

**Environment Variable** (`.env`):
```
N8N_SHARED_SECRET=9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394
```

**n8n Header**:
```
X-N8N-Secret: <value-from-env>
```

### Chatbot Authentication

**JWT Token** (recommended):
- Chatbot authenticates user
- Sends JWT token in `Authorization: Bearer <token>` header
- Backend validates token (implement JWT middleware)

**Session Token** (alternative):
- Use session-based authentication
- Store session in Redis/cookies

### No Scraping

✅ **No Upwork credentials in backend**
✅ **No scraping code**
✅ **No login automation**
✅ **All data comes from Vollna extension**

## 📊 6. MongoDB Schema

### Jobs Collection (`jobs_raw`, `jobs_filtered`)

```javascript
{
  "_id": ObjectId("..."),
  "title": "Python Developer",
  "description": "...",
  "url": "https://www.upwork.com/jobs/~abc123", // Unique index
  "source": "vollna",
  "region": "United States",
  "posted_at": ISODate("2025-01-15T10:00:00Z"), // Indexed (descending)
  "skills": ["Python", "FastAPI"], // Indexed
  "budget": 50.0, // Indexed (descending)
  "proposals": 5, // Indexed (ascending)
  "client": {
    "rating": 4.8,
    "payment_verified": true
  },
  "raw": {
    "original_vollna_payload": {...}
  },
  "created_at": ISODate("..."),
  "updated_at": ISODate("..."),
  "last_seen_at": ISODate("...")
}
```

### Indexes

**jobs_raw**:
- `url` (unique)
- `posted_at` (descending)
- `source` (ascending)
- `budget` (descending)
- `proposals` (ascending)
- `created_at` (descending)

**jobs_filtered**:
- `url` (unique)
- `posted_at` (descending)
- `source` (ascending)
- `budget` (descending)
- `proposals` (ascending)
- `skills` (ascending)

## 🧪 7. Testing

### Test Vollna Webhook

```bash
curl -X POST http://localhost:8000/vollna/jobs \
  -H "Content-Type: application/json" \
  -H "X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394" \
  -d '{
    "title": "Test Job",
    "description": "Test description",
    "url": "https://www.upwork.com/jobs/~test123",
    "budget": 50.0,
    "proposals": 5,
    "skills": ["Python"],
    "postedOn": "2025-01-15T10:00:00Z"
  }'
```

### Test Job Search

```bash
curl -X POST http://localhost:8000/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "min_budget": 30.0,
    "max_proposals": 10,
    "skills": ["Python"],
    "keywords": ["backend"],
    "source": "vollna",
    "limit": 10
  }'
```

### Test Recommendations

```bash
curl -X POST "http://localhost:8000/jobs/recommend?user_skills=Python,FastAPI&prioritize_budget=true" \
  -H "Content-Type: application/json" \
  -d '{
    "min_budget": 30.0,
    "max_proposals": 10,
    "skills": ["Python"],
    "limit": 10
  }'
```

## 📝 8. Real-Time Updates

### Workflow

1. **Vollna detects new job** → Sends to n8n webhook
2. **n8n normalizes** → Forwards to `/vollna/jobs`
3. **Backend stores** → MongoDB (deduplicated)
4. **Chatbot polls** → `GET /jobs?source=vollna&limit=10` (newest first)
5. **Chatbot displays** → New jobs to user

### Polling Strategy

```javascript
// Poll for new jobs every 30 seconds
setInterval(async () => {
  const jobs = await fetch('http://localhost:8000/jobs?source=vollna&limit=10')
    .then(r => r.json());
  
  // Compare with last seen jobs
  const newJobs = jobs.filter(job => 
    !seenJobIds.has(job.id)
  );
  
  if (newJobs.length > 0) {
    displayNewJobs(newJobs);
    newJobs.forEach(job => seenJobIds.add(job.id));
  }
}, 30000);
```

## ✅ 9. Checklist

- [x] Vollna extension installed and configured
- [x] n8n webhook created
- [x] n8n workflow normalizes payload
- [x] n8n forwards to `/vollna/jobs` with secret header
- [x] Backend endpoint `/vollna/jobs` receives and processes
- [x] MongoDB indexes created (posted_at, budget, proposals, skills)
- [x] Jobs deduplicated by URL
- [x] Feed status tracked
- [x] Chatbot integrated with `/jobs/search`
- [x] Chatbot uses `/jobs/recommend` for AI ranking
- [x] Chatbot can generate proposals via `/ai/generate-proposal`
- [x] Security: n8n secret configured
- [x] Security: No scraping code
- [x] Testing: All endpoints tested

## 🚨 Troubleshooting

### Error: "invalid n8n secret"

**Solution**: Check `.env` file has `N8N_SHARED_SECRET` set, and n8n sends it in `X-N8N-Secret` header.

### Error: "No valid jobs found in Vollna payload"

**Solution**: Ensure payload has `title`, `description`, and `url` fields. Check n8n normalization code.

### Jobs not appearing in search

**Solution**: 
1. Check jobs are in `jobs_filtered` collection (not just `jobs_raw`)
2. Verify filters match job data (e.g., skills, budget)
3. Check MongoDB indexes are created

### Chatbot not getting real-time updates

**Solution**: Implement polling or WebSocket connection. See "Real-Time Updates" section above.

## 📚 Additional Resources

- **Swagger UI**: `http://localhost:8000/docs`
- **API Health**: `http://localhost:8000/health`
- **Feed Status**: `GET /feeds/status?source=vollna`

