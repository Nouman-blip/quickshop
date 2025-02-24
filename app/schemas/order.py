from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.order import OrderStatus

class OrderItemBase(BaseModel):
    """Base OrderItem Schema"""
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    """Schema for creating a new order item"""
    pass

class OrderItemInDB(OrderItemBase):
    """Schema for order item in DB"""
    id: int
    order_id: int
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    """Base Order Schema"""
    shipping_address: str

class OrderCreate(OrderBase):
    """Schema for creating a new order"""
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    """Schema for updating an existing order"""
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None

class OrderInDBBase(OrderBase):
    """Base schema for Order in DB"""
    id: int
    customer_id: int
    total_amount: float
    status: OrderStatus
    payment_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItemInDB]

    class Config:
        from_attributes = True

class Order(OrderInDBBase):
    """Schema for returning order to client"""
    pass

class OrderInDB(OrderInDBBase):
    """Schema for order stored in DB"""
    pass