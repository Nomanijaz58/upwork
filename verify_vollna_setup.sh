#!/bin/bash

# Verify Vollna Setup - Check if Real Upwork Jobs are Coming
# This script helps verify Vollna is configured correctly and sending real jobs

API_URL="https://upwork-xxsc.onrender.com"

echo "🔍 Vollna Setup Verification"
echo "============================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}STEP 1️⃣  Checking Vollna Webhook Configuration${NC}"
echo "---------------------------------------------------"
echo ""
echo "⚠️  MANUAL CHECK REQUIRED:"
echo ""
echo "1. Open Vollna Extension/Dashboard"
echo "2. Go to Settings → Integrations → Webhooks"
echo "3. Verify webhook exists:"
echo -e "   ${GREEN}URL: https://upwork-xxsc.onrender.com/webhook/vollna${NC}"
echo -e "   ${GREEN}Enabled: true${NC}"
echo -e "   ${GREEN}Headers: X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394${NC}"
echo ""
read -p "Press Enter when you've verified the webhook configuration..."

echo ""
echo -e "${BLUE}STEP 2️⃣  Checking Current Jobs (Identifying Test vs Real)${NC}"
echo "---------------------------------------------------"
echo ""

response=$(curl -s "$API_URL/jobs/all")
count=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('count', 0))")

echo "Total jobs in database: $count"
echo ""

if [ "$count" -gt 0 ]; then
    echo "Analyzing jobs to identify test vs real:"
    echo ""
    
    echo "$response" | python3 -c "
import sys, json
d = json.load(sys.stdin)
jobs = d.get('jobs', [])
test_jobs = []
real_jobs = []

for j in jobs:
    title = j.get('title', '').lower()
    url = j.get('url', '')
    client = j.get('client_name', '').lower()
    
    # Check if it's a test job
    is_test = (
        'test' in title or
        'test' in client or
        '/~test' in url or
        'monitor' in title.lower() or
        'script' in title.lower()
    )
    
    if is_test:
        test_jobs.append(j)
    else:
        real_jobs.append(j)

print(f'📊 Analysis:')
print(f'   Test jobs: {len(test_jobs)}')
print(f'   Real jobs: {len(real_jobs)}')
print()

if test_jobs:
    print('⚠️  TEST JOBS FOUND:')
    for j in test_jobs:
        print(f'   - {j.get(\"title\")} (ID: {j.get(\"_id\")})')
    print()
    print('💡 These were created by test scripts. Real jobs will have:')
    print('   - Real Upwork URLs (not /~test)')
    print('   - Real client names (not "Test Client")')
    print('   - Real job titles from Upwork')
    print()

if real_jobs:
    print('✅ REAL JOBS FOUND:')
    for j in real_jobs:
        print(f'   - {j.get(\"title\")}')
        print(f'     URL: {j.get(\"url\")}')
        print(f'     Client: {j.get(\"client_name\")}')
    print()
else:
    print('❌ NO REAL JOBS FOUND')
    print('   This means Vollna is not sending real jobs yet.')
    print()
"
fi

echo ""
echo -e "${BLUE}STEP 3️⃣  Checking Backend Webhook Endpoint${NC}"
echo "---------------------------------------------------"
echo ""

# Test webhook endpoint exists
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/webhook/vollna" \
    -H "Content-Type: application/json" \
    -H "X-N8N-Secret: 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394" \
    -d '{}')

if [ "$response" = "400" ] || [ "$response" = "200" ]; then
    echo -e "${GREEN}✅ Webhook endpoint is accessible${NC}"
    echo "   Endpoint: $API_URL/webhook/vollna"
else
    echo -e "${RED}❌ Webhook endpoint issue (HTTP $response)${NC}"
fi
echo ""

echo -e "${BLUE}STEP 4️⃣  Checking Render Logs (Webhook Activity)${NC}"
echo "---------------------------------------------------"
echo ""
echo "⚠️  MANUAL CHECK REQUIRED:"
echo ""
echo "1. Go to: https://dashboard.render.com"
echo "2. Select your service: upwork-xxsc"
echo "3. Click 'Logs' tab"
echo "4. Look for these messages:"
echo ""
echo -e "   ${GREEN}✅ Good signs:${NC}"
echo "   - 'Received Vollna webhook payload'"
echo "   - 'Processing X jobs from Vollna'"
echo "   - 'Inserted job X: [Real Job Title]'"
echo ""
echo -e "   ${RED}❌ Problem signs:${NC}"
echo "   - No webhook requests"
echo "   - Authentication errors"
echo "   - Only test jobs being inserted"
echo ""
read -p "Press Enter when you've checked Render logs..."

echo ""
echo -e "${BLUE}STEP 5️⃣  Vollna Extension Checklist${NC}"
echo "---------------------------------------------------"
echo ""
echo "Verify these in Vollna Extension/Dashboard:"
echo ""
echo "✅ Keywords configured:"
echo "   - Should have at least 1 keyword (e.g., 'Python')"
echo "   - Not too restrictive"
echo ""
echo "✅ Sections enabled:"
echo "   - Best Match: Enabled"
echo "   - Most Recent: Enabled"
echo ""
echo "✅ Country filters:"
echo "   - Temporarily DISABLE country exclusions"
echo "   - Allow jobs from all locations"
echo ""
echo "✅ Monitoring active:"
echo "   - Extension is enabled"
echo "   - Monitoring Upwork pages"
echo "   - Webhook is enabled"
echo ""
read -p "Press Enter when you've verified Vollna extension settings..."

echo ""
echo -e "${BLUE}STEP 6️⃣  Checking for Real Job Indicators${NC}"
echo "---------------------------------------------------"
echo ""

if [ "$count" -gt 0 ]; then
    echo "$response" | python3 -c "
import sys, json
d = json.load(sys.stdin)
jobs = d.get('jobs', [])

real_indicators = 0
for j in jobs:
    url = j.get('url', '')
    # Real Upwork URLs have format: /jobs/~[alphanumeric]
    # Test URLs have: /jobs/~test
    if '/~test' not in url and 'upwork.com/jobs/~' in url:
        real_indicators += 1

if real_indicators > 0:
    print('✅ Found jobs with real Upwork URL format')
    print(f'   {real_indicators} job(s) have real Upwork URLs')
else:
    print('❌ No jobs with real Upwork URLs found')
    print('   All jobs appear to be test jobs')
    print('   Real jobs will have URLs like: https://www.upwork.com/jobs/~abc123def456')
"
fi

echo ""
echo -e "${YELLOW}📋 SUMMARY & NEXT STEPS${NC}"
echo "============================"
echo ""
echo "1. ✅ Webhook endpoint is configured"
echo "2. ⚠️  Verify Vollna webhook URL matches: https://upwork-xxsc.onrender.com/webhook/vollna"
echo "3. ⚠️  Check Render logs for webhook activity"
echo "4. ⚠️  Verify Vollna extension is monitoring Upwork"
echo "5. ⚠️  Temporarily disable country filters in Vollna"
echo ""
echo "To monitor for NEW real jobs:"
echo "  python3 monitor_vollna_jobs.py"
echo ""
echo "To check current jobs:"
echo "  ./show_jobs.sh"
echo ""

