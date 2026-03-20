"""Credit card validation endpoints."""

from fastapi import APIRouter, Query

from app.models import CreditCardValidateRequest
from app.validators.creditcard import validate_credit_card

router = APIRouter(prefix="/creditcard", tags=["Credit Card"])


@router.get("/validate", summary="Validate a credit card number")
async def cc_validate(
    number: str = Query(..., description="Credit card number", examples=["4111111111111111"]),
):
    """Validate a credit card number using Luhn algorithm and detect card type (Visa, Mastercard, Amex, etc.)."""
    return validate_credit_card(number)


@router.post("/validate", summary="Validate a credit card number (POST)")
async def cc_validate_post(req: CreditCardValidateRequest):
    """Validate a credit card number via POST body."""
    return validate_credit_card(req.number)
