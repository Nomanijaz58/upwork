# Render CORS Configuration Update

## ✅ Code Changes Applied

### 1. Frontend API Base URL
**File**: `src/lib/api/config.ts`
- Changed default from `http://localhost:8000` to `https://upwork-xxsc.onrender.com`
- Frontend now calls live backend by default

### 2. Backend CORS Settings
**Files**: 
- `backend/app/core/settings.py` - Already includes `localhost:8080` ✅
- `backend/app/main.py` - CORS middleware configured ✅

## 🔧 Required: Update Render Environment Variable

You need to manually update the `CORS_ORIGINS` environment variable on Render:

### Steps:
1. Go to https://dashboard.render.com
2. Select your service: `upwork-xxsc`
3. Go to **Environment** tab
4. Find or add: `CORS_ORIGINS`
5. Set value to:
   ```
   http://localhost:8080,http://localhost:8081,http://localhost:3000,http://localhost:5173,http://127.0.0.1:8080,http://127.0.0.1:8081
   ```
6. Click **Save Changes**
7. Render will automatically redeploy

## ✅ Current Status

- ✅ Frontend configured to use live backend
- ✅ Backend code includes `localhost:8080` in CORS
- ⏳ **Action Required**: Update Render environment variable

## 🧪 Test After Update

Once Render redeploys, test from browser console:

```javascript
fetch("https://upwork-xxsc.onrender.com/jobs/all")
  .then(res => res.json())
  .then(data => {
    console.log("Jobs from Vollna:", data.jobs);
    console.log("Total jobs:", data.count);
  });
```

**Expected**: Should work without CORS errors!

---

**Note**: The code changes are ready. Just update the Render environment variable and redeploy! 🚀

