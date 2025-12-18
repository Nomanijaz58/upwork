#!/bin/bash

# Quick import script - Replace YOUR_PASSWORD with your actual password

ATLAS_URI="mongodb+srv://n4221891_db_user:YOUR_PASSWORD@cluster0.jnwiaoi.mongodb.net"
EXPORT_DIR="$HOME/mongodb_export_20251219_021949"

echo "📥 Importing data to MongoDB Atlas..."
echo ""

# Check if export directory exists
if [ ! -d "$EXPORT_DIR/upwork_proposal_bot" ]; then
    echo "❌ Export directory not found: $EXPORT_DIR"
    exit 1
fi

# Run import
mongorestore --uri="$ATLAS_URI" \
    --db=upwork_proposal_bot \
    --drop \
    "$EXPORT_DIR/upwork_proposal_bot"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Import completed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Update .env file with Atlas connection string"
    echo "  2. Test connection"
else
    echo ""
    echo "❌ Import failed"
    echo "Please check:"
    echo "  1. Password is correct (replace YOUR_PASSWORD in the script)"
    echo "  2. Network access allows your IP"
    echo "  3. Database user has write permissions"
fi

