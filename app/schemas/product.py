from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ProductBase(BaseModel):
    """Base Product Schema with common attributes"""
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None
    sku: str
    is_active: bool = True

class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass

class ProductUpdate(ProductBase):
    """Schema for updating an existing product"""
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    is_active: Optional[bool] = None

class ProductInDBBase(ProductBase):
    """Base schema for Product in DB, includes generated fields"""
    id: int
    seller_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Product(ProductInDBBase):
    """Schema for returning product to client"""
    pass

class ProductInDB(ProductInDBBase):
    """Schema for product stored in DB"""
    pass