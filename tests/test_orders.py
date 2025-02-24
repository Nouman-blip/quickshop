import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.config import settings
from app.models.order import OrderStatus
from app.schemas.order import OrderCreate, OrderItemCreate
from app.crud import crud_order

# Initialize TestClient
client = TestClient(app, raise_server_exceptions=True)

def test_create_order(db: Session, test_user_token_headers):
    """Test creating a new order."""
    data = {
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1}
        ],
        "shipping_address": "123 Test St, Test City"
    }
    response = client.post(
        f"{settings.API_V1_STR}/orders/",
        headers=test_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["shipping_address"] == data["shipping_address"]
    assert len(content["items"]) == 2

def test_cancel_order(db: Session, test_user_token_headers):
    """Test cancelling an order."""
    # First, create an order using your CRUD helper
    order_in = OrderCreate(
        items=[OrderItemCreate(product_id=1, quantity=1)],
        shipping_address="123 Test St"
    )
    order = crud_order.create(db, obj_in=order_in, customer_id=1)
    
    # Cancel the order via the API endpoint
    response = client.post(
        f"{settings.API_V1_STR}/orders/{order.id}/cancel",
        headers=test_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    # Verify the order status is updated to "cancelled"
    assert content["status"] == "cancelled"

def test_get_order(db: Session, test_user_token_headers):
    """Test retrieving an order."""
    # Create a test order using your CRUD helper
    order_in = OrderCreate(
        items=[OrderItemCreate(product_id=1, quantity=1)],
        shipping_address="123 Test St"
    )
    order = crud_order.create(db, obj_in=order_in, customer_id=1)
    
    response = client.get(
        f"{settings.API_V1_STR}/orders/{order.id}",
        headers=test_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == order.id
    assert content["shipping_address"] == order_in.shipping_address

def test_list_user_orders(db: Session, test_user_token_headers):
    """Test listing all orders for a user."""
    # Create multiple test orders
    for _ in range(3):
        order_in = OrderCreate(
            items=[OrderItemCreate(product_id=1, quantity=1)],
            shipping_address="123 Test St"
        )
        crud_order.create(db, obj_in=order_in, customer_id=1)
    
    response = client.get(
        f"{settings.API_V1_STR}/orders/",
        headers=test_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    # We expect at least the orders we just created to be returned
    assert len(content) >= 3

def test_create_order_with_invalid_product(db: Session, test_user_token_headers):
    """Test creating an order with a non-existent product."""
    data = {
        "items": [
            {"product_id": 99999, "quantity": 1}  # Non-existent product
        ],
        "shipping_address": "123 Test St"
    }
    response = client.post(
        f"{settings.API_V1_STR}/orders/",
        headers=test_user_token_headers,
        json=data,
    )
    # Expecting a 400 error due to invalid product
    assert response.status_code == 400

def test_create_order_with_insufficient_stock(db: Session, test_user_token_headers):
    """Test creating an order with a quantity exceeding available stock."""
    data = {
        "items": [
            {"product_id": 1, "quantity": 99999}  # Quantity exceeding available stock
        ],
        "shipping_address": "123 Test St"
    }
    response = client.post(
        f"{settings.API_V1_STR}/orders/",
        headers=test_user_token_headers,
        json=data,
    )
    # Expecting a 400 error because stock is insufficient
    assert response.status_code == 400

def test_cancel_non_pending_order(db: Session, test_user_token_headers):
    """Test cancelling an order that is not in a pending status."""
    # Create an order and update its status to something other than pending (e.g., PROCESSING)
    order_in = OrderCreate(
        items=[OrderItemCreate(product_id=1, quantity=1)],
        shipping_address="123 Test St"
    )
    order = crud_order.create(db, obj_in=order_in, customer_id=1)
    order.status = OrderStatus.PROCESSING
    db.add(order)
    db.commit()
    
    # Attempt to cancel an order that's already in processing status
    response = client.post(
        f"{settings.API_V1_STR}/orders/{order.id}/cancel",
        headers=test_user_token_headers,
    )
    # Expecting a 400 error because cancellation is not allowed
    assert response.status_code == 400

def test_get_nonexistent_order(db: Session, test_user_token_headers):
    """Test retrieving a non-existent order."""
    response = client.get(
        f"{settings.API_V1_STR}/orders/99999",
        headers=test_user_token_headers,
    )
    # Expecting a 404 not found error
    assert response.status_code == 404
