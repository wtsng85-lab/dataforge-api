"""VAT number validation endpoints."""

from fastapi import APIRouter, Query

from app.models import VATValidateRequest, VATValidateResponse
from app.validators.vat import validate_vat

router = APIRouter(prefix="/vat", tags=["VAT"])


@router.get("/validate", summary="Validate an EU VAT number", response_model=VATValidateResponse)
async def vat_validate(
    vat_number: str = Query(..., description="EU VAT number", examples=["DE123456789"], max_length=20),
):
    """Validate an EU VAT number format. Supports 28 EU countries + UK."""
    return validate_vat(vat_number.strip())


@router.post("/validate", summary="Validate an EU VAT number (POST)", response_model=VATValidateResponse)
async def vat_validate_post(req: VATValidateRequest):
    """Validate an EU VAT number via POST body."""
    return validate_vat(req.vat_number.strip())
