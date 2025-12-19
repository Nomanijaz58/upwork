#!/usr/bin/env python3
"""
Delete test jobs from vollna_jobs collection.
"""
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Get MongoDB connection details
uri = os.getenv('MONGODB_URI', 'mongodb+srv://n4221891_db_user:noman5858@cluster0.jnwiaoi.mongodb.net/')
db_name = os.getenv('MONGODB_DB', 'upwork_automation')

try:
    # Connect to MongoDB
    print(f"Connecting to MongoDB...")
    client = MongoClient(uri)
    db = client[db_name]
    
    # First, show what will be deleted
    print("\n🔍 Searching for test jobs...")
    # Find jobs with "Test Job" in title OR "/~test" in URL
    test_jobs = list(db.vollna_jobs.find({
        "$or": [
            {"title": {"$regex": "Test Job|test", "$options": "i"}},
            {"url": {"$regex": "/~test", "$options": "i"}}
        ]
    }))
    
    print(f"\nFound {len(test_jobs)} test jobs to delete:")
    for i, job in enumerate(test_jobs[:10], 1):  # Show first 10
        title = job.get("title", "No title")
        job_id = str(job.get("_id", "N/A"))
        print(f"  {i}. {title[:60]}... (ID: {job_id[:24]}...)")
    
    if len(test_jobs) > 10:
        print(f"  ... and {len(test_jobs) - 10} more")
    
    if len(test_jobs) == 0:
        print("\n✅ No test jobs found. Nothing to delete.")
        sys.exit(0)
    
    # Delete them
    print(f"\n🗑️  Deleting {len(test_jobs)} test jobs...")
    result = db.vollna_jobs.delete_many({
        "$or": [
            {"title": {"$regex": "Test Job|test", "$options": "i"}},
            {"url": {"$regex": "/~test", "$options": "i"}}
        ]
    })
    
    print(f"\n✅ Successfully deleted {result.deleted_count} test jobs")
    
    # Verify deletion
    remaining = db.vollna_jobs.count_documents({
        "$or": [
            {"title": {"$regex": "Test Job|test", "$options": "i"}},
            {"url": {"$regex": "/~test", "$options": "i"}}
        ]
    })
    if remaining == 0:
        print("✅ Verification: No test jobs remaining")
    else:
        print(f"⚠️  Warning: {remaining} test jobs still found")
    
    # Show total jobs remaining
    total = db.vollna_jobs.count_documents({})
    print(f"\n📊 Total jobs in vollna_jobs collection: {total}")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)

