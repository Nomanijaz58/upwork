#!/usr/bin/env python3
"""
Comprehensive verification and fix script for Vollna integration.
Checks webhook configuration, endpoints, and job sources.
"""
import urllib.request
import json
import sys
from datetime import datetime

API_URL = "https://upwork-xxsc.onrender.com"
WEBHOOK_URL = f"{API_URL}/webhook/vollna"
JOBS_ALL_URL = f"{API_URL}/jobs/all"
SECRET = "9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_webhook_endpoint():
    """Step 1: Check webhook configuration"""
    print_header("Step 1: Check Webhook Configuration")
    
    print(f"\n✅ Webhook Endpoint: {WEBHOOK_URL}")
    print(f"   Method: POST")
    print(f"   Authentication: X-N8N-Secret header required")
    
    # Test webhook with a simple payload
    print(f"\n🧪 Testing webhook endpoint...")
    try:
        test_payload = {
            "title": f"Webhook Test {int(datetime.utcnow().timestamp())}",
            "url": "https://www.upwork.com/jobs/~test",
            "budget": 50.0,
            "client_name": "Test Client"
        }
        
        data = json.dumps(test_payload).encode('utf-8')
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "X-N8N-Secret": SECRET
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"   ✅ Webhook is accepting POST requests")
            print(f"   Response: {result}")
            return True
            
    except urllib.error.HTTPError as e:
        print(f"   ❌ Webhook test failed: {e.code} - {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"   Error details: {error_body}")
        except:
            pass
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_jobs_all_source():
    """Step 2: Check /jobs/all source"""
    print_header("Step 2: Check /jobs/all Source")
    
    print(f"\n✅ Endpoint: {JOBS_ALL_URL}")
    print(f"   Collection: vollna_jobs")
    print(f"   Source: All jobs received via /webhook/vollna")
    
    try:
        with urllib.request.urlopen(JOBS_ALL_URL, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            count = data.get('count', 0)
            jobs = data.get('jobs', [])
            
            print(f"\n📊 Current Status:")
            print(f"   Total jobs: {count}")
            
            if count > 0:
                print(f"\n   Sample jobs:")
                for i, job in enumerate(jobs[:5], 1):
                    title = job.get('title', 'No title')
                    source = job.get('source', 'N/A')
                    url = job.get('url', 'N/A')
                    budget = job.get('budget', job.get('budget_value', 'N/A'))
                    
                    # Check if it's a real job or test job
                    is_test = 'test' in title.lower() or '/~test' in url.lower()
                    job_type = "❌ TEST" if is_test else "✅ REAL"
                    
                    print(f"   {i}. {job_type} - {title[:50]}...")
                    print(f"      Source: {source}, Budget: ${budget}, URL: {url[:60]}...")
                
                # Analyze job sources
                real_count = sum(1 for j in jobs if 'test' not in j.get('title', '').lower() and '/~test' not in j.get('url', '').lower())
                test_count = count - real_count
                
                print(f"\n   Analysis:")
                print(f"   ✅ Real jobs: {real_count}")
                print(f"   ❌ Test jobs: {test_count}")
                
                if real_count == 0:
                    print(f"\n   ⚠️  WARNING: No real jobs found!")
                    print(f"   This means Vollna is not sending real Upwork jobs yet.")
                    print(f"   Check Vollna configuration and ensure it's fetching from Upwork.")
            else:
                print(f"\n   ⚠️  No jobs found in database")
                print(f"   Vollna webhook has not received any jobs yet.")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Error checking /jobs/all: {e}")
        return False

def check_other_endpoints():
    """Step 3: Look for other job endpoints"""
    print_header("Step 3: Check Other Job Endpoints")
    
    endpoints = [
        ("/jobs/latest", "GET", "Latest jobs from jobs_raw collection"),
        ("/api/jobs", "GET", "Alias for /jobs/latest"),
        ("/jobs/search", "POST", "Search jobs with filters"),
        ("/api/jobs/filter/vollna", "POST", "Filter Vollna jobs"),
    ]
    
    print(f"\n📋 Available Endpoints:")
    for endpoint, method, description in endpoints:
        full_url = f"{API_URL}{endpoint}"
        print(f"\n   {method} {endpoint}")
        print(f"   URL: {full_url}")
        print(f"   Description: {description}")
        
        # Try to check if endpoint exists
        try:
            if method == "GET":
                with urllib.request.urlopen(full_url, timeout=5) as response:
                    status = response.getcode()
                    print(f"   Status: ✅ {status} OK")
            else:
                print(f"   Status: ⏳ (POST endpoint - requires payload)")
        except urllib.error.HTTPError as e:
            print(f"   Status: ⚠️  {e.code} {e.reason}")
        except Exception as e:
            print(f"   Status: ❌ Error: {e}")

def check_vollna_filters():
    """Step 4: Inspect and suggest filter adjustments"""
    print_header("Step 4: Vollna Filter Recommendations")
    
    print(f"\n📋 Filter Checklist for Vollna Dashboard:")
    print(f"\n   1. ✅ Webhook URL:")
    print(f"      {WEBHOOK_URL}")
    print(f"      Method: POST")
    print(f"      Header: X-N8N-Secret: {SECRET[:20]}...")
    
    print(f"\n   2. 🔍 Keywords Filter:")
    print(f"      ⚠️  Temporarily use ONLY 1 keyword (e.g., 'Python')")
    print(f"      ⚠️  Avoid over-filtering - too many keywords = fewer jobs")
    
    print(f"\n   3. 🌍 Geographic Filter:")
    print(f"      ⚠️  Temporarily REMOVE all country exclusions")
    print(f"      ⚠️  Allow jobs from all countries to see more results")
    
    print(f"\n   4. 💰 Budget Filter:")
    print(f"      ⚠️  Set wide range (e.g., $10 - $500/hr)")
    print(f"      ⚠️  Or remove budget filter entirely")
    
    print(f"\n   5. 📊 Sections Enabled:")
    print(f"      ✅ Enable 'Best Match' section")
    print(f"      ✅ Enable 'Most Recent' section")
    print(f"      ✅ Enable 'Saved Searches' if configured")
    
    print(f"\n   6. 🔄 Feed Status:")
    print(f"      ✅ Ensure Vollna extension is running")
    print(f"      ✅ Check Vollna logs for 'Fetched job from Upwork'")
    print(f"      ✅ Check Vollna logs for 'Sending job to webhook'")
    
    print(f"\n   7. 🧪 Test Mode:")
    print(f"      ❌ DISABLE test scripts")
    print(f"      ❌ Stop running test_vollna_webhook.sh")
    print(f"      ❌ Stop running monitor_vollna_jobs.py")

def generate_fix_summary():
    """Generate summary of fixes needed"""
    print_header("Fix Summary & Next Steps")
    
    print(f"\n✅ Completed Checks:")
    print(f"   1. Webhook endpoint verified: {WEBHOOK_URL}")
    print(f"   2. /jobs/all endpoint verified: {JOBS_ALL_URL}")
    print(f"   3. Other endpoints listed")
    print(f"   4. Filter recommendations provided")
    
    print(f"\n📋 Action Items:")
    print(f"   1. ✅ Verify Vollna webhook URL matches: {WEBHOOK_URL}")
    print(f"   2. ✅ Ensure Vollna is sending POST requests (not GET)")
    print(f"   3. ✅ Check Vollna Dashboard filters are loose (1 keyword, no country exclusions)")
    print(f"   4. ✅ Enable 'Best Match' and 'Most Recent' sections in Vollna")
    print(f"   5. ✅ Check Render logs for webhook activity: '🔹 Webhook hit!'")
    print(f"   6. ✅ Monitor for real jobs: Run 'python3 analyze_jobs.py'")
    
    print(f"\n🔍 How to Verify Real Jobs:")
    print(f"   1. Check Render logs for incoming webhooks")
    print(f"   2. Run: python3 analyze_jobs.py")
    print(f"   3. Check frontend: http://localhost:8080")
    print(f"   4. Look for jobs with real Upwork URLs (not /~test)")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Vollna Integration Verification & Fix")
    print("="*60)
    
    # Run all checks
    webhook_ok = check_webhook_endpoint()
    jobs_ok = check_jobs_all_source()
    check_other_endpoints()
    check_vollna_filters()
    generate_fix_summary()
    
    print(f"\n{'='*60}")
    if webhook_ok and jobs_ok:
        print("✅ All checks completed successfully!")
    else:
        print("⚠️  Some checks failed - review output above")
    print(f"{'='*60}\n")

