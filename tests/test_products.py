import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.crud import crud_product
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.config import settings

# Initialize TestClient
client = TestClient(app, raise_server_exceptions=True)

def test_create_product(db: Session, test_admin_token_headers):
    """Test creating a new product."""
    data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 99.99,
        "stock": 100,
        "category": "electronics"
    }
    response = client.post(
        f"{settings.API_V1_STR}/products/",
        headers=test_admin_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["price"] == data["price"]
    assert content["stock"] == data["stock"]

def test_get_product(db: Session):
    """Test retrieving a product."""
    # Create a test product directly via the CRUD helper.
    product_in = ProductCreate(
        name="Test Product",
        description="A test product",
        price=99.99,
        stock=100,
        category="electronics"
    )
    product = crud_product.create(db, obj_in=product_in)
    
    response = client.get(f"{settings.API_V1_STR}/products/{product.id}")
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == product.id
    assert content["name"] == product_in.name

def test_list_products(db: Session):
    """Test listing all products."""
    # Create multiple test products via CRUD.
    for i in range(3):
        product_in = ProductCreate(
            name=f"Test Product {i}",
            description=f"A test product {i}",
            price=99.99,
            stock=100,
            category="electronics"
        )
        crud_product.create(db, obj_in=product_in)
    
    response = client.get(f"{settings.API_V1_STR}/products/")
    assert response.status_code == 200
    content = response.json()
    # Assert that at least 3 products exist in the response.
    assert len(content) >= 3

def test_update_product(db: Session, test_admin_token_headers):
    """Test updating a product."""
    # Create a test product first.
    product_in = ProductCreate(
        name="Test Product",
        description="A test product",
        price=99.99,
        stock=100,
        category="electronics"
    )
    product = crud_product.create(db, obj_in=product_in)
    
    update_data = {
        "price": 89.99,
        "stock": 50
    }
    response = client.put(
        f"{settings.API_V1_STR}/products/{product.id}",
        headers=test_admin_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["price"] == update_data["price"]
    assert content["stock"] == update_data["stock"]

def test_delete_product(db: Session, test_admin_token_headers):
    """Test deleting a product."""
    # Create a test product to delete.
    product_in = ProductCreate(
        name="Test Product",
        description="A test product",
        price=99.99,
        stock=100,
        category="electronics"
    )
    product = crud_product.create(db, obj_in=product_in)
    
    response = client.delete(
        f"{settings.API_V1_STR}/products/{product.id}",
        headers=test_admin_token_headers,
    )
    assert response.status_code == 200
    
    # Verify that the product has been deleted.
    response = client.get(f"{settings.API_V1_STR}/products/{product.id}")
    assert response.status_code == 404

def test_create_product_invalid_data(db: Session, test_admin_token_headers):
    """Test creating a product with invalid data."""
    data = {
        "name": "",           # Empty name should fail validation.
        "description": "A test product",
        "price": -10,         # Negative price should fail validation.
        "stock": -5,          # Negative stock should fail validation.
        "category": "electronics"
    }
    response = client.post(
        f"{settings.API_V1_STR}/products/",
        headers=test_admin_token_headers,
        json=data,
    )
    # Expecting a 422 Unprocessable Entity error due to validation issues.
    assert response.status_code == 422

def test_update_nonexistent_product(db: Session, test_admin_token_headers):
    """Test updating a non-existent product."""
    update_data = {
        "price": 89.99,
        "stock": 50
    }
    response = client.put(
        f"{settings.API_V1_STR}/products/99999",
        headers=test_admin_token_headers,
        json=update_data,
    )
    # Expect a 404 Not Found error for a non-existent product.
    assert response.status_code == 404

def test_search_products(db: Session):
    """Test searching products by name or category."""
    # Create test products.
    products = [
        ProductCreate(
            name="Gaming Laptop",
            description="A powerful gaming laptop",
            price=1299.99,
            stock=10,
            category="electronics"
        ),
        ProductCreate(
            name="Office Laptop",
            description="A business laptop",
            price=899.99,
            stock=20,
            category="electronics"
        ),
        ProductCreate(
            name="Gaming Mouse",
            description="A gaming mouse",
            price=49.99,
            stock=100,
            category="accessories"
        )
    ]
    for product_in in products:
        crud_product.create(db, obj_in=product_in)
    
    # Test searching by name (should match "Gaming Laptop" and "Gaming Mouse").
    response = client.get(f"{settings.API_V1_STR}/products/search?query=Gaming")
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 2
    
    # Test searching by category (should match "Gaming Mouse").
    response = client.get(f"{settings.API_V1_STR}/products/search?category=accessories")
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 1
