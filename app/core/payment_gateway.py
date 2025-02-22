from decimal import Decimal
from typing import Dict, Optional
import aiohttp

class PaymentGateway:
    def __init__(self, api_key: str = "test_key", base_url: str = "https://api.payment.test"):
        self.api_key = api_key
        self.base_url = base_url

    async def process_payment(
        self,
        amount: Decimal,
        currency: str = "USD",
        payment_method: str = "card",
        metadata: Optional[Dict] = None
    ) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "amount": float(amount),
                    "currency": currency,
                    "payment_method": payment_method,
                    "metadata": metadata or {}
                }
                
                async with session.post(
                    f"{self.base_url}/v1/payments",
                    json=payload,
                    headers=headers
                ) as response:
                    return await response.json()
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }

    async def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {"payment_id": payment_id}
                if amount:
                    payload["amount"] = float(amount)
                
                async with session.post(
                    f"{self.base_url}/v1/refunds",
                    json=payload,
                    headers=headers
                ) as response:
                    return await response.json()
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }