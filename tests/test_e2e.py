import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.config import settings

# Initialize TestClient with the correct parameter format
client = TestClient(app, raise_server_exceptions=True)

def test_complete_order_flow(db: Session, test_user_token_headers):
    """Test the complete order flow from product listing to order completion."""
    # 1. List available products
    response = client.get(f"{settings.API_V1_STR}/products/")
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0
    product_id = products[0]["id"]
    
    # 2. Create an order
    order_data = {
        "items": [{"product_id": product_id, "quantity": 1}],
        "shipping_address": "123 Test St, Test City"
    }
    response = client.post(
        f"{settings.API_V1_STR}/orders/",
        headers=test_user_token_headers,
        json=order_data
    )
    assert response.status_code == 200
    order = response.json()
    order_id = order["id"]
    
    # 3. Check order status
    response = client.get(
        f"{settings.API_V1_STR}/orders/{order_id}",
        headers=test_user_token_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    
    # 4. Get order notifications
    response = client.get(
        f"{settings.API_V1_STR}/notifications/order-updates/{order_id}",
        headers=test_user_token_headers
    )
    assert response.status_code == 200

def test_rate_limiting(db: Session):
    """Test rate limiting functionality."""
    # Make multiple requests in quick succession
    for _ in range(70):  # Exceeds the default 60 requests per minute
        client.get(f"{settings.API_V1_STR}/products/")
    
    # The next request should be rate limited
    response = client.get(f"{settings.API_V1_STR}/products/")
    assert response.status_code == 429
    assert "retry_after" in response.json()

def test_analytics_endpoints(db: Session, test_admin_token_headers):
    """Test analytics endpoints."""
    # Test dashboard metrics
    response = client.get(
        f"{settings.API_V1_STR}/analytics/dashboard",
        headers=test_admin_token_headers
    )
    assert response.status_code == 200
    metrics = response.json()
    assert "orders" in metrics
    assert "revenue" in metrics
    assert "inventory" in metrics
    
    # Test sales trends
    response = client.get(
        f"{settings.API_V1_STR}/analytics/sales-trends",
        headers=test_admin_token_headers
    )
    assert response.status_code == 200
    trends = response.json()
    assert isinstance(trends, list)
    
    # Test product performance
    response = client.get(
        f"{settings.API_V1_STR}/analytics/product-performance",
        headers=test_admin_token_headers
    )
    assert response.status_code == 200
    performance = response.json()
    assert isinstance(performance, list)

def test_concurrent_order_processing(db: Session, test_user_token_headers):
    """Test handling of concurrent orders."""
    # Create multiple orders concurrently
    order_data = {
        "items": [{"product_id": 1, "quantity": 1}],
        "shipping_address": "123 Test St, Test City"
    }
    
    responses = []
    for _ in range(5):
        response = client.post(
            f"{settings.API_V1_STR}/orders/",
            headers=test_user_token_headers,
            json=order_data
        )
        responses.append(response)
        time.sleep(0.1)  # Small delay to simulate concurrent requests
    
    # Verify all orders were processed successfully
    for response in responses:
        assert response.status_code == 200
        assert "id" in response.json()
