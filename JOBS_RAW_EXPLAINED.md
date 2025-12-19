# What is `jobs_raw`?

## 📚 Definition

`jobs_raw` is a **MongoDB collection** that stores **ALL jobs that are successfully ingested** into the system, regardless of whether they pass keyword or geo filters.

## 🎯 Purpose

`jobs_raw` serves as the **master repository** for all job data:
- ✅ **Complete History**: Every job that comes through ingestion
- ✅ **No Filtering**: Jobs are stored here BEFORE keyword/geo filtering
- ✅ **Deduplication**: Uses unique `url` index to prevent duplicates
- ✅ **Source Tracking**: Tracks where each job came from (vollna, best_match, etc.)

## 🔄 Two-Collection System

The system uses **two collections** to separate raw data from filtered data:

### 1. `jobs_raw` Collection
- **Contains**: ALL ingested jobs
- **Purpose**: Complete job history, no filtering applied
- **When jobs are added**: Immediately upon ingestion (if valid)
- **Filtering**: None - all valid jobs are stored here

### 2. `jobs_filtered` Collection  
- **Contains**: Only jobs that passed BOTH filters
- **Purpose**: Pre-filtered jobs ready for display/recommendations
- **When jobs are added**: Only if they pass keyword AND geo filters
- **Filtering**: Keyword match + Geo match required

## 📊 Ingestion Flow

When a job is ingested via `/ingest/upwork` or `/webhook/vollna`:

```
1. Job Received
   ↓
2. Validate (title, description, URL required)
   ↓
3. ✅ Store in jobs_raw (ALL valid jobs)
   ↓
4. Check Keyword Filter
   ↓
5. Check Geo Filter
   ↓
6. ✅ Store in jobs_filtered (ONLY if both filters pass)
```

## 📋 Collection Structure

### `jobs_raw` Document Example:
```json
{
  "_id": ObjectId("..."),
  "title": "Python Developer",
  "description": "Build API with FastAPI",
  "url": "https://www.upwork.com/jobs/~123",
  "source": "vollna",
  "region": "United States",
  "posted_at": "2025-12-18T23:18:17",
  "skills": ["Python", "FastAPI", "MongoDB"],
  "budget": 75.0,
  "proposals": 8,
  "client": {},
  "raw": {...},  // Original payload
  "created_at": "2025-12-18T23:18:18",
  "updated_at": "2025-12-18T23:18:18",
  "last_seen_at": "2025-12-18T23:18:18"
}
```

## 🔍 Indexes on `jobs_raw`

For efficient querying, `jobs_raw` has these indexes:

1. **`url`** (unique) - Prevents duplicate jobs
2. **`posted_at`** (descending) - Sort by newest first
3. **`source`** (ascending) - Filter by source (vollna, best_match, etc.)
4. **`created_at`** (descending) - Sort by ingestion time
5. **`last_seen_at`** (descending) - Track when job was last seen
6. **`budget`** (descending) - Filter/sort by budget
7. **`proposals`** (ascending) - Filter by proposal count

## 🎯 When to Use `jobs_raw`

### Use `jobs_raw` when you want:
- ✅ **All jobs** from a source (no filtering)
- ✅ **Complete history** of ingested jobs
- ✅ **Raw data** before any filtering
- ✅ **Feed monitoring** (total jobs received)

### Example Endpoints:
- `GET /api/jobs?source=vollna` → Queries `jobs_raw`
- `GET /jobs/latest?source=vollna` → Queries `jobs_raw`
- `GET /feeds/status` → Counts jobs in `jobs_raw`

## 🎯 When to Use `jobs_filtered`

### Use `jobs_filtered` when you want:
- ✅ **Only relevant jobs** (passed keyword/geo filters)
- ✅ **Pre-filtered results** for recommendations
- ✅ **Quality jobs** that match your criteria

### Example Endpoints:
- `GET /jobs?use_filtered=true` → Queries `jobs_filtered`
- `POST /jobs/search` → Queries `jobs_filtered` for filtered results
- `POST /jobs/recommend` → Uses `jobs_filtered` for AI recommendations

## 📊 Current Status

**Your `jobs_raw` collection:**
- Contains: **3 jobs** with `source=vollna`
- All 3 jobs are test jobs from Vollna webhook
- All jobs have valid data (title, description, URL, skills, budget)

**Your `jobs_filtered` collection:**
- May contain fewer jobs (only those that passed keyword + geo filters)
- Check with: `GET /jobs?use_filtered=true&source=vollna`

## 🔍 Key Differences

| Feature | `jobs_raw` | `jobs_filtered` |
|---------|------------|----------------|
| **Contains** | ALL ingested jobs | Only filtered jobs |
| **Filtering** | None | Keyword + Geo |
| **Purpose** | Complete history | Quality jobs |
| **Size** | Larger (all jobs) | Smaller (filtered) |
| **Use Case** | Monitoring, all jobs | Recommendations, display |

## 🎯 Summary

**`jobs_raw`** = The complete, unfiltered database of all jobs that have been ingested into the system. It's your "source of truth" for all job data, regardless of whether jobs match your keyword or geo criteria.

---

**Think of it like this:**
- `jobs_raw` = Your entire inbox (all emails)
- `jobs_filtered` = Your filtered inbox (only important emails)

Both are useful, but for different purposes! 🚀

