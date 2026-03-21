"""Phone number validation and formatting endpoints."""

from fastapi import APIRouter, Query

from app.models import (
    PhoneValidateRequest, BulkPhoneRequest,
    PhoneValidateResponse, PhoneFormatResponse, BulkPhoneResponse,
)
from app.validators.phone import validate_phone, format_phone

router = APIRouter(prefix="/phone", tags=["Phone"])


@router.get("/validate", summary="Validate a phone number", response_model=PhoneValidateResponse)
async def phone_validate(
    number: str = Query(..., description="Phone number to validate", examples=["+14155552671"], max_length=30),
    country_code: str | None = Query(None, description="ISO country code", examples=["US"], max_length=3),
):
    """Validate a phone number and return parsed details including carrier, country, and timezone."""
    return validate_phone(number.strip(), country_code)


@router.post("/validate", summary="Validate a phone number (POST)", response_model=PhoneValidateResponse)
async def phone_validate_post(req: PhoneValidateRequest):
    """Validate a phone number via POST body."""
    return validate_phone(req.number, req.country_code)


@router.get("/format", summary="Format a phone number", response_model=PhoneFormatResponse)
async def phone_format(
    number: str = Query(..., description="Phone number", examples=["+14155552671"], max_length=30),
    country_code: str | None = Query(None, description="ISO country code", max_length=3),
    format: str = Query("e164", description="Output format: e164, international, national, rfc3966"),
):
    """Format a phone number to a specific format (E.164, international, national, RFC3966)."""
    return format_phone(number.strip(), country_code, format)


@router.post("/bulk-validate", summary="Bulk validate phone numbers", response_model=BulkPhoneResponse)
async def phone_bulk_validate(req: BulkPhoneRequest):
    """Validate up to 100 phone numbers in a single request."""
    results = [validate_phone(n, req.country_code) for n in req.numbers]
    valid_count = sum(1 for r in results if r.get("valid"))
    return {
        "total": len(results),
        "valid_count": valid_count,
        "invalid_count": len(results) - valid_count,
        "results": results,
    }
