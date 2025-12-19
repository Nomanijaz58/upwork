# Frontend Integration Guide - Display All Vollna Jobs

## 🎯 Goal

Configure your frontend (`job-scout-pro-main`) to display ALL jobs from your Vollna/Upwork feed.

## 📋 Backend API Endpoints

Your backend is ready at: `https://upwork-xxsc.onrender.com`

**Key Endpoints**:
- `GET /api/jobs?source=vollna&limit=1000` - Get all Vollna jobs (up to 1000)
- `POST /jobs/search` - Search with filters
- `POST /jobs/recommend` - AI recommendations

## 🔧 Frontend Configuration

### Step 1: Find Your API Configuration

Look for these files in your `job-scout-pro-main` folder:
- `src/config.js` or `config.ts`
- `src/api/client.ts` or `api.ts`
- `.env` or `.env.local`
- `src/services/api.js` or `api.ts`
- Any file with "API" or "config" in the name

### Step 2: Set API Base URL

**Option A: Environment Variable (Recommended)**

Create or update `.env` file:
```bash
VITE_API_URL=https://upwork-xxsc.onrender.com
# or
REACT_APP_API_URL=https://upwork-xxsc.onrender.com
# or
NEXT_PUBLIC_API_URL=https://upwork-xxsc.onrender.com
```

**Option B: Config File**

Update your config file:
```javascript
// config.js or api.js
export const API_URL = 'https://upwork-xxsc.onrender.com';
```

### Step 3: Update Job Fetching Code

Find where your frontend fetches jobs (look for `fetch`, `axios`, or `api.get`):

**Before (if exists)**:
```javascript
// ❌ Old - might be fetching from wrong endpoint
fetch('/api/jobs')
```

**After (Correct)**:
```javascript
// ✅ Correct - Get ALL jobs from Vollna
const API_URL = import.meta.env.VITE_API_URL || 'https://upwork-xxsc.onrender.com';

async function loadAllJobs() {
  try {
    const response = await fetch(`${API_URL}/api/jobs?source=vollna&limit=1000`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const jobs = await response.json();
    console.log(`Loaded ${jobs.length} jobs from Vollna`);
    return jobs;
  } catch (error) {
    console.error('Error loading jobs:', error);
    return [];
  }
}
```

### Step 4: Update Polling/Refresh Logic

If you have auto-refresh, update it:

```javascript
// Poll every 10-15 seconds for new jobs
useEffect(() => {
  const loadJobs = async () => {
    const jobs = await loadAllJobs();
    setJobs(jobs);
  };
  
  // Load immediately
  loadJobs();
  
  // Then poll every 10 seconds
  const interval = setInterval(loadJobs, 10000);
  
  return () => clearInterval(interval);
}, []);
```

## 📝 Common Frontend Frameworks

### React (with hooks)

```javascript
import { useState, useEffect } from 'react';

const API_URL = 'https://upwork-xxsc.onrender.com';

function JobList() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/api/jobs?source=vollna&limit=1000`);
        const data = await response.json();
        setJobs(data);
      } catch (error) {
        console.error('Error fetching jobs:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
    
    // Poll every 10 seconds
    const interval = setInterval(fetchJobs, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading jobs...</div>;

  return (
    <div>
      <h2>All Jobs from Vollna ({jobs.length})</h2>
      {jobs.map(job => (
        <div key={job.id} className="job-card">
          <h3>{job.title}</h3>
          <p>Budget: ${job.budget}/hr</p>
          <p>Proposals: {job.proposals}</p>
          <p>Skills: {job.skills.join(', ')}</p>
          <a href={job.url} target="_blank">View on Upwork</a>
        </div>
      ))}
    </div>
  );
}
```

### Vue.js

```javascript
<template>
  <div>
    <h2>All Jobs from Vollna ({{ jobs.length }})</h2>
    <div v-for="job in jobs" :key="job.id" class="job-card">
      <h3>{{ job.title }}</h3>
      <p>Budget: ${{ job.budget }}/hr</p>
      <p>Proposals: {{ job.proposals }}</p>
      <a :href="job.url" target="_blank">View on Upwork</a>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      jobs: [],
      API_URL: 'https://upwork-xxsc.onrender.com'
    };
  },
  mounted() {
    this.loadJobs();
    // Poll every 10 seconds
    setInterval(this.loadJobs, 10000);
  },
  methods: {
    async loadJobs() {
      try {
        const response = await fetch(`${this.API_URL}/api/jobs?source=vollna&limit=1000`);
        this.jobs = await response.json();
      } catch (error) {
        console.error('Error loading jobs:', error);
      }
    }
  }
};
</script>
```

### Vanilla JavaScript

```javascript
const API_URL = 'https://upwork-xxsc.onrender.com';

