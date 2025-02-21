# app/routes/orders.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Order as OrderModel
from app.schemas import Order, OrderCreate
from app.tasks import process_order_task

router = APIRouter()

@router.post("/", response_model=Order)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    new_order = OrderModel(**order.dict(), status="pending")
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    # Enqueue background task for order processing
    process_order_task.delay(new_order.id, order.dict())
    return new_order

@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(f"SELECT * FROM orders WHERE id = {order_id}")
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
