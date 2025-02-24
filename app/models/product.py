from sqlalchemy import Boolean, Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Product(Base):
    """Product Model for storing product related details
    This model represents items available for purchase in the e-commerce system
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    # Name of the product as displayed to customers
    name = Column(String, index=True, nullable=False)
    # Detailed description of the product features and specifications
    description = Column(Text, nullable=True)
    # Current selling price of the product
    price = Column(Float, nullable=False)
    # Number of items currently available in stock
    stock = Column(Integer, nullable=False, default=0)
    # Category or type of the product (e.g., Electronics, Clothing)
    category = Column(String, index=True)
    # URL to the main product image
    image_url = Column(String, nullable=True)
    # SKU (Stock Keeping Unit) - unique identifier for inventory management
    sku = Column(String, unique=True, index=True)
    # Whether the product is currently available for purchase
    is_active = Column(Boolean, default=True)
    # Reference to the seller/vendor of the product
    seller_id = Column(Integer, ForeignKey('users.id'))
    seller = relationship("User", back_populates="products")
    # Automatically track when the product was added
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Automatically track when the product was last updated
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())