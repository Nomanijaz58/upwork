from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime


class User(Document):
    """
    User model using Beanie ODM
    """
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    age: Optional[int] = Field(None, description="User's age")
    is_active: bool = Field(default=True, description="Whether user is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"  # Collection name
        indexes = ["email"]  # Index on email field


class Product(Document):
    """
    Product model using Beanie ODM
    """
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., gt=0, description="Product price (must be > 0)")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(default=True, description="Whether product is in stock")
    quantity: int = Field(default=0, ge=0, description="Product quantity")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "products"  # Collection name
        indexes = ["name", "category"]  # Indexes on name and category
