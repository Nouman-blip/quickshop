from celery import shared_task
from typing import Dict
from fastapi_mail import FastMail, MessageSchema
from app.core.config import settings

class MultiChannelNotification:
    def send_eco_friendly_confirmation(
        self,
        user_email: str,
        order_data: Dict,
        eco_impact: Dict
    ) -> bool:
        """Send eco-friendly order confirmation via multiple channels"""
        email_sent = self._send_email(user_email, order_data, eco_impact)
        sms_sent = self._send_sms(order_data['phone'], order_data, eco_impact)
        
        return email_sent and sms_sent
    
    def _send_email(self, email: str, order_data: Dict, eco_impact: Dict) -> bool:
        template = self._get_eco_template('order_confirmation')
        content = template.render(
            order_data=order_data,
            eco_impact=eco_impact,
            eco_tips=self._get_eco_tips()
        )
        
        message = MessageSchema(
            subject=f"Your Eco-Friendly Order #{order_data['order_id']}",
            recipients=[email],
            body=content,
            subtype="html"
        )
        
        mailer = FastMail(settings.MAIL_CONFIG)
        return mailer.send_message(message)

@shared_task
def send_email(to_email: str, subject: str, message: str):
    """Send email notifications"""
    message = MessageSchema(
        subject=subject,
        recipients=[to_email],
        body=message,
        subtype="html"
    )
    fm = FastMail(settings.MAIL_CONFIG)
    fm.send_message(message)

@shared_task
def send_push_notification(user_id: str, message: str):
    """Send push notifications"""
    # Implementation with your preferred push notification service
    pass