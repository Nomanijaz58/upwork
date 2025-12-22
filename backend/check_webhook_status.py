"""
Diagnostic script to check webhook status and recent job activity.
"""
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.settings import settings

async def check_webhook_status():
    """Check webhook activity and recent jobs"""
    
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB]
    collection = db['vollna_jobs']
    
    print("=" * 60)
    print("WEBHOOK STATUS DIAGNOSTIC")
    print("=" * 60)
    
    # Total jobs
    total = await collection.count_documents({})
    print(f"\n📊 Total jobs in database: {total}")
    
    # Most recent jobs
    recent = await collection.find({}).sort([('received_at', -1)]).limit(10).to_list(length=10)
    print(f"\n🕐 Most recent 10 jobs received:")
    for i, job in enumerate(recent, 1):
        received = job.get('received_at', 'N/A')
        posted = job.get('posted_at', 'N/A')
        title = job.get('title', 'N/A')[:50]
        print(f"  {i}. {title}...")
        print(f"     Received: {received}")
        print(f"     Posted: {posted}")
    
    # Time analysis
    now = datetime.utcnow()
    time_ranges = [
        (1, "last hour"),
        (6, "last 6 hours"),
        (24, "last 24 hours"),
        (48, "last 48 hours"),
        (168, "last week"),
    ]
    
    print(f"\n⏰ Jobs received by time period:")
    for hours, label in time_ranges:
        cutoff = now - timedelta(hours=hours)
        count = await collection.count_documents({'received_at': {'$gte': cutoff}})
        print(f"  {label:20s}: {count:4d} jobs")
    
    # Check if webhook is receiving data
    if recent:
        latest_received = recent[0].get('received_at')
        if isinstance(latest_received, str):
            try:
                latest_dt = datetime.fromisoformat(latest_received.replace('Z', '+00:00'))
            except:
                latest_dt = None
        elif isinstance(latest_received, datetime):
            latest_dt = latest_received
        else:
            latest_dt = None
        
        if latest_dt:
            hours_ago = (now - latest_dt.replace(tzinfo=None)).total_seconds() / 3600
            print(f"\n⚠️  Last job received: {hours_ago:.1f} hours ago")
            
            if hours_ago > 24:
                print(f"\n❌ WARNING: No new jobs received in over 24 hours!")
                print(f"   This suggests Vollna is not sending webhooks.")
                print(f"\n   Check:")
                print(f"   1. Vollna webhook URL: https://upwork-xxsc.onrender.com/webhook/vollna")
                print(f"   2. Vollna authentication: Bearer token or X-N8N-Secret header")
                print(f"   3. Vollna filter is active and matching jobs")
                print(f"   4. Vollna webhook settings are enabled")
            elif hours_ago > 6:
                print(f"\n⚠️  WARNING: No new jobs received in over 6 hours.")
                print(f"   This might be normal if there are no new matching jobs.")
            else:
                print(f"\n✅ Webhook appears to be active (jobs received recently)")
    
    # Check for duplicate URLs (might indicate webhook is working but sending duplicates)
    pipeline = [
        {"$group": {"_id": "$url", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    duplicates = await collection.aggregate(pipeline).to_list(length=5)
    if duplicates:
        print(f"\n📋 Top duplicate URLs (might indicate webhook is working):")
        for dup in duplicates:
            print(f"  {dup['_id'][:60]}... ({dup['count']} times)")
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_webhook_status())

