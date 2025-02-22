from typing import Dict
from app.models import Order, Product

class SustainabilityService:
    def calculate_order_impact(self, order: Order) -> Dict:
        """Calculate environmental impact metrics for an order"""
        total_carbon = 0
        recycled_materials = 0
        
        for item in order.items:
            total_carbon += item.product.carbon_footprint * item.quantity
            recycled_materials += item.product.recycled_content * item.quantity
            
        return {
            'carbon_footprint': total_carbon,
            'packaging_type': self._determine_packaging(order),
            'recycled_materials': recycled_materials
        }
    
    def get_sustainability_metrics(self) -> Dict:
        """Get overall sustainability metrics"""
        return {
            'total_carbon_saved': self._calculate_carbon_savings(),
            'recycling_rate': self._calculate_recycling_rate(),
            'eco_friendly_products_ratio': self._get_eco_products_ratio()
        }
    
    def get_recycling_statistics(self) -> Dict:
        """Get recycling impact statistics"""
        return {
            'materials_recycled': self._get_recycled_materials(),
            'packaging_saved': self._calculate_packaging_saved(),
            'water_saved': self._calculate_water_savings()
        }

    def _determine_packaging(self, order: Order) -> str:
        total_volume = sum(item.product.volume * item.quantity for item in order.items)
        if total_volume < 1000:
            return "recycled_small"
        elif total_volume < 5000:
            return "recycled_medium"
        return "recycled_large"

    def _calculate_carbon_savings(self) -> float:
        db = SessionLocal()
        try:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            result = db.query(func.sum(EcoMetrics.carbon_footprint))\
                      .filter(EcoMetrics.created_at >= thirty_days_ago)\
                      .scalar()
            return float(result or 0)
        finally:
            db.close()

    def _calculate_recycling_rate(self) -> float:
        db = SessionLocal()
        try:
            total_products = db.query(Product).count()
            recyclable_products = db.query(Product)\
                                 .filter(Product.is_recyclable == True)\
                                 .count()
            return (recyclable_products / total_products) * 100 if total_products > 0 else 0
        finally:
            db.close()

    def _get_eco_products_ratio(self) -> float:
        db = SessionLocal()
        try:
            total_products = db.query(Product).count()
            eco_products = db.query(Product)\
                          .filter(Product.eco_certified == True)\
                          .count()
            return (eco_products / total_products) * 100 if total_products > 0 else 0
        finally:
            db.close()

    def _get_recycled_materials(self) -> float:
        db = SessionLocal()
        try:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            result = db.query(func.sum(EcoMetrics.recycled_materials))\
                      .filter(EcoMetrics.created_at >= thirty_days_ago)\
                      .scalar()
            return float(result or 0)
        finally:
            db.close()

    def _calculate_packaging_saved(self) -> float:
        db = SessionLocal()
        try:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            orders = db.query(Order)\
                      .filter(Order.created_at >= thirty_days_ago)\
                      .all()
            return sum(2.5 if self._determine_packaging(order) == "recycled_small"
                      else 5.0 if self._determine_packaging(order) == "recycled_medium"
                      else 8.0 for order in orders)
        finally:
            db.close()

    def _calculate_water_savings(self) -> float:
        db = SessionLocal()
        try:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            orders = db.query(Order)\
                      .filter(Order.created_at >= thirty_days_ago)\
                      .all()
            return sum(
                sum(item.product.water_savings * item.quantity for item in order.items)
                for order in orders
            )
        finally:
            db.close()