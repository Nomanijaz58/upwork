# Quick Migration: Local MongoDB to Atlas

## 🎯 Easiest Method: Run This Command

Replace `YOUR_ATLAS_URI` with your MongoDB Atlas connection string:

```bash
# Step 1: Export from local
mongodump --uri="mongodb://localhost:27017" \
  --db=upwork_proposal_bot \
  --out=~/mongodb_export

# Step 2: Import to Atlas
mongorestore --uri="YOUR_ATLAS_URI" \
  --db=upwork_proposal_bot \
  --drop \
  ~/mongodb_export/upwork_proposal_bot
```

## 📋 Your Atlas Connection String

Get it from MongoDB Atlas:
1. Go to "Database" → "Connect"
2. Choose "Connect your application"
3. Copy the connection string
4. Replace `<username>` and `<password>` with your credentials

**Format:**
```
mongodb+srv://upwork_user:your-password@cluster0.jnwiaoi.mongodb.net
```

## ✅ After Migration

1. **Update .env file:**
   ```bash
   MONGODB_URI=mongodb+srv://upwork_user:your-password@cluster0.jnwiaoi.mongodb.net
   MONGODB_DB=upwork_proposal_bot
   ```

2. **Test connection:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

3. **Verify:**
   - Visit: http://localhost:8000/health
   - Should return: `{"status": "ok", "database": "connected"}`

## 🚨 If Command Fails

Use MongoDB Compass method (see MIGRATE_TO_ATLAS.md)

