# Render Deployment Checklist

Use this checklist to ensure a smooth deployment to Render.

## ✅ Pre-Deployment

### Code Preparation
- [x] All code committed to Git
- [x] `render.yaml` created in project root
- [x] `Procfile` created (alternative to render.yaml)
- [x] `requirements.txt` exists in `backend/` directory
- [x] `.renderignore` created (optional, excludes unnecessary files)
- [x] `runtime.txt` created (specifies Python version)

### Configuration Files
- [x] `render.yaml` configured with correct paths
- [x] Start command uses `$PORT` environment variable
- [x] Build command installs from `backend/requirements.txt`

### Environment Variables Ready
- [ ] MongoDB connection string ready (MongoDB Atlas or Render MongoDB)
- [ ] `N8N_SHARED_SECRET` value ready
- [ ] `OPENAI_API_KEY` ready (if using AI features)

## 🚀 Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create Render Service
- [ ] Go to https://dashboard.render.com
- [ ] Click "New +" → "Blueprint" (if using render.yaml)
- [ ] OR "New +" → "Web Service" (manual setup)
- [ ] Connect GitHub repository
- [ ] Select branch (usually `main`)

### 3. Configure Service
- [ ] Service name: `upwork-proposal-bot`
- [ ] Environment: `Python 3`
- [ ] Build command: `pip install -r backend/requirements.txt`
- [ ] Start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 4. Set Environment Variables
- [ ] `MONGODB_URI` - MongoDB connection string
- [ ] `MONGODB_DB` - `upwork_proposal_bot`
- [ ] `N8N_SHARED_SECRET` - Your secret key
- [ ] `OPENAI_API_KEY` - OpenAI API key (optional)
- [ ] `LOG_LEVEL` - `INFO`

### 5. Deploy
- [ ] Click "Create Web Service" or "Apply"
- [ ] Wait for build to complete
- [ ] Check build logs for errors

## ✅ Post-Deployment Verification

### Health Check
- [ ] Service URL accessible: `https://your-service.onrender.com`
- [ ] Health endpoint works: `GET /health`
- [ ] Returns: `{"status": "ok", "database": "connected"}`

### API Documentation
- [ ] Swagger UI accessible: `https://your-service.onrender.com/docs`
- [ ] All endpoints visible in Swagger

### Test Endpoints
- [ ] `GET /` - Returns service info
- [ ] `GET /health` - Returns health status
- [ ] `POST /vollna/jobs` - Webhook endpoint (test with curl)

### Integration Updates
- [ ] n8n webhook URL updated to Render URL
- [ ] Chatbot API endpoints updated to Render URL
- [ ] Vollna extension configured with new webhook URL

## 🔍 Troubleshooting

### Build Fails
- [ ] Check `requirements.txt` has all dependencies
- [ ] Verify Python version in `runtime.txt` (if used)
- [ ] Check build logs for specific errors

### Service Won't Start
- [ ] Verify start command uses `$PORT`
- [ ] Check environment variables are set
- [ ] Review service logs for errors

### Database Connection Fails
- [ ] Verify `MONGODB_URI` is correct
- [ ] Check MongoDB network access allows Render IPs
- [ ] Verify MongoDB user has correct permissions
- [ ] Test connection string locally first

### Health Check Fails
- [ ] Check MongoDB connection
- [ ] Verify all environment variables are set
- [ ] Review service logs

## 📊 Monitoring Setup

- [ ] Enable Render monitoring (automatic)
- [ ] Set up log aggregation (if needed)
- [ ] Configure alerts (optional)

## 🔒 Security Checklist

- [ ] All sensitive variables marked as "Secret" in Render
- [ ] MongoDB connection uses strong password
- [ ] `N8N_SHARED_SECRET` is secure and unique
- [ ] Network access restricted where possible

## 📝 Notes

- **Free Tier**: Service sleeps after 15 minutes of inactivity
- **First Request**: May take 30-60 seconds to wake up
- **Upgrade**: Consider paid plan for always-on service

## 🎯 Next Steps After Deployment

1. Test all endpoints via Swagger UI
2. Update n8n workflow with new webhook URL
3. Update chatbot with new API endpoints
4. Monitor logs for first 24 hours
5. Set up MongoDB backups (if using MongoDB Atlas)

## 📚 Resources

- **Render Docs**: https://render.com/docs
- **Deployment Guide**: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
- **API Docs**: `https://your-service.onrender.com/docs`

