#!/bin/bash
# Script to clean Python cache files
# This helps when files aren't opening properly in IDEs

echo "Cleaning Python cache files..."

# Remove __pycache__ directories
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null

# Remove .pyc files
find . -type f -name "*.pyc" -delete 2>/dev/null

# Remove .pyo files
find . -type f -name "*.pyo" -delete 2>/dev/null

# Remove .pytest_cache
find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null

echo "Cache files cleaned!"
echo ""
echo "If you're still having issues:"
echo "1. Make sure all dependencies are installed: pip install -r backend/requirements.txt"
echo "2. Check that .env file exists in backend/ directory"
echo "3. Restart your IDE"

