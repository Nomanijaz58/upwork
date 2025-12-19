#!/bin/bash

# ⚠️  DISABLED - DO NOT RUN THIS SCRIPT
# This script creates TEST jobs that pollute the database
# Use verify_vollna_fix.py instead for verification

echo "❌ ERROR: This script is DISABLED to prevent test job creation."
echo "   Use 'python3 verify_vollna_fix.py' for verification instead."
echo "   Exiting..."
exit 1

# Test Vollna Webhook and Monitor Jobs
# This script helps verify Vollna webhook is working and jobs are being received

API_URL="https://upwork-xxsc.onrender.com"
# For local testing, use: API_URL="http://localhost:8000"
SECRET="9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394"

echo "🔍 Vollna Webhook Testing & Monitoring"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check endpoint
check_endpoint() {
    local endpoint=$1
    local description=$2
    
    echo -n "Checking $description... "
    response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    else
        echo -e "${RED}❌ Failed (HTTP $http_code)${NC}"
        echo "$body"
    fi
    echo ""
}

# 1. Check health
echo "1️⃣  Backend Health Check"
check_endpoint "/health" "Backend health"

# 2. Check current jobs count
echo "2️⃣  Current Jobs in Database"
check_endpoint "/jobs/all" "All jobs from Vollna"

# 3. Send test job via webhook
echo "3️⃣  Sending Test Job via Webhook"
TIMESTAMP=$(date +%s)
TEST_JOB='[{
    "title": "Test Job from Vollna Monitor '"$TIMESTAMP"'",
    "url": "https://www.upwork.com/jobs/~test'"$TIMESTAMP"'",
    "budget": 75.0,
    "client_name": "Test Client",
    "description": "This is a test job sent via webhook monitoring script",
    "skills": ["Python", "FastAPI", "Testing"],
    "proposals": 5,
    "source": "vollna"
}]'

echo "Sending job..."
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/webhook/vollna" \
    -H "Content-Type: application/json" \
    -H "X-N8N-Secret: $SECRET" \
    -d "$TEST_JOB")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✅ Webhook accepted job${NC}"
    echo "$body" | python3 -m json.tool
else
    echo -e "${RED}❌ Webhook failed (HTTP $http_code)${NC}"
    echo "$body"
fi
echo ""

# 4. Wait and check jobs again
echo "4️⃣  Verifying Job Was Stored"
sleep 2
check_endpoint "/jobs/all" "All jobs (should include new test job)"

# 5. Check filter endpoint
echo "5️⃣  Testing Filter Endpoint"
FILTER_PAYLOAD='{
    "keywords": ["Python", "Test"],
    "budget_min": 50,
    "budget_max": 100
}'

echo "Testing with filters: $FILTER_PAYLOAD"
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/jobs/filter/vollna" \
    -H "Content-Type: application/json" \
    -d "$FILTER_PAYLOAD")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✅ Filter endpoint working${NC}"
    echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'Found {d.get(\"count\", 0)} jobs'); [print(f'  - {j.get(\"title\")} (${j.get(\"budget\")})') for j in d.get('jobs', [])[:5]]" 2>/dev/null || echo "$body"
else
    echo -e "${RED}❌ Filter failed (HTTP $http_code)${NC}"
    echo "$body"
fi
echo ""

echo "✅ Testing Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Check Render logs for webhook activity"
echo "2. Monitor frontend at http://localhost:8080"
echo "3. Verify jobs appear in dashboard"
echo "4. Check Vollna extension/n8n workflow is sending jobs"
