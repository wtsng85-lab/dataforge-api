"""Date conversion and detection endpoints."""

from fastapi import APIRouter, Query

from app.models import (
    DateConvertRequest, DateDetectRequest,
    DateConvertResponse, DateDetectResponse,
)
from app.validators.date import convert_date, detect_date_format, FORMAT_MAP

router = APIRouter(prefix="/date", tags=["Date"])


@router.get("/convert", summary="Convert a date between formats", response_model=DateConvertResponse)
async def date_convert(
    date: str = Query(..., description="Date string", examples=["03/20/2026"], max_length=50),
    from_format: str = Query(..., description="Source format", examples=["MM/DD/YYYY"], max_length=20),
    to_format: str = Query(..., description="Target format", examples=["ISO8601"], max_length=20),
):
    """Convert a date string from one format to another. Supports 15+ date formats."""
    return convert_date(date.strip(), from_format.strip(), to_format.strip())


@router.post("/convert", summary="Convert a date between formats (POST)", response_model=DateConvertResponse)
async def date_convert_post(req: DateConvertRequest):
    """Convert a date string via POST body."""
    return convert_date(req.date.strip(), req.from_format.strip(), req.to_format.strip())


@router.get("/detect", summary="Detect date format", response_model=DateDetectResponse)
async def date_detect(
    date: str = Query(..., description="Date string to detect", examples=["2026-03-20"], max_length=50),
):
    """Detect the format of a date string. Returns all possible matches and flags ambiguity."""
    return detect_date_format(date.strip())


@router.post("/detect", summary="Detect date format (POST)", response_model=DateDetectResponse)
async def date_detect_post(req: DateDetectRequest):
    """Detect date format via POST body."""
    return detect_date_format(req.date.strip())


@router.get("/formats", summary="List supported date formats")
async def date_formats():
    """List all supported date format names and their patterns."""
    return {
        "total": len(FORMAT_MAP),
        "formats": {name: pattern for name, pattern in sorted(FORMAT_MAP.items())},
    }
