
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Product as ProductModel
from app.schemas import Product, ProductCreate

router = APIRouter()

@router.post("/", response_model=Product)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    new_product = ProductModel(**product.dict())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

@router.get("/", response_model=list[Product])
async def list_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute("SELECT * FROM products")
    products = result.scalars().all()
    return products
