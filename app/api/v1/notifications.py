from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.session import get_db
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.core.auth import get_current_user
from datetime import datetime

router = APIRouter()

@router.get("/order-updates/{order_id}", response_model=List[Dict[str, Any]])
async def get_order_updates(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get all status updates for a specific order."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    # TODO: Implement order history tracking
    # For now, return current status
    return [{
        "timestamp": order.updated_at.isoformat(),
        "status": order.status.value,
        "message": f"Order is {order.status.value}"
    }]

@router.get("/user-notifications", response_model=List[Dict[str, Any]])
async def get_user_notifications(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get all notifications for the current user."""
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(
        Order.updated_at.desc()
    ).offset(skip).limit(limit).all()
    
    notifications = []
    for order in orders:
        notification = {
            "id": f"order_{order.id}",
            "type": "order_update",
            "timestamp": order.updated_at.isoformat(),
            "read": True,  # TODO: Implement notification read status
            "data": {
                "order_id": order.id,
                "order_number": order.order_number,
                "status": order.status.value,
                "message": f"Order #{order.order_number} is {order.status.value}"
            }
        }
        notifications.append(notification)
    
    return notifications

@router.post("/subscribe", response_model=Dict[str, Any])
async def subscribe_to_notifications(
    notification_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Subscribe to specific types of notifications."""
    valid_types = ["order_updates", "promotions", "inventory_alerts"]
    if notification_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid notification type. Must be one of: {', '.join(valid_types)}"
        )
    
    # TODO: Implement notification preferences storage
    return {
        "status": "success",
        "message": f"Successfully subscribed to {notification_type}",
        "subscription": {
            "user_id": current_user.id,
            "type": notification_type,
            "created_at": datetime.utcnow().isoformat()
        }
    }