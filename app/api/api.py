from fastapi import APIRouter

api_router = APIRouter()

# Import and include other routers
# Example:
# from app.api.v1.endpoints import users, products, orders
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(products.router, prefix="/products", tags=["products"])
# api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
