# Local Server Guide

## ✅ Server Running!

Your backend server is now running on **localhost:8000**

## 🔗 Available URLs

### Main Endpoints:
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Root**: http://localhost:8000/

### Jobs Endpoints:
- **Get All Vollna Jobs**: http://localhost:8000/api/jobs?source=vollna&limit=1000
- **Get Latest Jobs**: http://localhost:8000/jobs/latest?source=vollna&limit=1000
- **Search Jobs**: http://localhost:8000/jobs/search (POST)
- **Recommend Jobs**: http://localhost:8000/jobs/recommend (POST)

### Webhook Endpoints:
- **Vollna Webhook**: http://localhost:8000/webhook/vollna (POST)
- **Vollna Jobs**: http://localhost:8000/vollna/jobs (POST)

## 🧪 Quick Tests

### Test Health:
```bash
curl http://localhost:8000/health
```

### Test Jobs API:
```bash
curl "http://localhost:8000/api/jobs?source=vollna&limit=10"
```

### Test in Browser:
- Open: http://localhost:8000/docs
- Try out endpoints in Swagger UI

## 🔧 Frontend Configuration

Update your frontend to use localhost for development:

**Option 1: Environment Variable**
```bash
# In job-scout-pro-main/.env
VITE_API_BASE_URL=http://localhost:8000
```

**Option 2: Update config.ts**
```typescript
// src/lib/api/config.ts
export const API_BASE_URL = 'http://localhost:8000';
```

## 📝 Server Commands

### Start Server:
```bash
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Stop Server:
Press `Ctrl+C` in the terminal where server is running

### Check if Running:
```bash
curl http://localhost:8000/health
```

## 🐛 Troubleshooting

### Port Already in Use:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### MongoDB Connection Error:
- Check `.env` file has correct `MONGODB_URI`
- Verify MongoDB is running (if local) or Atlas connection is correct

### Import Errors:
- Make sure you're in the `backend` directory
- Check virtual environment is activated (if using one)
- Install dependencies: `pip install -r requirements.txt`

## ✅ Server Features

- ✅ Auto-reload on code changes (`--reload` flag)
- ✅ CORS enabled for localhost:8081
- ✅ All endpoints available
- ✅ Swagger UI at /docs
- ✅ Health check at /health

---

**Server is ready!** Test endpoints at http://localhost:8000/docs 🚀

