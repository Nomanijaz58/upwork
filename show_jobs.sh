#!/bin/bash

# Quick script to show current jobs from Vollna

API_URL="https://upwork-xxsc.onrender.com"

echo "📊 Current Jobs in Database"
echo "============================"
echo ""

response=$(curl -s "$API_URL/jobs/all")
count=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('count', 0))")

echo "Total jobs: $count"
echo ""

if [ "$count" -gt 0 ]; then
    echo "$response" | python3 -c "
import sys, json
d = json.load(sys.stdin)
jobs = d.get('jobs', [])
for i, j in enumerate(jobs, 1):
    print(f'{i}. {j.get(\"title\", \"No title\")}')
    print(f'   ID: {j.get(\"_id\", \"N/A\")}')
    print(f'   Budget: \${j.get(\"budget\", 0)}/hr')
    print(f'   Client: {j.get(\"client_name\", \"Unknown\")}')
    print()
"
else
    echo "No jobs found."
fi

