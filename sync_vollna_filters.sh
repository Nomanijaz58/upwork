#!/bin/bash

# Quick script to sync Vollna filters to backend
# Based on your Vollna dashboard configuration

API_URL="https://upwork-xxsc.onrender.com"
SECRET="9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394"

echo "🔄 Syncing Vollna Filters to Backend"
echo "===================================="
echo ""

# Extract from your Vollna dashboard:
# - Keywords: python, english language, fastapis, flask
# - Search in: title, description, skills
# - Match mode: any (job matches if it has ANY keyword)
# - Hourly rate max: 50

echo "📋 Syncing filters..."
SYNC_RESPONSE=$(curl -s -X POST "$API_URL/vollna/sync/filters" \
  -H "X-N8N-Secret: $SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": {
      "terms": ["python", "english language", "fastapis", "flask"],
      "match_mode": "any",
      "search_in": ["title", "description", "skills"]
    },
    "budget": {
      "hourly_rate_max": 50.0
    },
    "geo": {
      "excluded_countries": []
    }
  }')

echo "Response: $SYNC_RESPONSE"
echo ""

# Check if sync was successful
if echo "$SYNC_RESPONSE" | grep -q '"synced":true'; then
    echo "✅ Filters synced successfully!"
else
    echo "❌ Sync failed. Check the response above."
    exit 1
fi

echo ""
echo "📊 Verifying sync status..."
STATUS_RESPONSE=$(curl -s -X GET "$API_URL/vollna/sync/filters/status" \
  -H "X-N8N-Secret: $SECRET")

echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"
echo ""

echo "✅ Sync complete!"
echo ""
echo "📝 Next steps:"
echo "1. Test with a job: ./quick_test.sh"
echo "2. Check if jobs pass filters: inserted_filtered should be > 0"
echo "3. View filters in Swagger: $API_URL/docs"

