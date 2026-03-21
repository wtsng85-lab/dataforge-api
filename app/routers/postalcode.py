"""Postal code validation endpoints."""

from fastapi import APIRouter, Query

from app.models import PostalCodeValidateRequest, PostalCodeValidateResponse
from app.validators.postalcode import validate_postal_code, POSTAL_PATTERNS

router = APIRouter(prefix="/postalcode", tags=["Postal Code"])


@router.get("/validate", summary="Validate a postal/ZIP code", response_model=PostalCodeValidateResponse)
async def postal_validate(
    code: str = Query(..., description="Postal/ZIP code", examples=["10001"], max_length=15),
    country: str = Query(..., description="ISO country code", examples=["US"], max_length=3),
):
    """Validate a postal/ZIP code for a given country. Supports 30+ countries."""
    return validate_postal_code(code.strip(), country.strip())


@router.post("/validate", summary="Validate a postal/ZIP code (POST)", response_model=PostalCodeValidateResponse)
async def postal_validate_post(req: PostalCodeValidateRequest):
    """Validate a postal/ZIP code via POST body."""
    return validate_postal_code(req.code.strip(), req.country.strip())


@router.get("/countries", summary="List supported countries")
async def postal_countries():
    """List all supported countries with example postal code formats."""
    return {
        "total": len(POSTAL_PATTERNS),
        "countries": {
            code: {"example": example}
            for code, (_, example) in sorted(POSTAL_PATTERNS.items())
        },
    }
