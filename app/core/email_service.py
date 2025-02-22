from typing import List
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self, smtp_host: str = "smtp.gmail.com", smtp_port: int = 587):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: str = "noreply@quickshop.com"
    ) -> bool:
        message = MIMEMultipart()
        message["From"] = from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        try:
            async with aiosmtplib.SMTP(hostname=self.smtp_host, port=self.smtp_port) as smtp:
                await smtp.send_message(message)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    async def send_bulk_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        from_email: str = "noreply@quickshop.com"
    ) -> dict:
        results = {
            "success": [],
            "failed": []
        }
        
        for email in to_emails:
            success = await self.send_email(email, subject, body, from_email)
            if success:
                results["success"].append(email)
            else:
                results["failed"].append(email)
        
        return results