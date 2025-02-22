from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.database import SessionLocal, engine
from app.routers import users, products, orders, cart
from app.core import security, config

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="QuickShop API",
    description="E-commerce REST API built with FastAPI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(
    users.router,
    prefix="/api/users",
    tags=["users"]
)

app.include_router(
    products.router,
    prefix="/api/products",
    tags=["products"]
)

app.include_router(
    orders.router,
    prefix="/api/orders",
    tags=["orders"]
)

app.include_router(
    cart.router,
    prefix="/api/cart",
    tags=["cart"]
)

@app.get("/")
async def root():
    """
    Root endpoint to check API status
    """
    return {
        "status": "online",
        "message": "Welcome to QuickShop API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.utcnow()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)