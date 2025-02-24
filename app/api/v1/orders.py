from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.order import Order, OrderCreate, OrderUpdate
from app.crud.order import order as crud_order
from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.schemas.user import UserInDB

router = APIRouter()

@router.get("/", response_model=List[Order])
def read_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """Retrieve orders. Users can only see their own orders."""
    orders = crud_order.get_multi(db, customer_id=current_user.id, skip=skip, limit=limit)
    return orders

@router.post("/", response_model=Order)
def create_order(
    *,
    db: Session = Depends(get_db),
    order_in: OrderCreate,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """Create new order."""
    try:
        order = crud_order.create(db, obj_in=order_in, customer_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return order

@router.get("/{order_id}", response_model=Order)
def read_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """Get order by ID."""
    order = crud_order.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return order

@router.put("/{order_id}", response_model=Order)
def update_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    order_in: OrderUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """Update order status or shipping address."""
    order = crud_order.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    order = crud_order.update(db, db_obj=order, obj_in=order_in)
    return order

@router.post("/{order_id}/cancel", response_model=Order)
def cancel_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """Cancel an order. Only pending orders can be cancelled."""
    order = crud_order.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        order = crud_order.cancel_order(db, db_obj=order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return order