from typing import List, Optional, Union
from sqlalchemy.orm import Session
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentUpdate

class CRUDPayment:
    def create(self, db: Session, *, obj_in: PaymentCreate) -> Payment:
        """Create a new payment record"""
        db_obj = Payment(
            order_id=obj_in.order_id,
            amount=obj_in.amount,
            payment_method=obj_in.payment_method,
            payment_details=obj_in.payment_details
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Payment, obj_in: Union[PaymentUpdate, dict]) -> Payment:
        """Update an existing payment record"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[Payment]:
        """Get a payment by ID"""
        return db.query(Payment).filter(Payment.id == id).first()

    def get_by_order_id(self, db: Session, order_id: int) -> List[Payment]:
        """Get all payments for a specific order"""
        return db.query(Payment).filter(Payment.order_id == order_id).all()

    def get_by_status(self, db: Session, status: PaymentStatus) -> List[Payment]:
        """Get all payments with a specific status"""
        return db.query(Payment).filter(Payment.status == status).all()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Get multiple payments with pagination"""
        return db.query(Payment).offset(skip).limit(limit).all()

payment = CRUDPayment()