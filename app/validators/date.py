"""Date format detection, validation, and conversion."""

from datetime import datetime, date

FORMAT_MAP = {
    "ISO8601": "%Y-%m-%d",
    "US": "%m/%d/%Y",
    "EU": "%d/%m/%Y",
    "UK": "%d-%m-%Y",
    "YYYY-MM-DD": "%Y-%m-%d",
    "DD/MM/YYYY": "%d/%m/%Y",
    "MM/DD/YYYY": "%m/%d/%Y",
    "DD-MM-YYYY": "%d-%m-%Y",
    "MM-DD-YYYY": "%m-%d-%Y",
    "YYYY/MM/DD": "%Y/%m/%d",
    "DD.MM.YYYY": "%d.%m.%Y",
    "YYYYMMDD": "%Y%m%d",
    "RFC2822": "%a, %d %b %Y",
    "LONG_US": "%B %d, %Y",
    "LONG_EU": "%d %B %Y",
}

DETECTION_FORMATS = [
    ("%Y-%m-%d", "ISO8601"),
    ("%Y/%m/%d", "YYYY/MM/DD"),
    ("%Y%m%d", "YYYYMMDD"),
    ("%d/%m/%Y", "DD/MM/YYYY"),
    ("%m/%d/%Y", "MM/DD/YYYY"),
    ("%d-%m-%Y", "DD-MM-YYYY"),
    ("%m-%d-%Y", "MM-DD-YYYY"),
    ("%d.%m.%Y", "DD.MM.YYYY"),
    ("%B %d, %Y", "LONG_US"),
    ("%d %B %Y", "LONG_EU"),
    ("%b %d, %Y", "LONG_US"),
    ("%d %b %Y", "LONG_EU"),
]


def convert_date(date_str: str, from_format: str, to_format: str) -> dict:
    """Convert a date string from one format to another."""
    from_fmt = FORMAT_MAP.get(from_format.upper())
    to_fmt = FORMAT_MAP.get(to_format.upper())

    if not from_fmt:
        return {
            "error": f"Unsupported source format: {from_format}",
            "supported_formats": list(FORMAT_MAP.keys()),
        }
    if not to_fmt:
        return {
            "error": f"Unsupported target format: {to_format}",
            "supported_formats": list(FORMAT_MAP.keys()),
        }

    try:
        parsed = datetime.strptime(date_str.strip(), from_fmt)
    except ValueError:
        return {
            "error": f"Cannot parse '{date_str}' with format {from_format} ({from_fmt})",
            "input": date_str,
        }

    return {
        "input": date_str,
        "from_format": from_format,
        "to_format": to_format,
        "result": parsed.strftime(to_fmt),
        "iso8601": parsed.strftime("%Y-%m-%d"),
        "timestamp": int(parsed.timestamp()),
        "day_of_week": parsed.strftime("%A"),
    }


def detect_date_format(date_str: str) -> dict:
    """Detect the format of a date string."""
    stripped = date_str.strip()
    matches = []

    for fmt, name in DETECTION_FORMATS:
        try:
            parsed = datetime.strptime(stripped, fmt)
            if 1900 <= parsed.year <= 2100:
                matches.append({
                    "format": name,
                    "pattern": fmt,
                    "parsed": parsed.strftime("%Y-%m-%d"),
                })
        except ValueError:
            continue

    return {
        "input": date_str,
        "detected_formats": matches,
        "best_match": matches[0] if matches else None,
        "ambiguous": len(matches) > 1,
    }
