"""Postal code validation endpoints."""

from fastapi import APIRouter, Query

from app.models import PostalCodeValidateRequest
from app.validators.postalcode import validate_postal_code

router = APIRouter(prefix="/postalcode", tags=["Postal Code"])


@router.get("/validate", summary="Validate a postal/ZIP code")
async def postal_validate(
    code: str = Query(..., description="Postal/ZIP code", examples=["10001"]),
    country: str = Query(..., description="ISO country code", examples=["US"]),
):
    """Validate a postal/ZIP code for a given country. Supports 30+ countries."""
    return validate_postal_code(code, country)


@router.post("/validate", summary="Validate a postal/ZIP code (POST)")
async def postal_validate_post(req: PostalCodeValidateRequest):
    """Validate a postal/ZIP code via POST body."""
    return validate_postal_code(req.code, req.country)
