from pymongo import MongoClient
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from typing import AsyncGenerator

from .config import settings
from .models import User, Product

# PyMongo synchronous client for connection management
pymongo_client: MongoClient = None
pymongo_database = None

# Motor client for Beanie (required for async operations)
motor_client: AsyncIOMotorClient = None


async def init_mongodb():
    """
    Initialize MongoDB connection using PyMongo client and Beanie ODM.
    
    Note: While we use PyMongo for connection management, Beanie requires
    Motor's AsyncIOMotorClient internally for async operations. This is
    a requirement of Beanie - it cannot work without Motor for async ops.
    However, we configure everything using PyMongo connection strings and
    the user only interacts with Beanie models, not Motor directly.
    """
    global pymongo_client, pymongo_database, motor_client
    
    # Parse database name from connection string
    db_name = settings.MONGODB_URL.split('/')[-1].split('?')[0]
    
    # Create PyMongo client for connection management
    pymongo_client = MongoClient(settings.MONGODB_URL)
    pymongo_database = pymongo_client[db_name]
    
    # Create Motor client for Beanie (required for async operations)
    # Motor uses the same connection string format as PyMongo
    motor_client = AsyncIOMotorClient(settings.MONGODB_URL)
    motor_database = motor_client[db_name]
    
    # Initialize Beanie with Motor database
    # Beanie will automatically create collections when documents are inserted
    await init_beanie(
        database=motor_database,
        document_models=[User, Product]
    )
    
    print(f"MongoDB initialized with PyMongo: {db_name}")
    print(f"Collections will be created automatically by Beanie")


async def close_mongodb():
    """Close MongoDB connections"""
    global pymongo_client, motor_client
    if motor_client:
        motor_client.close()
    if pymongo_client:
        pymongo_client.close()
    print("MongoDB connections closed")


async def get_db() -> AsyncGenerator:
    """
    Dependency function that returns the Motor database.
    
    Note: Beanie models can be used directly without this dependency,
    but this is provided for cases where direct database access is needed.
    """
    global motor_client
    db_name = settings.MONGODB_URL.split('/')[-1].split('?')[0]
    yield motor_client[db_name]
