from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.get("/metrics/{order_id}", response_model=schemas.EcoMetrics)
def get_order_eco_metrics(order_id: int, db: Session = Depends(get_db)):
    metrics = crud.get_eco_metrics(db, order_id=order_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Eco metrics not found")
    return metrics

@router.get("/sustainability/products", response_model=List[schemas.Product])
def get_sustainable_products(
    min_score: float = 50.0,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_products_by_sustainability(db, min_score, skip, limit)

@router.get("/impact/summary", response_model=dict)
def get_environmental_impact(db: Session = Depends(get_db)):
    return crud.get_total_environmental_impact(db)