# Render Deployment Steps - Quick Guide

## ✅ Step 1: Code is Already on GitHub
Your code is now at: https://github.com/Nomanijaz58/upwork.git

## 🚀 Step 2: Deploy on Render

### Option A: Using Blueprint (Recommended - Easiest)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign up or log in

2. **Create New Blueprint**
   - Click "New +" button (top right)
   - Select "Blueprint"
   - Click "Connect account" to connect your GitHub account
   - Authorize Render to access your repositories

3. **Select Repository**
   - Find and select: `Nomanijaz58/upwork`
   - Render will automatically detect `render.yaml`
   - Click "Apply"

4. **Set Environment Variables**
   - After the service is created, go to your service
   - Click on "Environment" tab
   - Add these variables:

   | Variable | Value | Notes |
   |----------|-------|-------|
   | `MONGODB_URI` | `mongodb+srv://...` | Your MongoDB connection string |
   | `MONGODB_DB` | `upwork_proposal_bot` | Database name |
   | `N8N_SHARED_SECRET` | `your-secret-here` | Secret for n8n webhooks |
   | `OPENAI_API_KEY` | `sk-...` | OpenAI API key (optional) |
   | `LOG_LEVEL` | `INFO` | Logging level |

5. **Deploy**
   - Render will automatically start deploying
   - Wait for build to complete (2-5 minutes)
   - Check build logs for any errors

### Option B: Manual Setup

1. **Create New Web Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select repository: `Nomanijaz58/upwork`

2. **Configure Service**
   - **Name**: `upwork-proposal-bot`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `backend` if needed)
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables** (same as Option A)

4. **Create Web Service**
   - Click "Create Web Service"
   - Wait for deployment

## 🗄️ Step 3: Set Up MongoDB

### Option 1: MongoDB Atlas (Recommended)

1. **Create Account**
   - Go to: https://www.mongodb.com/cloud/atlas
   - Sign up for free account

2. **Create Cluster**
   - Click "Build a Database"
   - Choose "M0 FREE" tier
   - Select your region
   - Click "Create"

3. **Create Database User**
   - Go to "Database Access" → "Add New Database User"
   - Username: `upwork_user` (or your choice)
   - Password: Generate secure password (save it!)
   - Database User Privileges: "Atlas admin"
   - Click "Add User"

4. **Configure Network Access**
   - Go to "Network Access" → "Add IP Address"
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
   - Click "Confirm"

5. **Get Connection String**
   - Go to "Database" → "Connect"
   - Click "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database user password
   - Format: `mongodb+srv://username:password@cluster.mongodb.net`

6. **Add to Render**
   - In Render dashboard → Your service → Environment
   - Add `MONGODB_URI` with the connection string

### Option 2: Render MongoDB (Beta)

1. **Create MongoDB Service**
   - In Render dashboard, click "New +" → "MongoDB"
   - Choose plan (Free tier available)
   - Create service

2. **Get Internal Connection String**
   - Go to MongoDB service → "Info" tab
   - Copy "Internal Connection String"
   - Use this for `MONGODB_URI` in your web service

## ✅ Step 4: Verify Deployment

1. **Check Service URL**
   - Your service will be at: `https://your-service-name.onrender.com`
   - Find it in Render dashboard → Your service → "Settings" → "Service Details"

2. **Test Health Endpoint**
   ```bash
   curl https://your-service-name.onrender.com/health
   ```
   Should return:
   ```json
   {
     "status": "ok",
     "database": "connected"
   }
   ```

3. **Check API Documentation**
   - Visit: `https://your-service-name.onrender.com/docs`
   - You should see Swagger UI with all endpoints

## 🔧 Step 5: Update Integrations

### Update n8n Webhook
- Old URL: `http://localhost:8000/vollna/jobs`
- New URL: `https://your-service-name.onrender.com/vollna/jobs`
- Update in your n8n workflow

### Update Chatbot
- Old URL: `http://localhost:8000`
- New URL: `https://your-service-name.onrender.com`
- Update all API endpoints in your chatbot

## 🚨 Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify `requirements.txt` has all dependencies
- Check Python version in `runtime.txt`

### Service Won't Start
- Check service logs in Render dashboard
- Verify environment variables are set correctly
- Ensure `MONGODB_URI` is correct

### Database Connection Fails
- Verify MongoDB connection string is correct
- Check MongoDB network access allows Render IPs
- Verify database user has correct permissions
- Test connection string locally first

### Health Check Returns Error
- Check MongoDB connection
- Verify all environment variables are set
- Review service logs for errors

## 📊 Free Tier Limitations

- **Sleeps after 15 minutes** of inactivity
- **First request** may take 30-60 seconds to wake up
- **512 MB RAM**
- **0.1 CPU**

To avoid sleeping, upgrade to a paid plan ($7/month for Starter).

## 🎯 Next Steps

1. ✅ Code pushed to GitHub
2. ⏳ Deploy on Render (follow steps above)
3. ⏳ Set up MongoDB Atlas
4. ⏳ Configure environment variables
5. ⏳ Test endpoints
6. ⏳ Update n8n webhook URL
7. ⏳ Update chatbot endpoints

## 📚 Resources

- **Render Dashboard**: https://dashboard.render.com
- **MongoDB Atlas**: https://www.mongodb.com/cloud/atlas
- **Full Deployment Guide**: See `RENDER_DEPLOYMENT.md`
- **API Documentation**: `https://your-service-name.onrender.com/docs` (after deployment)

