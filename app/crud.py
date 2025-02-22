from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from . import models, schemas
from app.tasks import notify_low_stock, update_product_analytics
from typing import List, Optional
from datetime import datetime

# Async product retrieval with caching
def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    cache_key: Optional[str] = None
) -> List[models.Product]:
    if cache_key:
        # Redis cache implementation would go here
        pass
    return db.query(models.Product)\
             .offset(skip)\
             .limit(limit)\
             .all()

def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    return db.query(models.Product)\
             .filter(models.Product.id == product_id)\
             .first()

def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    db_product = models.Product(
        **product.dict(),
        created_at=datetime.utcnow(),
        last_updated=datetime.utcnow()
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Trigger async analytics update
    update_product_analytics.delay(db_product.id)
    return db_product

def update_product(
    db: Session,
    product_id: int,
    product: schemas.ProductCreate
) -> Optional[models.Product]:
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product.dict(exclude_unset=True)
        update_data['last_updated'] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(db_product, key, value)
            
        # Check stock levels after update
        if db_product.stock <= db_product.stock_threshold:
            notify_low_stock.delay(product_id)
            
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int) -> bool:
    db_product = get_product(db, product_id)
    if db_product:
        db_product.is_active = False  # Soft delete
        db_product.last_updated = datetime.utcnow()
        db.commit()
        return True
    return False

def get_products_by_category(
    db: Session,
    category_id: int,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False
) -> List[models.Product]:
    query = db.query(models.Product)\
             .filter(models.Product.category_id == category_id)
    
    if not include_inactive:
        query = query.filter(models.Product.is_active == True)
    
    return query.offset(skip).limit(limit).all()

def search_products(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 100,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[models.Product]:
    search = f"%{query}%"
    filters = [
        models.Product.is_active == True,
        or_(
            models.Product.name.ilike(search),
            models.Product.description.ilike(search)
        )
    ]
    
    if min_price is not None:
        filters.append(models.Product.price >= min_price)
    if max_price is not None:
        filters.append(models.Product.price <= max_price)
        
    return db.query(models.Product)\
             .filter(and_(*filters))\
             .offset(skip)\
             .limit(limit)\
             .all()
def get_eco_certified_products(
    db: Session,
    min_score: float = 50.0,
    skip: int = 0,
    limit: int = 100
) -> List[models.Product]:
    return db.query(models.Product)\
             .filter(
                 models.Product.eco_certified == True,
                 models.Product.sustainability_score >= min_score
             )\
             .offset(skip)\
             .limit(limit)\
             .all()

def get_locally_sourced_products(
    db: Session,
    region: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Product]:
    query = db.query(models.Product)\
             .filter(models.Product.locally_sourced == True)
    
    if region:
        query = query.filter(models.Product.source_region == region)
    
    return query.offset(skip).limit(limit).all()

def get_sustainable_products(
    db: Session,
    min_score: float = 70.0,
    eco_certified: Optional[bool] = None,
    biodegradable: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Product]:
    filters = [models.Product.sustainability_score >= min_score]
    
    if eco_certified is not None:
        filters.append(models.Product.eco_certified == eco_certified)
    if biodegradable is not None:
        filters.append(models.Product.biodegradable == biodegradable)
    
    return db.query(models.Product)\
             .filter(*filters)\
             .offset(skip)\
             .limit(limit)\
             .all()

def get_product_impact(db: Session, product_id: int) -> Optional[Dict]:
    product = db.query(models.Product).get(product_id)
    if not product:
        return None
    
    return {
        "carbon_footprint": product.carbon_footprint,
        "water_savings": product.water_savings,
        "recycled_content": product.recycled_content,
        "sustainability_score": product.sustainability_score,
        "eco_certifications": product.eco_certifications,
        "renewable_materials": product.renewable_materials_percentage
    }