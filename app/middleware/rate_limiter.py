from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import time
from redis import Redis
from app.core.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client: Redis):
        super().__init__(app)
        self.limiter = RateLimiter(redis_client)

    async def dispatch(self, request: Request, call_next):
        is_limited, error_response = await self.limiter.is_rate_limited(request)
        if is_limited:
            return JSONResponse(status_code=429, content=error_response)
        return await call_next(request)

class RateLimiter:
    def __init__(
        self,
        redis_client: Redis,
        requests_per_minute: int = 60,
        burst_limit: int = 100,
        key_prefix: str = "ratelimit:"
    ):
        self.redis = redis_client
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.key_prefix = key_prefix

    async def _get_client_identifier(self, request: Request) -> str:
        # Use X-Forwarded-For header if behind a proxy, fallback to client host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host
        return f"{self.key_prefix}{client_ip}"

    async def is_rate_limited(self, request: Request) -> Tuple[bool, Optional[Dict]]:
        identifier = await self._get_client_identifier(request)
        current = int(time.time())
        minute_window = current - (current % 60)

        pipeline = self.redis.pipeline()
        pipeline.incr(f"{identifier}:{minute_window}")
        pipeline.expire(f"{identifier}:{minute_window}", 90)  # TTL slightly longer than window
        requests_in_window = pipeline.execute()[0]

        if requests_in_window > self.burst_limit:
            return True, {
                "error": "Too many requests",
                "detail": "Rate limit exceeded",
                "retry_after": 60 - (current % 60)
            }

        if requests_in_window > self.requests_per_minute:
            return True, {
                "error": "Too many requests",
                "detail": "Rate limit exceeded",
                "retry_after": 60 - (current % 60)
            }

        return False, None