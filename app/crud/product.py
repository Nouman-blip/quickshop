from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.celery import celery_app
import json

class CRUDProduct:
    def get(self, db: Session, id: int) -> Optional[Product]:
        # Try to get product from Redis cache first
        redis = celery_app.backend.client
        cache_key = f"product:{id}"
        cached_product = redis.get(cache_key)
        
        if cached_product:
            product_data = json.loads(cached_product)
            return Product(**product_data)
        
        # If not in cache, get from database and cache it
        product = db.query(Product).filter(Product.id == id).first()
        if product:
            redis.setex(
                cache_key,
                3600,  # Cache for 1 hour
                json.dumps({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': product.price,
                    'stock': product.stock
                })
            )
        return product

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        return db.query(Product).offset(skip).limit(limit).all()

    def create(
        self,
        db: Session,
        *,
        obj_in: ProductCreate
    ) -> Product:
        db_obj = Product(
            name=obj_in.name,
            description=obj_in.description,
            price=obj_in.price,
            stock=obj_in.stock
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Product,
        obj_in: ProductUpdate
    ) -> Product:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Invalidate cache
        redis = celery_app.backend.client
        redis.delete(f"product:{db_obj.id}")
        
        return db_obj

product = CRUDProduct()