"""Middleware for authentication, rate limiting, response caching, and request tracking."""

import hashlib
import hmac
import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from cachetools import TTLCache

from app.config import get_settings

logger = logging.getLogger("dataforge")


class RapidAPIAuthMiddleware(BaseHTTPMiddleware):
    """Verify requests come from RapidAPI proxy or have a valid API key."""

    EXEMPT_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        settings = get_settings()

        # Check RapidAPI proxy secret
        rapid_secret = request.headers.get("X-RapidAPI-Proxy-Secret", "")
        if settings.rapidapi_proxy_secret and hmac.compare_digest(rapid_secret, settings.rapidapi_proxy_secret):
            return await call_next(request)

        # Check direct API key
        api_key = request.headers.get("X-API-Key", "")
        if settings.api_key and hmac.compare_digest(api_key, settings.api_key):
            return await call_next(request)

        logger.warning("Unauthorized request: %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized", "detail": "Valid API key required"},
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter per API key / IP.

    Limits are per-minute windows. Default: 120 req/min for free tier.
    """

    EXEMPT_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json"}

    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.rpm = requests_per_minute
        # key -> (count, window_start) — auto-expires after 2 minutes to prevent memory leak
        self._buckets: TTLCache = TTLCache(maxsize=100_000, ttl=120)

    def _get_client_key(self, request: Request) -> str:
        """Identify client by RapidAPI user or API key or IP."""
        rapid_user = request.headers.get("X-RapidAPI-User", "")
        if rapid_user:
            return f"rapid:{rapid_user}"
        api_key = request.headers.get("X-API-Key", "")
        if api_key:
            return f"key:{api_key}"
        forwarded = request.headers.get("X-Forwarded-For", "")
        ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")
        return f"ip:{ip}"

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        client_key = self._get_client_key(request)
        now = time.time()
        window = 60.0

        count, window_start = self._buckets.get(client_key, (0, now))

        # Reset window if expired
        if now - window_start >= window:
            count = 0
            window_start = now

        count += 1
        self._buckets[client_key] = (count, window_start)

        remaining = max(0, self.rpm - count)
        reset_at = int(window_start + window)

        if count > self.rpm:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {self.rpm} requests per minute",
                    "retry_after": reset_at - int(now),
                },
                headers={
                    "X-RateLimit-Limit": str(self.rpm),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_at),
                    "Retry-After": str(reset_at - int(now)),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.rpm)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_at)
        return response


class ResponseCacheMiddleware(BaseHTTPMiddleware):
    """Cache GET responses for identical queries. TTL = 5 minutes, max 10k entries."""

    EXEMPT_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json"}

    def __init__(self, app, maxsize: int = 10_000, ttl: int = 300):
        super().__init__(app)
        self._cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)

    def _cache_key(self, request: Request) -> str | None:
        """Only cache GET requests. Include client identity to prevent cross-user cache leakage."""
        if request.method != "GET":
            return None
        if request.url.path in self.EXEMPT_PATHS:
            return None
        # Include client identity in cache key to isolate per-user responses
        client_id = (
            request.headers.get("X-RapidAPI-User", "")
            or request.headers.get("X-API-Key", "")
            or request.client.host if request.client else "unknown"
        )
        raw = f"{client_id}:{request.url.path}?{request.url.query}"
        return hashlib.md5(raw.encode()).hexdigest()

    async def dispatch(self, request: Request, call_next):
        key = self._cache_key(request)

        if key and key in self._cache:
            cached_body, cached_status, cached_content_type = self._cache[key]
            resp = Response(
                content=cached_body,
                status_code=cached_status,
                media_type=cached_content_type,
            )
            resp.headers["X-Cache"] = "HIT"
            return resp

        response = await call_next(request)

        if key and 200 <= response.status_code < 300:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk if isinstance(chunk, bytes) else chunk.encode()
            content_type = response.headers.get("content-type", "application/json")
            self._cache[key] = (body, response.status_code, content_type)

            resp = Response(
                content=body,
                status_code=response.status_code,
                media_type=content_type,
            )
            # Copy headers from original
            for k, v in response.headers.items():
                if k.lower() not in ("content-length", "content-type"):
                    resp.headers[k] = v
            resp.headers["X-Cache"] = "MISS"
            return resp

        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Add response timing and version headers."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000
        response.headers["X-Response-Time"] = f"{elapsed:.1f}ms"
        response.headers["X-API-Version"] = "2.1.0"
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every response for traceability."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
