from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.db.base_class import Base

class OrderStatus(PyEnum):
    # Order has been created but payment is pending
    PENDING = "pending"
    # Payment has been confirmed and order is being processed
    PROCESSING = "processing"
    # Order has been shipped to the customer
    SHIPPED = "shipped"
    # Order has been delivered to the customer
    DELIVERED = "delivered"
    # Order was cancelled by customer or system
    CANCELLED = "cancelled"

class Order(Base):
    """Order Model for storing order related details
    This model tracks customer purchases from creation to delivery
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    # Unique order reference number for customer tracking
    order_number = Column(String, unique=True, index=True)
    # Customer who placed the order
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="orders")
    # Total amount to be paid by customer
    total_amount = Column(Float, nullable=False)
    # Current status of the order in its lifecycle
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    # Shipping address for delivery
    shipping_address = Column(String, nullable=False)
    # Any special instructions from customer
    notes = Column(String, nullable=True)
    # Payment method used (e.g., credit card, PayPal)
    payment_method = Column(String)
    # When the order was placed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # When the order status was last updated
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # Products included in this order
    items = relationship("OrderItem", back_populates="order")