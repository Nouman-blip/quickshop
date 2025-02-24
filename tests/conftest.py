import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base_class import Base
from app.main import app
from app.core.config import settings

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    """Creates a test database session."""
    Base.metadata.create_all(bind=engine)  # Create tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Cleanup after tests

@pytest.fixture(scope="module")
def client():
    """Provides a test client."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_user_token_headers(client, db):
    """Registers a test user and returns authentication headers."""
    user_data = {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    # Register user (ignore failure if user exists)
    client.post("/api/v1/auth/register", json=user_data)
    
    # Login request must use form data
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    assert login_response.status_code == 200, "Login failed for test user"
    
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}

@pytest.fixture
def test_admin_token_headers(client, db):
    """Registers an admin user and returns authentication headers."""
    admin_data = {
        "email": "admin@example.com",
        "password": "adminpass123",
        "full_name": "Admin User",
        "is_admin": True
    }
    
    # Register admin (ignore failure if user exists)
    client.post("/api/v1/auth/register", json=admin_data)
    
    # Login request must use form data
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": admin_data["email"], "password": admin_data["password"]}
    )
    assert login_response.status_code == 200, "Login failed for admin user"
    
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}
