"""IBAN validation endpoints."""

from fastapi import APIRouter, Query

from app.models import IBANValidateRequest
from app.validators.iban import validate_iban

router = APIRouter(prefix="/iban", tags=["IBAN"])


@router.get("/validate", summary="Validate an IBAN")
async def iban_validate(
    iban: str = Query(..., description="IBAN to validate", examples=["DE89370400440532013000"]),
):
    """Validate an IBAN and extract bank code, account code, BIC, and bank name."""
    return validate_iban(iban)


@router.post("/validate", summary="Validate an IBAN (POST)")
async def iban_validate_post(req: IBANValidateRequest):
    """Validate an IBAN via POST body."""
    return validate_iban(req.iban)
