#!/bin/bash

# Test Vollna Webhook Integration
# This script tests the Vollna webhook endpoint with sample data

API_URL="https://upwork-xxsc.onrender.com"
BEARER_TOKEN="9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394"

echo "🧪 Testing Vollna Integration"
echo "=============================="
echo ""

# Test 1: Health Check
echo "1️⃣  Testing Health Endpoint..."
HEALTH=$(curl -s "$API_URL/health")
echo "Response: $HEALTH"
echo ""

# Test 2: Feed Status
echo "2️⃣  Checking Feed Status..."
FEED_STATUS=$(curl -s "$API_URL/feeds/status?source=vollna")
echo "Response: $FEED_STATUS"
echo ""

# Test 3: Get Latest Jobs
echo "3️⃣  Getting Latest Jobs from Vollna..."
JOBS=$(curl -s "$API_URL/jobs?source=vollna&limit=5")
echo "Response: $JOBS"
echo ""

# Test 4: Test Vollna Webhook
echo "4️⃣  Testing Vollna Webhook Endpoint..."
WEBHOOK_RESPONSE=$(curl -s -X POST "$API_URL/vollna/jobs" \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [
      {
        "title": "Test Job from Vollna",
        "description": "This is a test job to verify the webhook integration is working correctly",
        "url": "https://www.upwork.com/jobs/~test_'$(date +%s)'",
        "budget": 50.0,
        "proposals": 5,
        "skills": ["Python", "FastAPI", "MongoDB"],
        "postedOn": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
      }
    ]
  }')

echo "Response: $WEBHOOK_RESPONSE"
echo ""

# Test 5: Verify Job Was Stored
echo "5️⃣  Verifying Job Was Stored..."
sleep 2
LATEST_JOBS=$(curl -s "$API_URL/jobs?source=vollna&limit=1")
echo "Latest Jobs: $LATEST_JOBS"
echo ""

echo "✅ Testing Complete!"
echo ""
echo "Next Steps:"
echo "1. Check Swagger UI: $API_URL/docs"
echo "2. Test /jobs/search endpoint with filters"
echo "3. Test /jobs/recommend for AI recommendations"

