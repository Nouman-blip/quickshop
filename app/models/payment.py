from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.db.base_class import Base

class PaymentStatus(PyEnum):
    # Payment is pending processing
    PENDING = "pending"
    # Payment has been successfully processed
    COMPLETED = "completed"
    # Payment failed during processing
    FAILED = "failed"
    # Payment was refunded
    REFUNDED = "refunded"

class PaymentMethod(PyEnum):
    # Credit card payment
    CREDIT_CARD = "credit_card"
    # PayPal payment
    PAYPAL = "paypal"
    # Bank transfer
    BANK_TRANSFER = "bank_transfer"

class Payment(Base):
    """Payment Model for storing payment related details
    This model tracks all payment transactions in the system
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    # Order associated with this payment
    order_id = Column(Integer, ForeignKey('orders.id'))
    order = relationship("Order", back_populates="payments")
    # Amount processed in this payment
    amount = Column(Float, nullable=False)
    # Payment method used
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    # Current status of the payment
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    # Transaction ID from payment processor
    transaction_id = Column(String, unique=True, index=True)
    # Additional payment details (JSON stored as string)
    payment_details = Column(String, nullable=True)
    # When the payment was initiated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # When the payment status was last updated
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())