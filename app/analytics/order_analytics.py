from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Dict, List, Tuple

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product

class OrderAnalytics:
    """Analytics service for order-related metrics and insights"""

    def __init__(self, db: Session):
        self.db = db

    def get_order_volume_by_status(self) -> Dict[str, int]:
        """Get the count of orders grouped by their current status"""
        results = (
            self.db.query(Order.status, func.count(Order.id))
            .group_by(Order.status)
            .all()
        )
        return {status.value: count for status, count in results}

    def get_daily_revenue(self, days: int = 30) -> List[Tuple[datetime, float]]:
        """Get daily revenue for the specified number of past days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        results = (
            self.db.query(
                func.date_trunc('day', Order.created_at).label('day'),
                func.sum(Order.total_amount).label('revenue')
            )
            .filter(Order.created_at >= start_date)
            .filter(Order.status != OrderStatus.CANCELLED)
            .group_by('day')
            .order_by('day')
            .all()
        )
        return [(day, float(revenue or 0)) for day, revenue in results]

    def get_top_selling_products(self, limit: int = 10) -> List[Dict]:
        """Get the top selling products based on order quantity"""
        results = (
            self.db.query(
                Product.id,
                Product.name,
                func.sum(OrderItem.quantity).label('total_quantity'),
                func.sum(OrderItem.total_price).label('total_revenue')
            )
            .join(OrderItem)
            .join(Order)
            .filter(Order.status != OrderStatus.CANCELLED)
            .group_by(Product.id, Product.name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
            .all()
        )
        return [
            {
                'product_id': r.id,
                'product_name': r.name,
                'total_quantity': int(r.total_quantity),
                'total_revenue': float(r.total_revenue)
            }
            for r in results
        ]

    def get_order_processing_metrics(self) -> Dict:
        """Get metrics about order processing times and efficiency"""
        processing_times = (
            self.db.query(
                func.avg(Order.updated_at - Order.created_at),
                func.min(Order.updated_at - Order.created_at),
                func.max(Order.updated_at - Order.created_at)
            )
            .filter(Order.status == OrderStatus.DELIVERED)
            .first()
        )
        
        return {
            'avg_processing_time': processing_times[0],
            'min_processing_time': processing_times[1],
            'max_processing_time': processing_times[2],
            'orders_in_processing': self.db.query(Order)
                .filter(Order.status == OrderStatus.PROCESSING)
                .count()
        }