from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from ..models import User, Product

router = APIRouter(prefix="/api", tags=["example"])


# ==================== USER ROUTES ====================

@router.post("/users", response_model=dict, status_code=201)
async def create_user(
    name: str,
    email: str,
    age: int = None,
    is_active: bool = True
):
    """
    Create a new user document
    """
    try:
        # Check if user with email already exists
        existing_user = await User.find_one(User.email == email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create new user
        user = User(
            name=name,
            email=email,
            age=age,
            is_active=is_active
        )
        await user.insert()
        
        return {
            "status": "created",
            "user": user.model_dump(mode='json')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.get("/users", response_model=List[dict])
async def get_all_users(
    skip: int = 0,
    limit: int = 100
):
    """
    Get list of all users
    """
    try:
        users = await User.find_all().skip(skip).limit(limit).to_list()
        return [user.model_dump(mode='json') for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")


@router.get("/users/{user_id}", response_model=dict)
async def get_user(user_id: str):
    """
    Get a single user by ID
    """
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")


@router.put("/users/{user_id}", response_model=dict)
async def update_user(
    user_id: str,
    name: str = None,
    email: str = None,
    age: int = None,
    is_active: bool = None
):
    """
    Update a user document
    """
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields if provided
        if name is not None:
            user.name = name
        if email is not None:
            # Check if email is already taken by another user
            existing_user = await User.find_one(User.email == email)
            if existing_user and existing_user.id != user.id:
                raise HTTPException(status_code=400, detail="Email already taken")
            user.email = email
        if age is not None:
            user.age = age
        if is_active is not None:
            user.is_active = is_active
        
        user.updated_at = datetime.utcnow()
        await user.save()
        
        return {
            "status": "updated",
            "user": user.model_dump(mode='json')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")


@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    """
    Delete a user document
    """
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        await user.delete()
        
        return {
            "status": "deleted",
            "message": f"User {user_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")


# ==================== PRODUCT ROUTES ====================

@router.post("/products", response_model=dict, status_code=201)
async def create_product(
    name: str,
    description: str = None,
    price: float = None,
    category: str = None,
    in_stock: bool = True,
    quantity: int = 0
):
    """
    Create a new product document
    """
    try:
        if price is None or price <= 0:
            raise HTTPException(status_code=400, detail="Price must be greater than 0")
        if category is None:
            raise HTTPException(status_code=400, detail="Category is required")
        
        product = Product(
            name=name,
            description=description,
            price=price,
            category=category,
            in_stock=in_stock,
            quantity=quantity
        )
        await product.insert()
        
        return {
            "status": "created",
            "product": product.model_dump(mode='json')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")


@router.get("/products", response_model=List[dict])
async def get_all_products(
    skip: int = 0,
    limit: int = 100,
    category: str = None
):
    """
    Get list of all products (optionally filtered by category)
    """
    try:
        query = {}
        if category:
            query["category"] = category
        
        if query:
            products = await Product.find(Product.category == category).skip(skip).limit(limit).to_list()
        else:
            products = await Product.find_all().skip(skip).limit(limit).to_list()
        
        return [product.model_dump(mode='json') for product in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")


@router.get("/products/{product_id}", response_model=dict)
async def get_product(product_id: str):
    """
    Get a single product by ID
    """
    try:
        product = await Product.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching product: {str(e)}")


@router.put("/products/{product_id}", response_model=dict)
async def update_product(
    product_id: str,
    name: str = None,
    description: str = None,
    price: float = None,
    category: str = None,
    in_stock: bool = None,
    quantity: int = None
):
    """
    Update a product document
    """
    try:
        product = await Product.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Update fields if provided
        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if price is not None:
            if price <= 0:
                raise HTTPException(status_code=400, detail="Price must be greater than 0")
            product.price = price
        if category is not None:
            product.category = category
        if in_stock is not None:
            product.in_stock = in_stock
        if quantity is not None:
            if quantity < 0:
                raise HTTPException(status_code=400, detail="Quantity cannot be negative")
            product.quantity = quantity
        
        product.updated_at = datetime.utcnow()
        await product.save()
        
        return {
            "status": "updated",
            "product": product.model_dump(mode='json')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")


@router.delete("/products/{product_id}", response_model=dict)
async def delete_product(product_id: str):
    """
    Delete a product document
    """
    try:
        product = await Product.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        await product.delete()
        
        return {
            "status": "deleted",
            "message": f"Product {product_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting product: {str(e)}")

