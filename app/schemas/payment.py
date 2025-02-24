from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.payment import PaymentStatus, PaymentMethod

class PaymentBase(BaseModel):
    """Base Payment Schema with common attributes"""
    amount: float
    payment_method: PaymentMethod
    payment_details: Optional[str] = None

class PaymentCreate(PaymentBase):
    """Schema for creating a new payment"""
    order_id: int

class PaymentUpdate(BaseModel):
    """Schema for updating an existing payment"""
    status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None
    payment_details: Optional[str] = None

class PaymentInDBBase(PaymentBase):
    """Base schema for Payment in DB, includes generated fields"""
    id: int
    order_id: int
    status: PaymentStatus
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Payment(PaymentInDBBase):
    """Schema for returning payment to client"""
    pass

class PaymentInDB(PaymentInDBBase):
    """Schema for payment stored in DB"""
    pass