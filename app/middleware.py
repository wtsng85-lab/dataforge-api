"""Middleware for authentication, rate limiting, and request tracking."""

import time

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from cachetools import TTLCache

from app.config import get_settings


class RapidAPIAuthMiddleware(BaseHTTPMiddleware):
    """Verify requests come from RapidAPI proxy or have a valid API key."""

    EXEMPT_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        settings = get_settings()

        # Check RapidAPI proxy secret
        rapid_secret = request.headers.get("X-RapidAPI-Proxy-Secret", "")
        if settings.rapidapi_proxy_secret and rapid_secret == settings.rapidapi_proxy_secret:
            return await call_next(request)

        # Check direct API key
        api_key = request.headers.get("X-API-Key", "")
        if settings.api_key and api_key == settings.api_key:
            return await call_next(request)

        # In dev mode, allow unauthenticated requests
        if settings.environment == "development":
            return await call_next(request)

        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized", "detail": "Valid API key required"},
        )


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Add response timing header."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000
        response.headers["X-Response-Time"] = f"{elapsed:.1f}ms"
        return response
