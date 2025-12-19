#!/usr/bin/env python3
"""
Analyze jobs to identify test vs real jobs
"""
import sys
import json
import urllib.request
import urllib.error

API_URL = "https://upwork-xxsc.onrender.com"

def analyze_jobs():
    """Analyze jobs and identify test vs real."""
    try:
        with urllib.request.urlopen(f"{API_URL}/jobs/all", timeout=10) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    jobs = data.get("jobs", [])
    count = len(jobs)
    
    print("📊 Current Jobs Analysis")
    print("=" * 60)
    print(f"Total jobs: {count}\n")
    
    if count == 0:
        print("No jobs found. Waiting for Vollna to send jobs...")
        return
    
    test_jobs = []
    real_jobs = []
    
    for job in jobs:
        title = job.get("title", "").lower()
        url = job.get("url", "")
        client = job.get("client_name", "").lower()
        
        # Check if it's a test job
        is_test = (
            "test" in title or
            "test" in client or
            "/~test" in url or
            "monitor" in title or
            "script" in title
        )
        
        if is_test:
            test_jobs.append(job)
        else:
            real_jobs.append(job)
    
    print(f"📈 Summary:")
    print(f"   ✅ Real jobs: {len(real_jobs)}")
    print(f"   ❌ Test jobs: {len(test_jobs)}\n")
    
    if test_jobs:
        print("⚠️  TEST JOBS FOUND (created by test scripts):")
        print("-" * 60)
        for job in test_jobs:
            print(f"   Title: {job.get('title')}")
            print(f"   URL: {job.get('url')}")
            print(f"   Client: {job.get('client_name')}")
            print(f"   ID: {job.get('_id')}")
            print()
        print("💡 These are fake jobs. Stop running test scripts!")
        print()
    
    if real_jobs:
        print("✅ REAL JOBS FOUND (from Vollna/Upwork):")
        print("-" * 60)
        for job in real_jobs:
            print(f"   Title: {job.get('title')}")
            print(f"   URL: {job.get('url')}")
            print(f"   Client: {job.get('client_name')}")
            print(f"   Budget: ${job.get('budget')}/hr")
            print(f"   ID: {job.get('_id')}")
            print()
        print("✅ These are real Upwork jobs from Vollna!")
    else:
        print("❌ NO REAL JOBS FOUND")
        print()
        print("This means:")
        print("   - Vollna is not sending jobs yet, OR")
        print("   - Only test jobs are in the database")
        print()
        print("Next steps:")
        print("   1. Verify Vollna webhook is configured")
        print("   2. Check Vollna extension is monitoring Upwork")
        print("   3. Check Render logs for webhook activity")
        print("   4. Wait for real jobs to arrive")

if __name__ == "__main__":
    analyze_jobs()

