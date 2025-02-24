from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api import api_router
from redis import Redis
from app.middleware.rate_limiter import RateLimitMiddleware
from app.core.load_balancer import LoadBalancer

# Initialize Redis client
redis_client = Redis.from_url(settings.REDIS_URL)

# Initialize Load Balancer
load_balancer = LoadBalancer()

app = FastAPI(
    title="QuickShop API",
    description="A modern e-commerce platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Add Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware, redis_client=redis_client)

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to QuickShop API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)