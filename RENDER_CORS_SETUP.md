# Render CORS Environment Variable Setup

## 🎯 Purpose

Configure CORS origins in Render to allow your localhost frontend to access the API.

## 📋 Step-by-Step Instructions

### Step 1: Open Render Dashboard

1. Go to https://dashboard.render.com
2. Select your service: `upwork-xxsc` (or your service name)
3. Click on **"Environment"** tab in the left sidebar

### Step 2: Add CORS_ORIGINS Variable

1. Click **"Add Environment Variable"** button
2. **Key**: `CORS_ORIGINS`
3. **Value**: `http://localhost:8081,http://localhost:3000,http://localhost:5173,http://127.0.0.1:8081`
4. Click **"Save Changes"**

### Step 3: Add Production Frontend (Optional)

If you have a production frontend URL, add it to the list:

**Value**: `http://localhost:8081,http://localhost:3000,http://localhost:5173,http://127.0.0.1:8081,https://your-frontend-domain.com`

### Step 4: Deploy

Render will automatically redeploy when you save environment variables. Wait 2-5 minutes for deployment to complete.

## 🔧 Environment Variable Format

**Format**: Comma-separated list of URLs (no spaces around commas)

**Example**:
```
http://localhost:8081,http://localhost:3000,https://myapp.com
```

**Allowed Origins**:
- `http://localhost:8081` - Your current frontend
- `http://localhost:3000` - React default port
- `http://localhost:5173` - Vite default port
- `http://127.0.0.1:8081` - Alternative localhost format
- `https://your-production-domain.com` - Production frontend

## 📝 Complete Environment Variables List

Here are all environment variables you should have in Render:

| Variable | Value | Description |
|----------|-------|-------------|
| `MONGODB_URI` | `mongodb+srv://...` | MongoDB Atlas connection string |
| `MONGODB_DB` | `upwork_proposal_bot` | Database name |
| `N8N_SHARED_SECRET` | `9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394` | Secret for webhook auth |
| `OPENAI_API_KEY` | `sk-...` | OpenAI API key (optional) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `http://localhost:8081,http://localhost:3000,http://localhost:5173` | Allowed CORS origins |

## ✅ Verification

After deployment, test in your browser console (on localhost:8081):

```javascript
fetch('https://upwork-xxsc.onrender.com/api/jobs?source=vollna&limit=10')
  .then(r => r.json())
  .then(data => console.log('✅ CORS working!', data))
  .catch(err => console.error('❌ CORS error:', err));
```

**Expected**: Should return jobs data without CORS errors.

## 🔍 Troubleshooting

### Issue: Still getting CORS errors

**Check**:
1. Is the environment variable set correctly? (no extra spaces)
2. Did Render finish deploying? (check deployment logs)
3. Are you using the correct frontend URL? (must match exactly)
4. Clear browser cache and try again

### Issue: Environment variable not taking effect

**Solution**:
1. Check Render deployment logs for errors
2. Verify variable name is exactly `CORS_ORIGINS` (case-sensitive)
3. Restart the service manually in Render dashboard

### Issue: Need to add more origins

**Solution**:
1. Edit `CORS_ORIGINS` in Render dashboard
2. Add new URL to comma-separated list
3. Save and wait for redeploy

## 📊 Default Values

If `CORS_ORIGINS` is not set, the backend defaults to:
- `http://localhost:8081`
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:8081`

## 🚀 Quick Setup Command

You can also set this via Render CLI (if you have it installed):

```bash
render env:set CORS_ORIGINS="http://localhost:8081,http://localhost:3000,http://localhost:5173" --service upwork-xxsc
```

## 📝 Notes

- **No spaces**: Don't add spaces around commas in the value
- **Case sensitive**: Variable name must be exactly `CORS_ORIGINS`
- **Protocol required**: Include `http://` or `https://` in URLs
- **Port required**: Include port number for localhost URLs
- **Auto-redeploy**: Render automatically redeploys when you save environment variables

