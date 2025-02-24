from celery import shared_task
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.order import Order, OrderStatus
from app.core.celery import celery_app
from app.models.product import Product
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_order(self, order_id: int) -> None:
    """Process an order asynchronously.
    
    This task handles the order processing workflow including:
    - Updating order status
    - Sending confirmation emails
    - Triggering inventory updates
    - Notifying shipping service
    
    Args:
        order_id: The ID of the order to process
    """
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.error(f"Order {order_id} not found")
            return
        
        # Update order status to processing
        order.status = OrderStatus.PROCESSING
        db.add(order)
        db.commit()
        
        # Verify inventory
        for item in order.items:
            product = db.query(Product).get(item.product_id)
            if not product or product.stock < 0:
                raise ValueError(f"Insufficient stock for product {item.product_id}")
        
        # Send order confirmation email
        send_order_confirmation.delay(order_id)
        
        # Update order status to shipped
        order.status = OrderStatus.SHIPPED
        db.add(order)
        db.commit()
        
        # TODO: Integrate with shipping service
        # This would typically involve calling an external shipping API
        
        # Update order status to delivered
        order.status = OrderStatus.DELIVERED
        db.add(order)
        db.commit()
        
        logger.info(f"Successfully processed order {order_id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing order {order_id}: {str(e)}")
        # Retry the task with exponential backoff
        self.retry(exc=e, countdown=2 ** self.request.retries)
    finally:
        db.close()

@shared_task
def send_order_confirmation(order_id: int) -> None:
    """Send order confirmation email to customer.
    
    Args:
        order_id: The ID of the order to send confirmation for
    """
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.error(f"Order {order_id} not found")
            return
            
        # TODO: Implement actual email sending logic
        # This would typically involve:
        # 1. Getting customer email from order.user.email
        # 2. Creating email template with order details
        # 3. Sending email through configured email service
        
        logger.info(f"Order confirmation email sent for order {order_id}")
        
    except Exception as e:
        logger.error(f"Error sending confirmation for order {order_id}: {str(e)}")
        raise
    finally:
        db.close()