async function loadAllJobs() {
  try {
    const response = await fetch(`${API_URL}/api/jobs?source=vollna&limit=1000`);
    const jobs = await response.json();
    displayJobs(jobs);
  } catch (error) {
    console.error('Error loading jobs:', error);
  }
}

function displayJobs(jobs) {
  const container = document.getElementById('job-list');
  container.innerHTML = jobs.map(job => `
    <div class="job-card">
      <h3>${job.title}</h3>
      <p>Budget: $${job.budget || 'Not specified'}/hr</p>
      <p>Proposals: ${job.proposals || 'N/A'}</p>
      <p>Skills: ${job.skills.join(', ')}</p>
      <a href="${job.url}" target="_blank">View on Upwork</a>
    </div>
  `).join('');
}

// Load on page load
loadAllJobs();

// Poll every 10 seconds
setInterval(loadAllJobs, 10000);
```

## 🔍 Finding Your Frontend Code

### Search for API calls:

```bash
# In your job-scout-pro-main folder
cd /path/to/job-scout-pro-main

# Search for API calls
grep -r "fetch\|axios\|api" src/ --include="*.js" --include="*.ts" --include="*.jsx" --include="*.tsx"

# Search for API URL
grep -r "api\|API\|localhost:8000\|upwork-xxsc" src/ --include="*.js" --include="*.ts"
```

### Common file locations:

- **React**: `src/App.js`, `src/components/JobList.js`, `src/services/api.js`
- **Vue**: `src/views/Jobs.vue`, `src/services/api.js`
- **Next.js**: `pages/jobs.js`, `app/jobs/page.js`, `lib/api.js`
- **Angular**: `src/app/services/job.service.ts`

## ✅ Quick Checklist

- [ ] Found API configuration file
- [ ] Set API URL to `https://upwork-xxsc.onrender.com`
- [ ] Updated fetch call to `/api/jobs?source=vollna&limit=1000`
- [ ] Added `source=vollna` parameter
- [ ] Increased limit to 1000 (or removed limit)
- [ ] Tested in browser - jobs should load
- [ ] Verified CORS is working (no CORS errors)

## 🧪 Testing

### Test in Browser Console:

```javascript
// Test API connection
fetch('https://upwork-xxsc.onrender.com/api/jobs?source=vollna&limit=10')
  .then(r => r.json())
  .then(jobs => console.log('Jobs loaded:', jobs.length, jobs))
  .catch(err => console.error('Error:', err));
```

**Expected**: Should return array of jobs without CORS errors.

### Test with cURL:

```bash
curl "https://upwork-xxsc.onrender.com/api/jobs?source=vollna&limit=10"
```

## 🐛 Troubleshooting

### Issue: No jobs showing

**Check**:
1. Are jobs in database? Test: `curl "https://upwork-xxsc.onrender.com/api/jobs?source=vollna&limit=10"`
2. Is Vollna webhook configured? (See `VOLLNA_FEED_SETUP.md`)
3. Is frontend calling correct endpoint? Check browser Network tab

### Issue: CORS errors

**Solution**: 
- Backend CORS is configured
- Make sure frontend URL is in `CORS_ORIGINS` in Render
- Check browser console for exact error

### Issue: Wrong endpoint

**Solution**:
- Use: `GET /api/jobs?source=vollna&limit=1000`
- Not: `/api/jobs` (missing source parameter)
- Not: `/jobs` (wrong path)

## 📊 Job Data Structure

Each job object has this structure:

```json
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
```

## 🚀 Next Steps

1. **Find your frontend code** in `job-scout-pro-main`
2. **Update API URL** to `https://upwork-xxsc.onrender.com`
3. **Update fetch call** to `/api/jobs?source=vollna&limit=1000`
4. **Test** - jobs should appear
5. **Set up Vollna webhook** - so real jobs start flowing (see `VOLLNA_FEED_SETUP.md`)

Once configured, all jobs from your Vollna feed will display on your frontend! 🎉

