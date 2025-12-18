# Render Deployment Guide

Complete guide for deploying the Upwork Proposal Bot to Render.

## 🚀 Quick Deploy

### Option 1: Using render.yaml (Recommended)

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Connect to Render**:
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically
   - Click "Apply"

3. **Set Environment Variables**:
   - Go to your service → Environment
   - Add the following variables:
     - `MONGODB_URI` - Your MongoDB connection string (from MongoDB Atlas or Render MongoDB)
     - `MONGODB_DB` - Database name (default: `upwork_proposal_bot`)
     - `N8N_SHARED_SECRET` - Your n8n secret key
     - `OPENAI_API_KEY` - Your OpenAI API key (optional, for AI features)
     - `LOG_LEVEL` - Logging level (default: `INFO`)

4. **Deploy**: Render will automatically deploy your service

### Option 2: Manual Setup

1. **Create New Web Service**:
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**:
   - **Name**: `upwork-proposal-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables** (same as above)

4. **Deploy**: Click "Create Web Service"

## 📋 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net` |
| `MONGODB_DB` | Database name | `upwork_proposal_bot` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `N8N_SHARED_SECRET` | Secret for n8n webhook authentication | None |
| `OPENAI_API_KEY` | OpenAI API key for AI features | None |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |

## 🗄️ MongoDB Setup

### Option 1: MongoDB Atlas (Recommended)

1. **Create MongoDB Atlas Account**:
   - Go to https://www.mongodb.com/cloud/atlas
   - Sign up for free tier

2. **Create Cluster**:
   - Create a free M0 cluster
   - Choose your region

3. **Get Connection String**:
   - Go to "Database Access" → Create database user
   - Go to "Network Access" → Add IP (0.0.0.0/0 for Render)
   - Go to "Database" → "Connect" → "Connect your application"
   - Copy connection string

4. **Set in Render**:
   - Format: `mongodb+srv://username:password@cluster.mongodb.net`
   - Set as `MONGODB_URI` environment variable

### Option 2: Render MongoDB (Beta)

1. **Create MongoDB Service**:
   - Go to Render Dashboard
   - Click "New +" → "MongoDB"
   - Choose plan (Free tier available)

2. **Get Connection String**:
   - Go to MongoDB service → "Info"
   - Copy "Internal Connection String"
   - Use format: `mongodb://user:pass@host:port`

3. **Set in Render**:
   - Set as `MONGODB_URI` environment variable

## 🔧 Configuration Files

### render.yaml

Located in project root. Contains:
- Service configuration
- Build and start commands
- Environment variables (non-sensitive)

### Procfile

Alternative to render.yaml. Contains:
- Start command for web service

## 🌐 Post-Deployment

### 1. Verify Deployment

Check your service URL:
```bash
curl https://your-service.onrender.com/health
```

Expected response:
```json
{
  "status": "ok",
  "database": "connected"
}
```

### 2. Update n8n Webhook

Update your n8n workflow to use the Render URL:
- Old: `http://localhost:8000/vollna/jobs`
- New: `https://your-service.onrender.com/vollna/jobs`

### 3. Update Chatbot

Update chatbot API endpoints:
- Old: `http://localhost:8000`
- New: `https://your-service.onrender.com`

### 4. Access API Documentation

Swagger UI available at:
```
https://your-service.onrender.com/docs
```

## 🔒 Security Checklist

- [ ] `N8N_SHARED_SECRET` is set and secure
- [ ] MongoDB connection string uses strong password
- [ ] MongoDB network access restricted (if possible)
- [ ] `OPENAI_API_KEY` is set (if using AI features)
- [ ] Environment variables marked as "Secret" in Render

## 📊 Monitoring

### Health Check

Render automatically monitors:
- `GET /health` endpoint
- Service uptime
- Response times

### Logs

View logs in Render Dashboard:
- Go to your service → "Logs"
- Real-time log streaming
- Search and filter logs

## 🚨 Troubleshooting

### Service Won't Start

**Error**: "Module not found"
- **Solution**: Check `requirements.txt` includes all dependencies

**Error**: "MongoDB connection failed"
- **Solution**: Verify `MONGODB_URI` is correct and MongoDB allows connections from Render IPs

**Error**: "Port already in use"
- **Solution**: Ensure start command uses `$PORT` environment variable

### Health Check Failing

**Error**: "Database disconnected"
- **Solution**: 
  1. Check MongoDB connection string
  2. Verify MongoDB network access allows Render IPs
  3. Check MongoDB user has correct permissions

### Environment Variables Not Working

**Issue**: Variables not being read
- **Solution**: 
  1. Ensure variables are set in Render Dashboard
  2. Restart service after adding variables
  3. Check variable names match exactly (case-sensitive)

## 🔄 Continuous Deployment

Render automatically deploys when you push to:
- `main` branch (production)
- Other branches (preview deployments)

To disable auto-deploy:
- Go to service → Settings → "Auto-Deploy" → Disable

## 📈 Scaling

### Free Tier Limitations

- **Sleeps after 15 minutes** of inactivity
- **512 MB RAM**
- **0.1 CPU**

### Paid Plans

- **Starter**: $7/month - Always on, 512 MB RAM
- **Standard**: $25/month - Always on, 2 GB RAM
- **Pro**: $85/month - Always on, 4 GB RAM

## 🎯 Next Steps

1. **Set up MongoDB Atlas** (if not using Render MongoDB)
2. **Configure environment variables** in Render
3. **Deploy service** using render.yaml or manual setup
4. **Test endpoints** using Swagger UI
5. **Update n8n webhook** URL
6. **Update chatbot** API endpoints
7. **Monitor logs** for any issues

## 📚 Additional Resources

- **Render Docs**: https://render.com/docs
- **MongoDB Atlas**: https://www.mongodb.com/docs/atlas
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **API Documentation**: `https://your-service.onrender.com/docs`

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] MongoDB Atlas cluster created (or Render MongoDB)
- [ ] MongoDB connection string obtained
- [ ] Render service created
- [ ] Environment variables set
- [ ] Service deployed successfully
- [ ] Health check passing
- [ ] API documentation accessible
- [ ] n8n webhook updated
- [ ] Chatbot endpoints updated
- [ ] Tested all endpoints

