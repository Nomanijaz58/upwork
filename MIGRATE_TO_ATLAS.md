# Migrate Data from Local MongoDB to MongoDB Atlas

Complete guide to copy your local MongoDB data to MongoDB Atlas.

## 🎯 Quick Method: Using MongoDB Compass (Easiest)

### Step 1: Export from Local MongoDB

1. **In MongoDB Compass**
   - Connect to `localhost:27017`
   - Select database: `upwork_proposal_bot`
   - For each collection:
     - Click on the collection
     - Click "EXPORT DATA ▼" button
     - Choose "Export Collection"
     - Format: **JSON** (recommended) or CSV
     - Save to a folder (e.g., `~/mongodb_export/`)

2. **Collections to Export:**
   - `audit_logs`
   - `feed_status`
   - `geo_filters`
   - `jobs_filtered`
   - `jobs_raw`
   - `keyword_config`
   - `proposals`
   - Any other collections you have

### Step 2: Import to MongoDB Atlas

1. **In MongoDB Compass**
   - Connect to `cluster0.jnwiaoi.mongodb.net` (your Atlas cluster)
   - Create database: `upwork_proposal_bot` (if not exists)
   - For each exported file:
     - Click on the database
     - Click "ADD DATA ▼" → "Import File"
     - Select the exported JSON file
     - Collection name: (same as original, e.g., `jobs_raw`)
     - Click "Import"

## 🚀 Method 2: Using mongodump/mongorestore (Faster for Large Data)

### Step 1: Export from Local MongoDB

```bash
# Create export directory
mkdir -p ~/mongodb_export

# Export entire database
mongodump --uri="mongodb://localhost:27017" \
  --db=upwork_proposal_bot \
  --out=~/mongodb_export

# Or export specific collections
mongodump --uri="mongodb://localhost:27017" \
  --db=upwork_proposal_bot \
  --collection=jobs_raw \
  --out=~/mongodb_export
```

### Step 2: Import to MongoDB Atlas

```bash
# Get your Atlas connection string
# Format: mongodb+srv://username:password@cluster0.jnwiaoi.mongodb.net

# Import entire database
mongorestore --uri="mongodb+srv://username:password@cluster0.jnwiaoi.mongodb.net" \
  --db=upwork_proposal_bot \
  ~/mongodb_export/upwork_proposal_bot

# Or import specific collection
mongorestore --uri="mongodb+srv://username:password@cluster0.jnwiaoi.mongodb.net" \
  --db=upwork_proposal_bot \
  --collection=jobs_raw \
  ~/mongodb_export/upwork_proposal_bot/jobs_raw.bson
```

## 📋 Step-by-Step: Using MongoDB Compass (Recommended)

### Export Process:

1. **Open MongoDB Compass**
   - Connect to `localhost:27017`

2. **Export Each Collection:**
   - Go to `upwork_proposal_bot` database
   - Click on `jobs_raw` collection
   - Click "EXPORT DATA ▼" → "Export Collection"
   - Format: **JSON**
   - Save as: `jobs_raw.json`
   - Repeat for all collections:
     - `jobs_filtered`
     - `feed_status`
     - `audit_logs`
     - `geo_filters`
     - `keyword_config`
     - `proposals`

### Import Process:

1. **Connect to Atlas in Compass**
   - Connection string: `mongodb+srv://username:password@cluster0.jnwiaoi.mongodb.net`

2. **Create Database (if needed)**
   - Click "Create Database"
   - Database name: `upwork_proposal_bot`
   - Collection name: `jobs_raw` (temporary, we'll import into it)

3. **Import Each Collection:**
   - Click on `upwork_proposal_bot` database
   - Click "ADD DATA ▼" → "Import File"
   - Select `jobs_raw.json`
   - Collection name: `jobs_raw`
   - Click "Import"
   - Repeat for all collections

## 🔧 Alternative: Using mongoimport/mongoexport

### Export from Local:

```bash
# Export jobs_raw collection
mongoexport --uri="mongodb://localhost:27017" \
  --db=upwork_proposal_bot \
  --collection=jobs_raw \
  --out=jobs_raw.json

# Export all collections (repeat for each)
mongoexport --uri="mongodb://localhost:27017" \
  --db=upwork_proposal_bot \
  --collection=jobs_filtered \
  --out=jobs_filtered.json
```

### Import to Atlas:

```bash
# Import jobs_raw collection
mongoimport --uri="mongodb+srv://username:password@cluster0.jnwiaoi.mongodb.net" \
  --db=upwork_proposal_bot \
  --collection=jobs_raw \
  --file=jobs_raw.json

# Import all collections (repeat for each)
mongoimport --uri="mongodb+srv://username:password@cluster0.jnwiaoi.mongodb.net" \
  --db=upwork_proposal_bot \
  --collection=jobs_filtered \
  --file=jobs_filtered.json
```

## ✅ After Migration

1. **Verify Data in Atlas**
   - Check each collection has correct document count
   - Verify indexes are created (they should be auto-created)

2. **Update .env File**
   - Change `MONGODB_URI` to your Atlas connection string
   - Keep `MONGODB_DB=upwork_proposal_bot`

3. **Test Connection**
   - Restart your server
   - Check health endpoint: `http://localhost:8000/health`

## 🚨 Troubleshooting

### Export Fails
- Check MongoDB is running locally
- Verify database name is correct
- Check file permissions for export directory

### Import Fails
- Verify Atlas connection string is correct
- Check network access allows your IP
- Verify database user has write permissions
- Check file format (must be JSON or BSON)

### Data Missing After Import
- Check import logs for errors
- Verify collection names match
- Check if documents were actually exported

## 📊 Collections to Migrate

Based on your setup, migrate these collections:
- ✅ `jobs_raw` - Raw job data
- ✅ `jobs_filtered` - Filtered job data
- ✅ `feed_status` - Feed health tracking
- ✅ `audit_logs` - Audit logs
- ✅ `geo_filters` - Geographic filters
- ✅ `keyword_config` - Keyword configuration
- ✅ `proposals` - Generated proposals

