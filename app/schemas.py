from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal
from enum import Enum

class PackagingType(str, Enum):
    MINIMAL = "minimal"
    RECYCLED = "recycled"
    BIODEGRADABLE = "biodegradable"
    REUSABLE = "reusable"

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class EcoMetricsBase(BaseModel):
    carbon_footprint: float = Field(..., ge=0)
    packaging_type: PackagingType
    recycled_materials: float = Field(..., ge=0)
    water_savings: float = Field(..., ge=0)
    energy_savings: float = Field(default=0.0, ge=0)
    trees_saved: float = Field(default=0.0, ge=0)
    biodegradability_index: float = Field(default=0.0, ge=0, le=100)

class EcoMetricsCreate(EcoMetricsBase):
    order_id: int

class EcoMetrics(EcoMetricsBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    carbon_footprint: float = Field(default=0.0, ge=0)
    recycled_content: float = Field(default=0.0, ge=0, le=100)
    is_recyclable: bool = False
    eco_certified: bool = False
    water_savings: float = Field(default=0.0, ge=0)
    volume: Optional[float] = Field(None, gt=0)
    packaging_type: PackagingType = PackagingType.MINIMAL
    sustainability_score: float = Field(default=0.0, ge=0, le=100)
    eco_certifications: Optional[List[str]] = []
    renewable_materials_percentage: float = Field(default=0.0, ge=0, le=100)
    biodegradable: bool = False
    locally_sourced: bool = False

    @validator('sustainability_score')
    def calculate_sustainability_score(cls, v, values):
        if v == 0.0:
            score = 0
            if values.get('eco_certified'): score += 30
            if values.get('is_recyclable'): score += 20
            if values.get('biodegradable'): score += 25
            if values.get('locally_sourced'): score += 25
            return float(score)
        return v

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    eco_metrics: Optional[EcoMetrics]

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    product_id: int
    customer_name: str
    amount: Decimal = Field(..., gt=0)
    eco_packaging_opted: bool = True
    carbon_offset_contribution: float = Field(default=0.0, ge=0)

    @validator('carbon_offset_contribution')
    def calculate_offset(cls, v, values):
        if v == 0.0 and 'amount' in values:
            return float(values['amount']) * 0.05  # 5% carbon offset
        return v

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    status: str
    created_at: datetime
    eco_metrics: Optional[EcoMetrics]
    product: Product

    class Config:
        orm_mode = True

class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)
    eco_packaging: bool = True

class Cart(BaseModel):
    items: List[CartItem]
    total_amount: Decimal
    total_carbon_offset: float
    eco_savings: Dict[str, float]

    @validator('total_carbon_offset', pre=True)
    def calculate_total_offset(cls, v, values):
        if 'total_amount' in values:
            return float(values['total_amount']) * 0.05
        return 0.0