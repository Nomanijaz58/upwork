# CORS Fix Guide - Frontend Integration

## 🔧 Problem

Frontend at `http://localhost:8081` was getting CORS errors when trying to fetch from `https://upwork-xxsc.onrender.com/api/jobs`.

**Error**: `Access to fetch at 'https://upwork-xxsc.onrender.com/api/jobs' from origin 'http://localhost:8081' has been blocked by CORS policy`

## ✅ Solution Applied

### 1. Added CORS Middleware

CORS middleware has been added to `backend/app/main.py` to allow requests from:
- `http://localhost:8081` (your frontend)
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)
- `http://127.0.0.1:8081` (alternative localhost)

### 2. Added `/api/jobs` Endpoint

Added an alias endpoint at `/api/jobs` to match your frontend's API path:
- Frontend calls: `GET /api/jobs`
- Backend provides: `GET /api/jobs` (alias to `/jobs/latest`)

## 📋 Available Endpoints

### For Frontend Integration

| Frontend Call | Backend Endpoint | Purpose |
|---------------|------------------|---------|
| `GET /api/jobs` | `GET /api/jobs` | Get latest jobs (alias) |
| `GET /jobs/latest` | `GET /jobs/latest` | Get latest jobs (original) |
| `POST /jobs/search` | `POST /jobs/search` | Search with filters |
| `POST /jobs/recommend` | `POST /jobs/recommend` | AI recommendations |

## 🔍 Frontend Code Example

### Correct API URL

```javascript
// ✅ Correct - Use full backend URL
const API_URL = 'https://upwork-xxsc.onrender.com';

// Get latest jobs
async function loadJobs() {
  const response = await fetch(`${API_URL}/api/jobs?source=vollna&limit=50`);
  const jobs = await response.json();
  return jobs;
}

// Search jobs
async function searchJobs(filters) {
  const response = await fetch(`${API_URL}/jobs/search`, {
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
  return result.filtered_jobs;
}
```

## 🧪 Testing

### Test CORS Fix

```bash
# Test from browser console (on localhost:8081)
fetch('https://upwork-xxsc.onrender.com/api/jobs?source=vollna&limit=10')
  .then(r => r.json())
  .then(data => console.log('Success:', data))
  .catch(err => console.error('Error:', err));
```

**Expected**: Should return jobs array without CORS errors.

### Test with cURL

```bash
# Test the endpoint
curl "https://upwork-xxsc.onrender.com/api/jobs?source=vollna&limit=10"

# Test CORS headers
curl -H "Origin: http://localhost:8081" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     "https://upwork-xxsc.onrender.com/api/jobs" \
     -v
```

**Expected**: Should see `Access-Control-Allow-Origin: http://localhost:8081` in response headers.

## 🚀 After Deployment

1. **Wait for Render to deploy** (2-5 minutes)
2. **Test in browser console** on `localhost:8081`:
   ```javascript
   fetch('https://upwork-xxsc.onrender.com/api/jobs?source=vollna&limit=10')
     .then(r => r.json())
     .then(console.log);
   ```
3. **Verify no CORS errors** in browser console
4. **Check network tab** - should see successful requests

## 📝 Notes

- CORS is configured for development (localhost ports)
- For production, add your production frontend URL to `allow_origins` list
- All HTTP methods are allowed (`allow_methods=["*"]`)
- All headers are allowed (`allow_headers=["*"]`)

## 🔄 If Still Getting Errors

1. **Check browser console** for exact error message
2. **Verify backend is deployed** - check `https://upwork-xxsc.onrender.com/health`
3. **Check network tab** - see if request is reaching backend
4. **Verify API URL** - make sure frontend is calling correct endpoint
5. **Clear browser cache** - sometimes cached CORS errors persist

## ✅ Success Criteria

- ✅ No CORS errors in browser console
- ✅ Jobs data loads successfully
- ✅ Network requests show 200 status
- ✅ Response includes `Access-Control-Allow-Origin` header

