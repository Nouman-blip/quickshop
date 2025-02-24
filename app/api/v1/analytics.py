from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func
from app.db.session import get_db
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get key metrics for the dashboard."""
    now = datetime.utcnow()
    last_30_days = now - timedelta(days=30)
    
    # Orders metrics
    total_orders = db.query(Order).count()
    recent_orders = db.query(Order).filter(Order.created_at >= last_30_days).count()
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    
    # Revenue metrics
    total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0.0
    recent_revenue = db.query(func.sum(Order.total_amount)).\
        filter(Order.created_at >= last_30_days).scalar() or 0.0
    
    # Inventory metrics
    low_stock_products = db.query(Product).filter(Product.stock < 10).count()
    
    return {
        "orders": {
            "total": total_orders,
            "recent": recent_orders,
            "pending": pending_orders
        },
        "revenue": {
            "total": float(total_revenue),
            "recent": float(recent_revenue),
            "average_order_value": float(total_revenue / total_orders) if total_orders > 0 else 0.0
        },
        "inventory": {
            "low_stock_count": low_stock_products
        }
    }

@router.get("/sales-trends", response_model=List[Dict[str, Any]])
async def get_sales_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get daily sales trends for specified number of days."""
    if days > 90:
        raise HTTPException(status_code=400, detail="Cannot fetch data for more than 90 days")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    daily_sales = db.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('order_count'),
        func.sum(Order.total_amount).label('revenue')
    ).filter(
        Order.created_at >= start_date
    ).group_by(
        func.date(Order.created_at)
    ).all()
    
    return [
        {
            "date": sale.date.isoformat(),
            "order_count": sale.order_count,
            "revenue": float(sale.revenue or 0)
        }
        for sale in daily_sales
    ]

@router.get("/product-performance", response_model=List[Dict[str, Any]])
async def get_product_performance(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get performance metrics for top-selling products."""
    from app.models.order_item import OrderItem
    
    top_products = db.query(
        Product.id,
        Product.name,
        func.sum(OrderItem.quantity).label('units_sold'),
        func.sum(OrderItem.total_price).label('revenue')
    ).join(
        OrderItem
    ).group_by(
        Product.id,
        Product.name
    ).order_by(
        func.sum(OrderItem.total_price).desc()
    ).limit(limit).all()
    
    return [
        {
            "product_id": product.id,
            "product_name": product.name,
            "units_sold": product.units_sold,
            "revenue": float(product.revenue or 0)
        }
        for product in top_products
    ]