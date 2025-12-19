#!/usr/bin/env python3
"""
Test Bearer Token authentication for Vollna webhook.
"""
import urllib.request
import json
import sys
from datetime import datetime

API_URL = "https://upwork-xxsc.onrender.com"
WEBHOOK_URL = f"{API_URL}/webhook/vollna"

# Use the same token as N8N_SHARED_SECRET (or set VOLLNA_BEARER_TOKEN in .env)
BEARER_TOKEN = "9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394"

def test_bearer_token():
    """Test webhook with Bearer Token authentication."""
    print("🧪 Testing Vollna Webhook with Bearer Token")
    print("=" * 60)
    print(f"URL: {WEBHOOK_URL}\n")
    
    # Test payload
    test_payload = {
        "title": f"Bearer Token Test {int(datetime.utcnow().timestamp())}",
        "url": "https://www.upwork.com/jobs/~bearer-test",
        "budget": 75.0,
        "client_name": "Test Client",
        "platform": "upwork"
    }
    
    print("📤 Sending test payload with Bearer Token...")
    print(f"Authorization: Bearer {BEARER_TOKEN[:20]}...\n")
    
    try:
        data = json.dumps(test_payload).encode('utf-8')
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {BEARER_TOKEN}"
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            response_text = response.read().decode('utf-8')
            
            print(f"✅ Status code: {status_code}")
            print(f"📥 Response:")
            try:
                response_json = json.loads(response_text)
                print(json.dumps(response_json, indent=2))
            except:
                print(response_text)
            
            if status_code == 200:
                print("\n🎉 Bearer Token authentication successful!")
                return True
            else:
                print(f"\n❌ Test failed with status {status_code}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error: {e.code} - {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"Response body: {error_body}")
        except:
            pass
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bearer_token()
    sys.exit(0 if success else 1)

