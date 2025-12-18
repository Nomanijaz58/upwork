#!/bin/bash

# Import data to MongoDB Atlas
# Run this script to import your local MongoDB data to Atlas

echo "📥 Importing data to MongoDB Atlas..."
echo ""

mongorestore --uri="mongodb+srv://n4221891_db_user:noman5858@cluster0.jnwiaoi.mongodb.net" \
    --db=upwork_proposal_bot \
    --drop \
    ~/mongodb_export_20251219_021949/upwork_proposal_bot

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Import completed successfully!"
    echo ""
    echo "Data migrated to MongoDB Atlas!"
    echo "Your .env file has been updated with the Atlas connection string."
else
    echo ""
    echo "❌ Import failed"
    echo "Please check:"
    echo "  1. Network access allows your IP in Atlas"
    echo "  2. Database user has write permissions"
    echo "  3. Connection string is correct"
fi

