#!/bin/bash

# Quick Test Script for All Endpoints
# Run this to test all endpoints quickly

API_URL="https://upwork-xxsc.onrender.com"
BEARER_TOKEN="9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394"

echo "🧪 Quick Endpoint Testing"
echo "========================"
echo ""

# Test 1: Health
echo "1️⃣  Health Check..."
HEALTH=$(curl -s "$API_URL/health")
echo "   Response: $HEALTH"
if echo "$HEALTH" | grep -q '"status":"ok"'; then
    echo "   ✅ Health check passed"
else
    echo "   ❌ Health check failed"
fi
echo ""

# Test 2: Feed Status
echo "2️⃣  Feed Status..."
FEED=$(curl -s "$API_URL/feeds/status?source=vollna")
echo "   Response: $FEED"
echo ""

# Test 3: Get Jobs (before creating)
echo "3️⃣  Get Latest Jobs (before test job)..."
JOBS_BEFORE=$(curl -s "$API_URL/jobs?source=vollna&limit=5")
COUNT_BEFORE=$(echo "$JOBS_BEFORE" | grep -o '"id"' | wc -l | tr -d ' ')
echo "   Jobs found: $COUNT_BEFORE"
echo ""

# Test 4: Create Test Job via Webhook
echo "4️⃣  Creating Test Job via Webhook..."
TIMESTAMP=$(date +%s)
WEBHOOK_RESPONSE=$(curl -s -X POST "$API_URL/vollna/jobs" \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"jobs\": [
      {
        \"title\": \"Python Developer Test Job $TIMESTAMP\",
        \"description\": \"Test job created at $(date -u +"%Y-%m-%dT%H:%M:%SZ")\",
        \"url\": \"https://www.upwork.com/jobs/~test$TIMESTAMP\",
        \"budget\": 75.0,
        \"proposals\": 8,
        \"skills\": [\"Python\", \"FastAPI\", \"MongoDB\"],
        \"postedOn\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"
      }
    ]
  }")

echo "   Response: $WEBHOOK_RESPONSE"
if echo "$WEBHOOK_RESPONSE" | grep -q '"inserted_raw":1'; then
    echo "   ✅ Job created successfully"
else
    echo "   ❌ Job creation failed"
fi
echo ""

# Wait a moment for processing
sleep 2

# Test 5: Get Jobs (after creating)
echo "5️⃣  Get Latest Jobs (after test job)..."
JOBS_AFTER=$(curl -s "$API_URL/jobs?source=vollna&limit=5")
COUNT_AFTER=$(echo "$JOBS_AFTER" | grep -o '"id"' | wc -l | tr -d ' ')
echo "   Jobs found: $COUNT_AFTER"
if [ "$COUNT_AFTER" -gt "$COUNT_BEFORE" ]; then
    echo "   ✅ New job appears in results"
else
    echo "   ⚠️  Job count didn't increase (may need to wait or check filters)"
fi
echo ""

# Test 6: Search Jobs (no filters)
echo "6️⃣  Search Jobs (no filters)..."
SEARCH_NO_FILTER=$(curl -s -X POST "$API_URL/jobs/search" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "vollna",
    "limit": 5
  }')

LATEST_COUNT=$(echo "$SEARCH_NO_FILTER" | grep -o '"latest_jobs_count":[0-9]*' | grep -o '[0-9]*')
FILTERED_COUNT=$(echo "$SEARCH_NO_FILTER" | grep -o '"filtered_jobs_count":[0-9]*' | grep -o '[0-9]*')

echo "   Latest jobs count: $LATEST_COUNT"
echo "   Filtered jobs count: $FILTERED_COUNT"
if [ -n "$LATEST_COUNT" ] && [ "$LATEST_COUNT" -gt 0 ]; then
    echo "   ✅ Search endpoint working"
else
    echo "   ⚠️  No jobs found (may need to wait for processing)"
fi
echo ""

# Test 7: Search Jobs (with filters)
echo "7️⃣  Search Jobs (with budget filter)..."
SEARCH_FILTERED=$(curl -s -X POST "$API_URL/jobs/search" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "vollna",
    "min_budget": 50.0,
    "limit": 5
  }')

FILTERED_COUNT_WITH_FILTER=$(echo "$SEARCH_FILTERED" | grep -o '"filtered_jobs_count":[0-9]*' | grep -o '[0-9]*')
echo "   Filtered jobs count (budget >= 50): $FILTERED_COUNT_WITH_FILTER"
if [ -n "$FILTERED_COUNT_WITH_FILTER" ]; then
    echo "   ✅ Filter working"
else
    echo "   ⚠️  Check filter logic"
fi
echo ""

echo "✅ Testing Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Check Swagger UI: $API_URL/docs"
echo "2. Test /jobs/recommend endpoint"
echo "3. Verify in MongoDB Compass"
echo "4. Test with real Vollna webhook"

