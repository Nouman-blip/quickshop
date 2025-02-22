# app/models.py

from sqlalchemy import (
    Column, Integer, Float, String, Boolean, DateTime, 
    ForeignKey, Table, Enum, Text, func
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

class PackagingType(PyEnum):
    MINIMAL = "minimal"
    RECYCLED = "recycled"
    BIODEGRADABLE = "biodegradable"
    REUSABLE = "reusable"

from sqlalchemy import Column, Integer, String, Numeric, Boolean, Float
from .database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Eco-friendly attributes
    carbon_footprint = Column(Float, default=0.0)
    recycled_content = Column(Float, default=0.0)
    is_recyclable = Column(Boolean, default=False)
    eco_certified = Column(Boolean, default=False)
    water_savings = Column(Float, default=0.0)
    volume = Column(Float)
    packaging_type = Column(Enum(PackagingType), default=PackagingType.MINIMAL)
    sustainability_score = Column(Float, default=0.0)
    eco_certifications = Column(Text)  # JSON list of certifications
    renewable_materials_percentage = Column(Float, default=0.0)
    biodegradable = Column(Boolean, default=False)
    locally_sourced = Column(Boolean, default=False)
    
    eco_metrics = relationship("EcoMetrics", back_populates="product")
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")
    class EcoMetrics(Base):
        __tablename__ = "eco_metrics"
        
        id = Column(Integer, primary_key=True, index=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        
        # Metrics
        carbon_footprint = Column(Float, default=0.0)
        water_savings = Column(Float, default=0.0)
        energy_efficiency = Column(Float, default=0.0)
        waste_reduction = Column(Float, default=0.0)
        recycling_rate = Column(Float, default=0.0)
        
        # Relationships
        product_id = Column(Integer, ForeignKey("products.id"))
        order_id = Column(Integer, ForeignKey("orders.id"))
        product = relationship("Product", back_populates="eco_metrics")
        order = relationship("Order", back_populates="eco_metrics")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    eco_packaging_opted = Column(Boolean, default=True)
    carbon_offset_contribution = Column(Float, default=0.0)
    
    eco_metrics = relationship("EcoMetrics", back_populates="order", uselist=False)
    product = relationship("Product")
class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    report_type = Column(String, nullable=False)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Report metrics
    total_products = Column(Integer, default=0)
    eco_certified_count = Column(Integer, default=0)
    average_sustainability_score = Column(Float, default=0.0)
    total_carbon_footprint = Column(Float, default=0.0)
    total_water_savings = Column(Float, default=0.0)
    
    # Relationships
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product = relationship("Product", backref="reports")
