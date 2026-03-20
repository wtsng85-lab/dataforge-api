"""Password strength analysis endpoints."""

from fastapi import APIRouter, Query

from app.models import PasswordAnalyzeRequest
from app.validators.password import analyze_password

router = APIRouter(prefix="/password", tags=["Password"])


@router.get("/analyze", summary="Analyze password strength")
async def password_analyze(
    password: str = Query(..., description="Password to analyze", examples=["MyP@ss123!"], max_length=200),
):
    """Analyze password strength: entropy, character diversity, common password check, and suggestions."""
    return analyze_password(password)


@router.post("/analyze", summary="Analyze password strength (POST)")
async def password_analyze_post(req: PasswordAnalyzeRequest):
    """Analyze password strength via POST body."""
    return analyze_password(req.password)
