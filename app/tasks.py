from celery import Celery
from typing import Dict, List
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.email_service import EmailService
from app.core.payment_gateway import PaymentGateway
from app.database import SessionLocal
from app.models import Order, Product, Report, EcoMetrics
from app.core.analytics import AnalyticsService
from app.core.sustainability import SustainabilityService
from app.core.notifications import MultiChannelNotification

celery = Celery('quickshop', broker='redis://localhost:6379/0')

@celery.task(bind=True, max_retries=3)
def send_order_confirmation(self, order_data: Dict, user_email: str) -> bool:
    """
    Send eco-friendly order confirmation to the user asynchronously.
    """
    try:
        # Calculate eco impact before sending confirmation
        eco_impact = calculate_eco_impact.delay(order_data['order_id']).get()
        order_data['eco_impact'] = eco_impact
        
        # Use multi-channel notification for better customer engagement
        notifications = MultiChannelNotification()
        return notifications.send_eco_friendly_confirmation(
            user_email=user_email,
            order_data=order_data,
            eco_impact=eco_impact
        )
    except Exception as e:
        self.retry(exc=e, countdown=60 * 5)
        return False
    """
    Send order confirmation email to the user asynchronously.

    Args:
        order_data (Dict): Dictionary containing order details including:
            - order_id: Unique identifier for the order
            - items: List of ordered items
            - total_amount: Total cost of the order
            - created_at: Timestamp of order creation
        user_email (str): Email address of the recipient

    Returns:
        bool: True if email was sent successfully, False otherwise

    Raises:
        SMTPException: If there's an error in sending the email
    """
    try:
        email_service = EmailService()
        template = email_service.get_template('order_confirmation')
        email_content = template.render(order_data)
        
        return email_service.send(
            to_email=user_email,
            subject=f"Order Confirmation #{order_data['order_id']}",
            content=email_content
        )
    except Exception as e:
        self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes
        return False

@celery.task(bind=True, max_retries=3)
def update_inventory(self, product_updates: List[Dict]) -> bool:
    """
    Update product inventory levels after order completion.

    Args:
        product_updates (List[Dict]): List of dictionaries containing:
            - product_id: ID of the product
            - quantity: Quantity to subtract from inventory

    Returns:
        bool: True if all updates were successful, False otherwise

    Raises:
        ValueError: If invalid product data is provided
    """
    db = SessionLocal()
    try:
        for update in product_updates:
            product = db.query(Product).get(update['product_id'])
            if product:
                if product.stock >= update['quantity']:
                    product.stock -= update['quantity']
                    if product.stock <= product.stock_threshold:
                        notify_low_stock.delay(product.id)
                else:
                    raise ValueError(f"Insufficient stock for product {product.id}")
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        self.retry(exc=e, countdown=30)
        return False
    finally:
        db.close()

@celery.task(bind=True, max_retries=2)
def process_payment(self, order_id: int, payment_data: Dict, amount: float) -> Dict:
    """
    Process payment for an order asynchronously.

    Args:
        order_id (int): The ID of the order being processed
        payment_data (Dict): Payment information including:
            - payment_method: Method of payment
            - card_info: Encrypted payment card information
        amount (float): The amount to be charged

    Returns:
        Dict: Dictionary containing:
            - success: Boolean indicating if payment was successful
            - transaction_id: ID of the payment transaction
            - error_message: Error message if payment failed

    Raises:
        PaymentProcessingError: If payment processing fails
    """
    try:
        payment_gateway = PaymentGateway()
        result = payment_gateway.process_payment(
            amount=amount,
            payment_data=payment_data
        )
        
        if result['success']:
            update_order_status.delay(order_id, 'paid')
        
        return result
    except Exception as e:
        self.retry(exc=e, countdown=60)
        return {
            "success": False,
            "transaction_id": None,
            "error_message": str(e)
        }

@celery.task
def generate_periodic_reports() -> bool:
    """
    Generate comprehensive eco-friendly business analytics reports.
    """
    db = SessionLocal()
    try:
        analytics = AnalyticsService()
        sustainability = SustainabilityService()
        
        report_data = {
            'sales_metrics': analytics.generate_daily_report(),
            'eco_metrics': sustainability.get_sustainability_metrics(),
            'recycling_impact': sustainability.get_recycling_statistics(),
            'carbon_offset': sustainability.calculate_total_carbon_offset()
        }
        
        new_report = Report(
            data=report_data,
            generated_at=datetime.utcnow(),
            report_type='eco_friendly'
        )
        db.add(new_report)
        db.commit()
        
        # Send report to administrators
        send_report_notification.delay(report_data)
        return True
    except Exception as e:
        db.rollback()
        celery.logger.error(f"Failed to generate eco-friendly reports: {str(e)}")
        return False
    finally:
        db.close()
@celery.task
def notify_low_stock(product_id: int) -> None:
    """
    Send notifications when product stock is low.
    """
    db = SessionLocal()
    try:
        product = db.query(Product).get(product_id)
        if product:
            send_order_confirmation.delay(
                {"product": product.name, "stock": product.stock},
                "inventory@quickshop.com"
            )
    finally:
        db.close()

@celery.task
def update_order_status(order_id: int, status: str) -> bool:
    """
    Update order status and notify customer.
    """
    db = SessionLocal()
    try:
        order = db.query(Order).get(order_id)
        if order:
            order.status = status
            db.commit()
            send_status_update.delay(order.user_email, order_id, status)
            return True
        return False
    finally:
        db.close()
@celery.task
def calculate_eco_impact(order_id: int) -> Dict:
    """Calculate environmental impact of an order"""
    db = SessionLocal()
    try:
        order = db.query(Order).get(order_id)
        if order:
            sustainability = SustainabilityService()
            impact = sustainability.calculate_order_impact(order)
            
            eco_metrics = EcoMetrics(
                order_id=order_id,
                carbon_footprint=impact['carbon_footprint'],
                packaging_type=impact['packaging_type'],
                recycled_materials=impact['recycled_materials']
            )
            db.add(eco_metrics)
            db.commit()
            return impact
    finally:
        db.close()

@celery.task
def generate_sustainability_report() -> bool:
    """Generate eco-friendly metrics report"""
    db = SessionLocal()
    try:
        analytics = AnalyticsService()
        report_data = {
            'standard_metrics': analytics.generate_daily_report(),
            'eco_metrics': analytics.get_sustainability_metrics(),
            'recycling_impact': analytics.get_recycling_statistics()
        }
        
        new_report = Report(
            data=report_data,
            generated_at=datetime.utcnow()
        )
        db.add(new_report)
        db.commit()
        
        # Send report to administrators
        send_report_notification.delay(report_data)
        return True
    except Exception as e:
        db.rollback()
        celery.logger.error(f"Failed to generate reports: {str(e)}")
        return False
    finally:
        db.close()