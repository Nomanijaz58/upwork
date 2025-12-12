# Setup Guide for Developers

## Quick Start

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file**
   ```bash
   # Copy the example (if it exists) or create manually
   # Required variables:
   DATABASE_URL=mysql+aiomysql://root:@localhost/upwork_db
   MONGODB_URL=mongodb://localhost:27017/upwork
   ```

3. **Clear Python cache** (if having import issues)
   ```bash
   find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
   find . -type f -name "*.pyc" -delete 2>/dev/null
   ```

4. **Start the server**
   ```bash
   python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Common Issues

### Files Not Opening in IDE

**Problem**: Files appear corrupted or can't be opened

**Solutions**:
1. Clear Python cache files:
   ```bash
   rm -rf app/__pycache__
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. Check Python version compatibility:
   - Current project uses Python 3.9+
   - Cache files show `cpython-312` which means they were created with Python 3.12
   - Delete cache files and let your Python version recreate them

### Import Errors

**Problem**: `ModuleNotFoundError` when importing

**Solutions**:
1. Ensure you're in the `backend` directory
2. Install all requirements: `pip install -r requirements.txt`
3. Check that virtual environment is activated (if using one)

### Database Connection Errors

**Problem**: Can't connect to MongoDB

**Solutions**:
1. Verify MongoDB is running: `lsof -i :27017`
2. Check `.env` file has correct `MONGODB_URL`
3. Test connection: `mongosh mongodb://localhost:27017/upwork`

## File Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py       # Settings and configuration
│   ├── db.py          # Database connection (MongoDB)
│   ├── main.py        # FastAPI app entry point
│   ├── models.py      # Beanie document models
│   └── routes/
│       ├── __init__.py
│       └── example.py  # API routes
├── .env               # Environment variables (create this)
└── requirements.txt   # Python dependencies
```

## Environment Variables

Create a `.env` file in the `backend/` directory with:

```env
DATABASE_URL=mysql+aiomysql://root:@localhost/upwork_db
MONGODB_URL=mongodb://localhost:27017/upwork
```

