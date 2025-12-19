#!/usr/bin/env python3
"""
Quick test script for Vollna webhook endpoint.
Tests the webhook with a sample payload and shows the response.
"""
import urllib.request
import urllib.error
import json
import sys
from datetime import datetime

# Configuration
WEBHOOK_URL = "https://upwork-xxsc.onrender.com/webhook/vollna"
# Get secret from environment or use None for testing
N8N_SECRET = "9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394"  # Replace with your actual secret

def test_webhook():
    """Test the webhook endpoint with a sample payload."""
    print("🧪 Testing Vollna Webhook")
    print("=" * 50)
    print(f"URL: {WEBHOOK_URL}\n")
    
    # Test payload - single job
    test_payload = {
        "title": f"Test Job from Python Script - {datetime.utcnow().isoformat()}",
        "description": "This is a test job sent via Python script to verify webhook functionality",
        "url": f"https://www.upwork.com/jobs/~test{int(datetime.utcnow().timestamp())}",
        "budget": 75.0,
        "client_name": "Test Client",
        "skills": ["Python", "FastAPI", "Testing"],
        "proposals": 5,
        "postedOn": datetime.utcnow().isoformat(),
        "platform": "upwork"
    }
    
    print("📤 Sending test payload:")
    print(json.dumps(test_payload, indent=2))
    print()
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "X-N8N-Secret": N8N_SECRET
    }
    
    try:
        # Send POST request
        print("⏳ Sending POST request...")
        
        # Prepare request
        data = json.dumps(test_payload).encode('utf-8')
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=data,
            headers=headers,
            method='POST'
        )
        
        # Send request
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            response_text = response.read().decode('utf-8')
            
            print(f"\n✅ Status code: {status_code}")
            print(f"📥 Response:")
            
            try:
                response_json = json.loads(response_text)
                print(json.dumps(response_json, indent=2))
            except:
                print(response_text)
            
            # Check if successful
            if status_code == 200:
                print("\n🎉 Webhook test successful!")
                return True
            else:
                print(f"\n❌ Webhook test failed with status {status_code}")
                return False
            
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error: {e.code} - {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"Response body: {error_body}")
        except:
            pass
        return False
    except urllib.error.URLError as e:
        print(f"\n❌ URL Error: Could not reach {WEBHOOK_URL}")
        print(f"   Error: {e.reason}")
        print("   Make sure the server is running and accessible.")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_webhook_simple():
    """Simple one-liner test (as requested by user)."""
    url = WEBHOOK_URL
    test_payload = {"test": "hello"}
    
    print("🧪 Simple Webhook Test")
    print("=" * 50)
    
    try:
        data = json.dumps(test_payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "X-N8N-Secret": N8N_SECRET
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            response_text = response.read().decode('utf-8')
            print(f"Status code: {status_code}")
            print(f"Response: {response_text}")
            return status_code == 200
    except urllib.error.HTTPError as e:
        print(f"Status code: {e.code}")
        print(f"Response: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--simple":
        # Run simple test
        test_webhook_simple()
    else:
        # Run full test
        test_webhook()

