#!/usr/bin/env python3
"""
Python one-liner to test Vollna webhook (as requested).
Run this directly or copy the code into a Python shell.
"""
import urllib.request
import json

# Replace with your webhook URL
url = "https://upwork-xxsc.onrender.com/webhook/vollna"
secret = "9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394"

# Send a test payload to see what Vollna would send
test_payload = {"test": "hello"}

# Prepare request
data = json.dumps(test_payload).encode('utf-8')
req = urllib.request.Request(
    url,
    data=data,
    headers={
        "Content-Type": "application/json",
        "X-N8N-Secret": secret
    },
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        print("Status code:", response.getcode())
        print("Response:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Status code:", e.code)
    print("Response:", e.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)

