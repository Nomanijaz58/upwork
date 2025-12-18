#!/usr/bin/env python3
"""
Script to verify database insertion from Vollna webhook.
Checks that jobs are properly inserted into both jobs_raw and jobs_filtered collections.
"""
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def verify_insertion(mongodb_uri: str, db_name: str):
    """Verify jobs are in both collections."""
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]
    
    print("🔍 Verifying Database Insertion")
    print("=" * 50)
    
    # Check jobs_raw
    raw_count = await db.jobs_raw.count_documents({"source": "vollna"})
    print(f"\n📊 jobs_raw collection:")
    print(f"   Total jobs from vollna: {raw_count}")
    
    if raw_count > 0:
        latest_raw = await db.jobs_raw.find_one(
            {"source": "vollna"},
            sort=[("created_at", -1)]
        )
        if latest_raw:
            print(f"   Latest job: {latest_raw.get('title', 'N/A')[:50]}")
            print(f"   URL: {latest_raw.get('url', 'N/A')}")
            print(f"   Created: {latest_raw.get('created_at', 'N/A')}")
            print(f"   Budget: {latest_raw.get('budget', 'N/A')}")
            print(f"   Proposals: {latest_raw.get('proposals', 'N/A')}")
    
    # Check jobs_filtered
    filtered_count = await db.jobs_filtered.count_documents({"source": "vollna"})
    print(f"\n📊 jobs_filtered collection:")
    print(f"   Total jobs from vollna: {filtered_count}")
    
    if filtered_count > 0:
        latest_filtered = await db.jobs_filtered.find_one(
            {"source": "vollna"},
            sort=[("created_at", -1)]
        )
        if latest_filtered:
            print(f"   Latest job: {latest_filtered.get('title', 'N/A')[:50]}")
            print(f"   URL: {latest_filtered.get('url', 'N/A')}")
            print(f"   Created: {latest_filtered.get('created_at', 'N/A')}")
            print(f"   Budget: {latest_filtered.get('budget', 'N/A')}")
            print(f"   Proposals: {latest_filtered.get('proposals', 'N/A')}")
    
    # Check feed status
    feed_status = await db.feed_status.find_one({"source": "vollna"})
    print(f"\n📊 Feed Status:")
    if feed_status:
        print(f"   Last fetch: {feed_status.get('last_fetch_at', 'N/A')}")
        print(f"   Last successful: {feed_status.get('last_successful_fetch_at', 'N/A')}")
        print(f"   Error count: {feed_status.get('error_count', 0)}")
        print(f"   Last error: {feed_status.get('last_error', 'None')}")
    else:
        print("   No feed status found")
    
    # Summary
    print(f"\n✅ Summary:")
    print(f"   Jobs in jobs_raw: {raw_count}")
    print(f"   Jobs in jobs_filtered: {filtered_count}")
    
    if raw_count > 0 and filtered_count == 0:
        print("   ⚠️  WARNING: Jobs in raw but not in filtered!")
        print("   This means jobs are failing keyword/geo filters.")
    elif raw_count == 0:
        print("   ⚠️  WARNING: No jobs found in jobs_raw!")
        print("   Webhook may not have received any jobs yet.")
    else:
        print("   ✅ Jobs are being inserted correctly!")
    
    client.close()

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv("backend/.env")
    
    mongodb_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB", "upwork_proposal_bot")
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in environment")
        sys.exit(1)
    
    asyncio.run(verify_insertion(mongodb_uri, db_name))

