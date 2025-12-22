"""
Script to update existing jobs in the database with posted_at from raw.published field.
This fixes jobs that were created before the time extraction logic was improved.
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.settings import settings

async def update_job_times():
    """Update posted_at field for jobs that have published time in raw.published"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB]
    collection = db["vollna_jobs"]
    
    print(f"Connecting to MongoDB: {settings.MONGODB_URI}")
    print(f"Database: {settings.MONGODB_DB}")
    print(f"Collection: vollna_jobs")
    
    # Find all jobs with null posted_at but have raw.published
    query = {
        "$or": [
            {"posted_at": None},
            {"posted_at": {"$exists": False}}
        ],
        "raw.published": {"$exists": True, "$ne": None}
    }
    
    # Count jobs to update
    count = await collection.count_documents(query)
    print(f"\nFound {count} jobs to update")
    
    if count == 0:
        print("No jobs need updating. Exiting.")
        client.close()
        return
    
    # Process jobs in batches
    updated = 0
    failed = 0
    batch_size = 100
    
    async for job in collection.find(query).batch_size(batch_size):
        try:
            job_id = job.get("_id")
            raw_data = job.get("raw", {})
            published = raw_data.get("published")
            
            if not published:
                continue
            
            # Parse the published time
            posted_at = None
            if isinstance(published, str):
                try:
                    # Try ISO format first
                    posted_at = datetime.fromisoformat(published.replace('Z', '+00:00'))
                except Exception:
                    try:
                        # Try RFC format
                        from email.utils import parsedate_to_datetime
                        posted_at = parsedate_to_datetime(published)
                    except Exception:
                        print(f"Failed to parse published time for job {job_id}: {published}")
                        failed += 1
                        continue
            elif isinstance(published, datetime):
                posted_at = published
            elif isinstance(published, (int, float)):
                # Unix timestamp
                if published > 1e12:  # milliseconds
                    posted_at = datetime.fromtimestamp(published / 1000)
                else:  # seconds
                    posted_at = datetime.fromtimestamp(published)
            
            if posted_at:
                # Update the job
                await collection.update_one(
                    {"_id": job_id},
                    {"$set": {"posted_at": posted_at.isoformat()}}
                )
                updated += 1
                
                if updated % 100 == 0:
                    print(f"Updated {updated} jobs...")
            else:
                failed += 1
                
        except Exception as e:
            print(f"Error updating job {job.get('_id')}: {e}")
            failed += 1
            continue
    
    print(f"\n✅ Update complete!")
    print(f"   Updated: {updated} jobs")
    print(f"   Failed: {failed} jobs")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_job_times())

