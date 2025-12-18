# MongoDB Atlas Setup Guide

Complete guide to set up MongoDB Atlas (free tier) for your Upwork Proposal Bot.

## 🚀 Step 1: Create MongoDB Atlas Account

1. **Go to MongoDB Atlas**
   - Visit: https://www.mongodb.com/cloud/atlas
   - Click "Try Free" or "Sign Up"

2. **Sign Up**
   - Use your email or Google/GitHub account
   - Fill in your details
   - Verify your email if required

## 🗄️ Step 2: Create Free Cluster

1. **After Login**
   - You'll see "Deploy a cloud database" screen
   - Click "Build a Database"

2. **Choose Plan**
   - Select **"M0 FREE"** (Free tier)
   - Click "Create"

3. **Choose Cloud Provider & Region**
   - **Cloud Provider**: AWS (recommended) or Google Cloud
   - **Region**: Choose closest to you (or Virginia if deploying on Render)
   - For Render deployment: Choose **"US East (N. Virginia)"**
   - Click "Create Cluster"

4. **Wait for Cluster**
   - Takes 3-5 minutes to create
   - You'll see "Your cluster is being created"

## 👤 Step 3: Create Database User

1. **Go to Database Access**
   - Click "Database Access" in left sidebar
   - Click "Add New Database User"

2. **Authentication Method**
   - Select "Password"
   - Click "Autogenerate Secure Password" (or create your own)
   - **IMPORTANT**: Copy and save the password! You'll need it.

3. **Database User Privileges**
   - Select "Atlas admin" (or "Read and write to any database")
   - Username: `upwork_user` (or your choice)

4. **Create User**
   - Click "Add User"
   - Save the username and password securely

## 🌐 Step 4: Configure Network Access

1. **Go to Network Access**
   - Click "Network Access" in left sidebar
   - Click "Add IP Address"

2. **Allow Access**
   - Click "Allow Access from Anywhere"
   - This adds `0.0.0.0/0` (allows all IPs)
   - **For Production**: You can restrict to specific IPs later
   - Click "Confirm"

3. **Wait for Update**
   - Takes a few seconds to apply

## 🔗 Step 5: Get Connection String

1. **Go to Database**
   - Click "Database" in left sidebar
   - Click "Connect" button on your cluster

2. **Choose Connection Method**
   - Click "Connect your application"

3. **Copy Connection String**
   - Driver: **Python** (or Node.js)
   - Version: **3.6 or later**
   - Copy the connection string
   - It looks like: `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`

4. **Replace Placeholders**
   - Replace `<username>` with your database username (e.g., `upwork_user`)
   - Replace `<password>` with your database password
   - **IMPORTANT**: URL-encode special characters in password (e.g., `@` becomes `%40`)

5. **Final Connection String Format**
   ```
   mongodb+srv://upwork_user:your-password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

## ⚙️ Step 6: Update Your .env File

1. **Open `.env` file**
   - Located in `backend/.env`

2. **Update MongoDB Settings**
   ```bash
   MONGODB_URI=mongodb+srv://upwork_user:your-password@cluster0.xxxxx.mongodb.net
   MONGODB_DB=upwork_proposal_bot
   ```

3. **Important Notes**
   - **Don't include database name in URI** (our code handles it separately)
   - Remove `?retryWrites=true&w=majority` from URI (or keep it, both work)
   - Make sure password is URL-encoded if it has special characters

## 🧪 Step 7: Test Connection

1. **Test Locally**
   ```bash
   cd backend
   python3 -c "from app.db.mongo import connect_mongo; import asyncio; asyncio.run(connect_mongo()); print('✅ Connected to MongoDB Atlas!')"
   ```

2. **Or Start Server**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   - Check logs for "MongoDB connected successfully"
   - Visit: http://localhost:8000/health
   - Should return: `{"status": "ok", "database": "connected"}`

## 🔒 Step 8: Add to Render (For Deployment)

1. **In Render Dashboard**
   - Go to your web service
   - Click "Environment" tab
   - Add environment variable:

   **Name**: `MONGODB_URI`
   **Value**: Your connection string (same as in .env)
   - Mark as "Secret" ✅

2. **Add Database Name**
   **Name**: `MONGODB_DB`
   **Value**: `upwork_proposal_bot`

## 🚨 Troubleshooting

### Connection Timeout
- **Problem**: Can't connect to MongoDB
- **Solution**: 
  - Check Network Access allows your IP (or 0.0.0.0/0)
  - Verify username/password are correct
  - Check connection string format

### Authentication Failed
- **Problem**: "Authentication failed" error
- **Solution**:
  - Verify username and password
  - URL-encode special characters in password
  - Check database user has correct privileges

### Database Not Found
- **Problem**: Database doesn't exist
- **Solution**: 
  - MongoDB Atlas creates databases automatically
  - Just use the connection string, database will be created on first write

### Password with Special Characters
- **Problem**: Password contains `@`, `#`, `%`, etc.
- **Solution**: URL-encode the password:
  - `@` → `%40`
  - `#` → `%23`
  - `%` → `%25`
  - `&` → `%26`
  - Use online URL encoder: https://www.urlencoder.org/

## 📋 Quick Checklist

- [ ] MongoDB Atlas account created
- [ ] Free M0 cluster created
- [ ] Database user created (username + password saved)
- [ ] Network access configured (0.0.0.0/0)
- [ ] Connection string obtained
- [ ] `.env` file updated with `MONGODB_URI` and `MONGODB_DB`
- [ ] Connection tested locally
- [ ] Render environment variables set (for deployment)

## 🎯 Next Steps

1. ✅ MongoDB Atlas set up
2. ⏳ Test connection locally
3. ⏳ Deploy to Render with MongoDB Atlas connection string
4. ⏳ Verify deployment works

## 💡 Tips

- **Free Tier Limits**: 512 MB storage, shared CPU
- **Backup**: Free tier includes automated backups
- **Monitoring**: Free tier includes basic monitoring
- **Upgrade**: Can upgrade anytime if you need more resources

