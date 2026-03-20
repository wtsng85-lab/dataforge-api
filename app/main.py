"""DataForge — Universal Data Formatter & Validator API."""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("dataforge")

from app.middleware import (
    RapidAPIAuthMiddleware,
    RateLimitMiddleware,
    ResponseCacheMiddleware,
    RequestTimingMiddleware,
)
from app.routers import phone, iban, creditcard, vat, postalcode, date

DESCRIPTION = """
## DataForge — Universal Data Formatter & Validator API

The Swiss Army knife for data validation. One API to validate, format, and parse:

- **Phone Numbers** — Validate, format (E.164/international/national), detect carrier & timezone
- **IBAN** — Validate, extract bank code, BIC lookup
- **Credit Cards** — Luhn check, card type detection (Visa, Mastercard, Amex, etc.)
- **VAT Numbers** — EU VAT format validation (28 countries + UK)
- **Postal Codes** — Validate ZIP/postal codes for 30+ countries
- **Dates** — Convert between 15+ date formats, auto-detect format

### Why DataForge?
Stop subscribing to 6 different validation APIs. DataForge bundles all structured data
validation into a single, blazing-fast API with sub-50ms response times.

### Features
- **Rate limiting** — Per-client rate limiting with clear headers
- **Response caching** — GET requests cached for 5 minutes (10k entries)
- **Bulk operations** — Validate up to 100 phone numbers per request

### Use Cases
- **Fintech** — Validate IBANs, credit cards, and VAT numbers at checkout
- **E-commerce** — Validate shipping addresses and phone numbers internationally
- **SaaS** — Clean and normalize user-submitted data at registration
- **Data Pipelines** — Bulk validate and format phone numbers, dates, postal codes
"""

_start_time = time.time()

app = FastAPI(
    title="DataForge",
    description=DESCRIPTION,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "DataForge API", "url": "https://rapidapi.com"},
    license_info={"name": "MIT"},
)

# Middleware (order matters — outermost first, executes first on request)
app.add_middleware(RequestTimingMiddleware)
app.add_middleware(ResponseCacheMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
app.add_middleware(RapidAPIAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler — never leak stack traces
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again.",
        },
    )


# Routers
app.include_router(phone.router)
app.include_router(iban.router)
app.include_router(creditcard.router)
app.include_router(vat.router)
app.include_router(postalcode.router)
app.include_router(date.router)


@app.get("/", tags=["Health"], include_in_schema=False)
async def root():
    return {
        "service": "DataForge",
        "version": "1.0.0",
        "description": "Universal Data Formatter & Validator API",
        "docs": "/docs",
        "endpoints": {
            "phone": "/phone/validate",
            "iban": "/iban/validate",
            "creditcard": "/creditcard/validate",
            "vat": "/vat/validate",
            "postalcode": "/postalcode/validate",
            "date_convert": "/date/convert",
            "date_detect": "/date/detect",
        },
    }


@app.get("/health", tags=["Health"], summary="Health check")
async def health():
    """Check API health and uptime."""
    uptime = time.time() - _start_time
    return {
        "status": "ok",
        "service": "DataForge",
        "version": "1.0.0",
        "uptime_seconds": round(uptime, 1),
    }
