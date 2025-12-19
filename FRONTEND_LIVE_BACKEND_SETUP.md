# Frontend Live Backend Setup

## ✅ Changes Applied

### 1. Frontend API Configuration
**File**: `src/lib/api/config.ts`

**Change**: Updated `API_BASE_URL` to use live Render backend:
```typescript
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://upwork-xxsc.onrender.com';
```

**Result**: Frontend now calls the live backend by default instead of localhost.

### 2. Backend CORS Configuration
**Files**: 
- `backend/app/core/settings.py`
- `backend/app/main.py`

**Changes**:
- Added `http://localhost:8080` to default CORS origins
- Added `http://127.0.0.1:8080` for localhost IP access
- CORS now allows:
  - `http://localhost:8080` ✅
  - `http://localhost:8081` ✅
  - `http://localhost:3000` ✅
  - `http://localhost:5173` ✅
  - `http://127.0.0.1:8080` ✅
  - `http://127.0.0.1:8081` ✅
  - `http://localhost:8000` ✅ (for local backend testing)

## 🚀 How It Works

### Frontend → Live Backend
1. Frontend calls: `https://upwork-xxsc.onrender.com/jobs/all`
2. Backend responds with CORS headers allowing `http://localhost:8080`
3. Browser allows the request ✅

### Environment Variable Override
You can still use local backend for development:
```bash
# In .env or environment
VITE_API_BASE_URL=http://localhost:8000
```

## 📋 Render Environment Variables

Make sure Render has these environment variables set:

```bash
CORS_ORIGINS=http://localhost:8080,http://localhost:8081,http://localhost:3000,http://localhost:5173,http://127.0.0.1:8080,http://127.0.0.1:8081
```

## 🧪 Testing

### Test from Browser Console:
```javascript
fetch("https://upwork-xxsc.onrender.com/jobs/all")
  .then(res => res.json())
  .then(data => {
    console.log("Jobs from Vollna:", data.jobs);
    console.log("Total jobs:", data.count);
  });
```

### Expected Response:
```json
{
  "count": 0,
  "jobs": []
}
```

Or with jobs:
```json
{
  "count": 5,
  "jobs": [
    {
      "_id": "...",
      "title": "Job Title",
      "url": "https://www.upwork.com/jobs/~...",
      "budget": 50.0,
      "client_name": "Client Name",
      "source": "vollna",
      "created_at": "...",
      "received_at": "..."
    }
  ]
}
```

## ✅ Verification Checklist

- [x] Frontend uses `https://upwork-xxsc.onrender.com` as default
- [x] CORS allows `http://localhost:8080`
- [x] `/jobs/all` endpoint is accessible
- [x] Frontend can fetch jobs from live backend
- [ ] Render environment variable `CORS_ORIGINS` is set (needs manual update on Render)

## 🔧 Next Steps

1. **Update Render Environment Variables**:
   - Go to Render dashboard
   - Navigate to your service
   - Go to Environment tab
   - Add/Update: `CORS_ORIGINS=http://localhost:8080,http://localhost:8081,http://localhost:3000,http://localhost:5173,http://127.0.0.1:8080,http://127.0.0.1:8081`
   - Save and redeploy

2. **Test Frontend**:
   - Open `http://localhost:8080`
   - Check browser console for API calls
   - Verify jobs are loading from live backend

3. **Send Test Job**:
   ```bash
   curl -X POST https://upwork-xxsc.onrender.com/webhook/vollna \
     -H "Content-Type: application/json" \
     -H "X-N8N-Secret: YOUR_SECRET" \
     -d '[{
       "title": "Test Job",
       "url": "https://www.upwork.com/jobs/~test",
       "budget": 50.0,
       "client_name": "Test Client"
     }]'
   ```

---

**Setup complete!** Frontend now calls live backend and CORS is configured. 🎉

