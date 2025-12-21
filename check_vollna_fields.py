#!/usr/bin/env python3
"""
Check what fields Vollna is actually sending in the payload by inspecting stored jobs.
This script queries the database to see what data we have.
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Try loading .env from multiple locations
load_dotenv()
load_dotenv(dotenv_path="backend/.env")
load_dotenv(dotenv_path=".env")

async def check_vollna_fields():
    """Check what fields are available in stored Vollna jobs."""
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_db = os.getenv("MONGODB_DB")
    
    if not mongodb_uri or not mongodb_db:
        print("❌ MONGODB_URI or MONGODB_DB not set in .env")
        return
    
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[mongodb_db]
    collection = db.vollna_jobs
    
    # Get a few sample jobs
    jobs = await collection.find({}).limit(5).to_list(length=5)
    
    print(f"\n📊 Found {len(jobs)} sample jobs in database\n")
    print("=" * 80)
    
    for idx, job in enumerate(jobs, 1):
        print(f"\n🔹 Job {idx}: {job.get('title', 'N/A')[:60]}")
        print("-" * 80)
        
        # Check client_name
        client_name = job.get("client_name", "NOT PRESENT")
        client_obj = job.get("client", {})
        print(f"  client_name field: {repr(client_name)}")
        print(f"  client object: {client_obj}")
        if isinstance(client_obj, dict) and client_obj:
            print(f"    - client.name: {client_obj.get('name', 'NOT PRESENT')}")
            print(f"    - client.rating: {client_obj.get('rating', 'NOT PRESENT')}")
        
        # Check proposals
        proposals = job.get("proposals")
        proposal_count = job.get("proposal_count")
        num_proposals = job.get("num_proposals")
        print(f"  proposals field: {proposals}")
        print(f"  proposal_count field: {proposal_count}")
        print(f"  num_proposals field: {num_proposals}")
        
        # Check raw payload
        raw = job.get("raw", {})
        if raw:
            print(f"  Raw payload keys: {list(raw.keys())[:15]}")
            if "client" in raw:
                print(f"    Raw client: {raw.get('client')}")
            if "client_details" in raw:
                client_details = raw.get("client_details")
                print(f"    Raw client_details: {client_details}")
                if isinstance(client_details, dict):
                    print(f"      - client_details keys: {list(client_details.keys())}")
                    print(f"      - client_details.name: {client_details.get('name')}")
                    print(f"      - client_details.rating: {client_details.get('rating')}")
            if "proposals" in raw:
                print(f"    Raw proposals: {raw.get('proposals')}")
            if "proposal_count" in raw:
                print(f"    Raw proposal_count: {raw.get('proposal_count')}")
        
        print()
    
    # Check overall statistics
    total_jobs = await collection.count_documents({})
    jobs_with_client = await collection.count_documents({"client_name": {"$exists": True, "$ne": ""}})
    jobs_with_proposals = await collection.count_documents({"proposals": {"$exists": True, "$ne": None}})
    
    print("=" * 80)
    print(f"\n📈 Statistics:")
    print(f"  Total jobs: {total_jobs}")
    print(f"  Jobs with client_name: {jobs_with_client} ({jobs_with_client/total_jobs*100:.1f}%)" if total_jobs > 0 else "  Jobs with client_name: 0")
    print(f"  Jobs with proposals: {jobs_with_proposals} ({jobs_with_proposals/total_jobs*100:.1f}%)" if total_jobs > 0 else "  Jobs with proposals: 0")
    print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_vollna_fields())

