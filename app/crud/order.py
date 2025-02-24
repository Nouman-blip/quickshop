from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderUpdate

class CRUDOrder:
    def get(self, db: Session, id: int) -> Optional[Order]:
        return db.query(Order).filter(Order.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        customer_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        query = db.query(Order)
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        return query.offset(skip).limit(limit).all()

    def create(
        self,
        db: Session,
        *,
        obj_in: OrderCreate,
        customer_id: int
    ) -> Order:
        total_amount = 0.0
        # Create order first
        db_obj = Order(
            customer_id=customer_id,
            shipping_address=obj_in.shipping_address,
            status=OrderStatus.PENDING,
            total_amount=total_amount
        )
        db.add(db_obj)
        db.flush()

        # Create order items and calculate total
        for item in obj_in.items:
            product = db.query(Product).get(item.product_id)
            if not product or product.stock < item.quantity:
                db.rollback()
                raise ValueError(f"Product {item.product_id} not available in requested quantity")
            
            item_total = product.price * item.quantity
            order_item = OrderItem(
                order_id=db_obj.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price,
                total_price=item_total
            )
            total_amount += item_total
            
            # Update product stock
            product.stock -= item.quantity
            db.add(product)
            db.add(order_item)

        # Update order total
        db_obj.total_amount = total_amount
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Order,
        obj_in: OrderUpdate
    ) -> Order:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def cancel_order(
        self,
        db: Session,
        *,
        db_obj: Order
    ) -> Order:
        if db_obj.status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can be cancelled")
        
        # Restore product stock
        for item in db_obj.items:
            product = db.query(Product).get(item.product_id)
            if product:
                product.stock += item.quantity
                db.add(product)
        
        db_obj.status = OrderStatus.CANCELLED
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

order = CRUDOrder()