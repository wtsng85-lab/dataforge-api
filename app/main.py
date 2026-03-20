"""DataForge — Universal Data Formatter & Validator API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.middleware import RapidAPIAuthMiddleware, RequestTimingMiddleware
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

### Use Cases
- **Fintech** — Validate IBANs, credit cards, and VAT numbers at checkout
- **E-commerce** — Validate shipping addresses and phone numbers internationally
- **SaaS** — Clean and normalize user-submitted data at registration
- **Data Pipelines** — Bulk validate and format phone numbers, dates, postal codes
"""

app = FastAPI(
    title="DataForge",
    description=DESCRIPTION,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "DataForge API", "url": "https://rapidapi.com"},
    license_info={"name": "MIT"},
)

# Middleware (order matters — outermost first)
app.add_middleware(RequestTimingMiddleware)
app.add_middleware(RapidAPIAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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
    }


@app.get("/health", tags=["Health"], summary="Health check")
async def health():
    """Check API health and uptime."""
    return {"status": "ok", "service": "DataForge", "version": "1.0.0"}
