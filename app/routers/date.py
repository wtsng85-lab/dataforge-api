"""Date conversion and detection endpoints."""

from fastapi import APIRouter, Query

from app.models import DateConvertRequest, DateDetectRequest
from app.validators.date import convert_date, detect_date_format

router = APIRouter(prefix="/date", tags=["Date"])


@router.get("/convert", summary="Convert a date between formats")
async def date_convert(
    date: str = Query(..., description="Date string", examples=["03/20/2026"]),
    from_format: str = Query(..., description="Source format", examples=["MM/DD/YYYY"]),
    to_format: str = Query(..., description="Target format", examples=["ISO8601"]),
):
    """Convert a date string from one format to another. Supports 15+ date formats."""
    return convert_date(date, from_format, to_format)


@router.post("/convert", summary="Convert a date between formats (POST)")
async def date_convert_post(req: DateConvertRequest):
    """Convert a date string via POST body."""
    return convert_date(req.date, req.from_format, req.to_format)


@router.get("/detect", summary="Detect date format")
async def date_detect(
    date: str = Query(..., description="Date string to detect", examples=["2026-03-20"]),
):
    """Detect the format of a date string. Returns all possible matches and flags ambiguity."""
    return detect_date_format(date)


@router.post("/detect", summary="Detect date format (POST)")
async def date_detect_post(req: DateDetectRequest):
    """Detect date format via POST body."""
    return detect_date_format(req.date)
