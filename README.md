# Upwork Automation

FastAPI application with MongoDB using Beanie ODM and PyMongo.

## Setup Instructions

### Prerequisites

- Python 3.9+
- MongoDB running on `localhost:27017`
- MySQL (optional, for legacy endpoints)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd upwork_automation
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual database credentials
   ```

5. **Start MongoDB** (if not already running)
   ```bash
   # macOS with Homebrew
   brew services start mongodb-community
   
   # Or using Docker
   docker run -d -p 27017:27017 mongo
   ```

6. **Run the server**
   ```bash
   cd backend
   python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - API Routes: http://localhost:8000/api/

## Project Structure

```
upwork_automation/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration settings
│   │   ├── db.py              # MongoDB connection setup
│   │   ├── main.py            # FastAPI application
│   │   ├── models.py          # Beanie document models
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── example.py     # Example CRUD routes
│   │   └── tasks.py
│   ├── .env.example           # Environment variables template
│   └── requirements.txt       # Python dependencies
├── infra/
│   └── docker-compose.yml
└── README.md
```

## API Endpoints

### User Endpoints
- `POST /api/users` - Create a new user
- `GET /api/users` - Get all users
- `GET /api/users/{user_id}` - Get a single user
- `PUT /api/users/{user_id}` - Update a user
- `DELETE /api/users/{user_id}` - Delete a user

### Product Endpoints
- `POST /api/products` - Create a new product
- `GET /api/products` - Get all products
- `GET /api/products/{product_id}` - Get a single product
- `PUT /api/products/{product_id}` - Update a product
- `DELETE /api/products/{product_id}` - Delete a product

## Technology Stack

- **FastAPI** - Modern Python web framework
- **Beanie** - MongoDB ODM (Object Document Mapper)
- **PyMongo** - MongoDB driver
- **Motor** - Async MongoDB driver (used internally by Beanie)
- **Pydantic** - Data validation

## Troubleshooting

### Files not opening in IDE

If other developers can't open files:

1. **Clear Python cache**
   ```bash
   find . -type d -name __pycache__ -exec rm -r {} +
   find . -type f -name "*.pyc" -delete
   ```

2. **Reinstall dependencies**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Check Python version**
   ```bash
   python3 --version  # Should be 3.9+
   ```

4. **Verify environment variables**
   - Ensure `.env` file exists
   - Check that MongoDB URL is correct

### Common Issues

- **Import errors**: Make sure all dependencies are installed
- **Database connection errors**: Verify MongoDB is running
- **Port already in use**: Change port in uvicorn command or kill existing process

## Development

The server runs with auto-reload enabled, so code changes will automatically restart the server.

