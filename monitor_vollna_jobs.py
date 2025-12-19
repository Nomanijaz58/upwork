#!/usr/bin/env python3
"""
Monitor Vollna Jobs - Watch for new jobs and display them in real-time
"""
import time
import json
import requests
from datetime import datetime
from typing import List, Dict, Any

API_URL = "https://upwork-xxsc.onrender.com"
# For local: API_URL = "http://localhost:8000"

def get_all_jobs() -> Dict[str, Any]:
    """Get all jobs from Vollna."""
    try:
        response = requests.get(f"{API_URL}/jobs/all", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching jobs: {e}")
        return {"count": 0, "jobs": []}

def display_job(job: Dict[str, Any], index: int):
    """Display a single job."""
    job_id = job.get("_id", job.get("id", "N/A"))
    title = job.get("title", "No title")
    budget = job.get("budget", 0)
    client = job.get("client_name", "Unknown")
    created = job.get("created_at", job.get("received_at", "N/A"))
    
    print(f"\n{'='*80}")
    print(f"Job #{index}")
    print(f"{'='*80}")
    print(f"📋 Title:     {title}")
    print(f"🆔 ID:        {job_id}")
    print(f"💰 Budget:    ${budget}/hr")
    print(f"👤 Client:    {client}")
    print(f"📅 Created:   {created}")
    print(f"🔗 URL:       {job.get('url', 'N/A')}")
    
    skills = job.get("skills", [])
    if skills:
        print(f"🛠️  Skills:    {', '.join(skills)}")
    
    proposals = job.get("proposals")
    if proposals is not None:
        print(f"📊 Proposals:  {proposals}")
    
    print(f"{'='*80}")

def monitor_jobs(interval: int = 10, watch_mode: bool = True):
    """Monitor jobs and display new ones."""
    print("🔍 Vollna Jobs Monitor")
    print("=" * 80)
    print(f"API URL: {API_URL}")
    print(f"Refresh interval: {interval} seconds")
    print(f"Watch mode: {'ON (shows only new jobs)' if watch_mode else 'OFF (shows all jobs)'}")
    print("=" * 80)
    print("\nPress Ctrl+C to stop\n")
    
    seen_job_ids = set()
    last_count = 0
    
    try:
        while True:
            data = get_all_jobs()
            count = data.get("count", 0)
            jobs = data.get("jobs", [])
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if count != last_count:
                print(f"\n⏰ [{current_time}] Job count changed: {last_count} → {count}")
                last_count = count
            
            if watch_mode:
                # Show only new jobs
                new_jobs = [j for j in jobs if j.get("_id") not in seen_job_ids]
                if new_jobs:
                    print(f"\n🆕 Found {len(new_jobs)} new job(s)!")
                    for idx, job in enumerate(new_jobs, 1):
                        job_id = job.get("_id", job.get("id"))
                        if job_id:
                            seen_job_ids.add(job_id)
                        display_job(job, idx)
            else:
                # Show all jobs
                if jobs:
                    print(f"\n📋 [{current_time}] Total jobs: {count}")
                    for idx, job in enumerate(jobs[:10], 1):  # Show first 10
                        display_job(job, idx)
                    if count > 10:
                        print(f"\n... and {count - 10} more jobs")
            
            if not watch_mode or not jobs:
                print(f"⏳ Waiting {interval}s... (Jobs: {count})", end="\r")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")
        print(f"Total jobs seen: {len(seen_job_ids)}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    interval = 10
    watch_mode = True
    
    if len(sys.argv) > 1:
        interval = int(sys.argv[1])
    if len(sys.argv) > 2:
        watch_mode = sys.argv[2].lower() != "all"
    
    monitor_jobs(interval=interval, watch_mode=watch_mode)

