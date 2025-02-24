from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.crud.product import product as crud_product
from app.api.deps import get_current_active_user, get_current_active_superuser
from app.db.session import get_db
from app.schemas.user import UserInDB

router = APIRouter()

@router.get("/", response_model=List[Product])
def read_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None
) -> Any:
    """Retrieve products with optional category filter."""
    products = crud_product.get_multi(db, skip=skip, limit=limit, category=category)
    return products

@router.post("/", response_model=Product)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """Create new product. Only authenticated users can create products."""
    product = crud_product.get_by_sku(db, sku=product_in.sku)
    if product:
        raise HTTPException(
            status_code=400,
            detail="The product with this SKU already exists."
        )
    product = crud_product.create(db, obj_in=product_in, seller_id=current_user.id)
    return product

@router.get("/{product_id}", response_model=Product)
def read_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Get product by ID."""
    product = crud_product.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """Update product. Only the seller or superuser can update the product."""
    product = crud_product.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.seller_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    product = crud_product.update(db, db_obj=product, obj_in=product_in)
    return product

@router.delete("/{product_id}", response_model=Product)
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """Delete product. Only the seller or superuser can delete the product."""
    product = crud_product.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.seller_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    product = crud_product.remove(db, id=product_id)
    return product