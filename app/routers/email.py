"""Email validation endpoints."""

from fastapi import APIRouter, Query

from app.models import EmailValidateRequest, EmailValidateResponse
from app.validators.email import validate_email

router = APIRouter(prefix="/email", tags=["Email"])


@router.get("/validate", summary="Validate an email address", response_model=EmailValidateResponse)
async def email_validate(
    email: str = Query(..., description="Email address to validate", examples=["user@example.com"], max_length=254),
    check_mx: bool = Query(True, description="Check MX records for domain"),
):
    """Validate email syntax, check MX records, and detect disposable/free providers."""
    return validate_email(email.strip(), check_mx=check_mx)


@router.post("/validate", summary="Validate an email address (POST)", response_model=EmailValidateResponse)
async def email_validate_post(req: EmailValidateRequest):
    """Validate an email address via POST body."""
    return validate_email(req.email.strip(), check_mx=req.check_mx)
