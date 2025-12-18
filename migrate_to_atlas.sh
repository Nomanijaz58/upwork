#!/bin/bash

# MongoDB Migration Script: Local to Atlas
# This script helps migrate data from local MongoDB to MongoDB Atlas

set -e

echo "🚀 MongoDB Migration: Local to Atlas"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if mongodump is available
if ! command -v mongodump &> /dev/null; then
    echo -e "${RED}❌ mongodump not found${NC}"
    echo "Please install MongoDB Database Tools:"
    echo "  macOS: brew install mongodb-database-tools"
    echo "  Or use MongoDB Compass export/import method"
    exit 1
fi

# Configuration
LOCAL_URI="mongodb://localhost:27017"
LOCAL_DB="upwork_proposal_bot"
EXPORT_DIR="$HOME/mongodb_export_$(date +%Y%m%d_%H%M%S)"

# Get Atlas connection string
echo -e "${YELLOW}Enter your MongoDB Atlas connection string:${NC}"
echo "Format: mongodb+srv://username:password@cluster0.xxxxx.mongodb.net"
read -p "Atlas URI: " ATLAS_URI

if [ -z "$ATLAS_URI" ]; then
    echo -e "${RED}❌ Atlas URI is required${NC}"
    exit 1
fi

# Create export directory
mkdir -p "$EXPORT_DIR"
echo -e "${GREEN}✓ Created export directory: $EXPORT_DIR${NC}"

# Export from local MongoDB
echo ""
echo -e "${YELLOW}📤 Exporting data from local MongoDB...${NC}"
mongodump --uri="$LOCAL_URI" \
    --db="$LOCAL_DB" \
    --out="$EXPORT_DIR"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Export completed successfully${NC}"
else
    echo -e "${RED}❌ Export failed${NC}"
    exit 1
fi

# Import to Atlas
echo ""
echo -e "${YELLOW}📥 Importing data to MongoDB Atlas...${NC}"
mongorestore --uri="$ATLAS_URI" \
    --db="$LOCAL_DB" \
    --drop \
    "$EXPORT_DIR/$LOCAL_DB"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Import completed successfully${NC}"
else
    echo -e "${RED}❌ Import failed${NC}"
    echo "Please check:"
    echo "  1. Atlas connection string is correct"
    echo "  2. Network access allows your IP"
    echo "  3. Database user has write permissions"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Migration completed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Update .env file with Atlas connection string"
echo "  2. Test connection: uvicorn app.main:app --reload"
echo "  3. Check health: http://localhost:8000/health"
echo ""
echo "Export directory: $EXPORT_DIR"
echo "You can delete it after verifying the migration."

