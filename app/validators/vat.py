"""EU VAT number validation."""

import re

# EU VAT number format patterns per country
VAT_PATTERNS = {
    "AT": (re.compile(r"^ATU\d{8}$"), "ATU + 8 digits"),
    "BE": (re.compile(r"^BE[01]\d{9}$"), "BE + 10 digits"),
    "BG": (re.compile(r"^BG\d{9,10}$"), "BG + 9-10 digits"),
    "CY": (re.compile(r"^CY\d{8}[A-Z]$"), "CY + 8 digits + letter"),
    "CZ": (re.compile(r"^CZ\d{8,10}$"), "CZ + 8-10 digits"),
    "DE": (re.compile(r"^DE\d{9}$"), "DE + 9 digits"),
    "DK": (re.compile(r"^DK\d{8}$"), "DK + 8 digits"),
    "EE": (re.compile(r"^EE\d{9}$"), "EE + 9 digits"),
    "EL": (re.compile(r"^EL\d{9}$"), "EL + 9 digits"),
    "ES": (re.compile(r"^ES[A-Z0-9]\d{7}[A-Z0-9]$"), "ES + letter/digit + 7 digits + letter/digit"),
    "FI": (re.compile(r"^FI\d{8}$"), "FI + 8 digits"),
    "FR": (re.compile(r"^FR[A-Z0-9]{2}\d{9}$"), "FR + 2 chars + 9 digits"),
    "HR": (re.compile(r"^HR\d{11}$"), "HR + 11 digits"),
    "HU": (re.compile(r"^HU\d{8}$"), "HU + 8 digits"),
    "IE": (re.compile(r"^IE\d{7}[A-Z]{1,2}$|^IE\d[A-Z+*]\d{5}[A-Z]$"), "IE + 7 digits + 1-2 letters"),
    "IT": (re.compile(r"^IT\d{11}$"), "IT + 11 digits"),
    "LT": (re.compile(r"^LT\d{9}$|^LT\d{12}$"), "LT + 9 or 12 digits"),
    "LU": (re.compile(r"^LU\d{8}$"), "LU + 8 digits"),
    "LV": (re.compile(r"^LV\d{11}$"), "LV + 11 digits"),
    "MT": (re.compile(r"^MT\d{8}$"), "MT + 8 digits"),
    "NL": (re.compile(r"^NL\d{9}B\d{2}$"), "NL + 9 digits + B + 2 digits"),
    "PL": (re.compile(r"^PL\d{10}$"), "PL + 10 digits"),
    "PT": (re.compile(r"^PT\d{9}$"), "PT + 9 digits"),
    "RO": (re.compile(r"^RO\d{2,10}$"), "RO + 2-10 digits"),
    "SE": (re.compile(r"^SE\d{12}$"), "SE + 12 digits"),
    "SI": (re.compile(r"^SI\d{8}$"), "SI + 8 digits"),
    "SK": (re.compile(r"^SK\d{10}$"), "SK + 10 digits"),
    "GB": (re.compile(r"^GB\d{9}$|^GB\d{12}$|^GBGD\d{3}$|^GBHA\d{3}$"), "GB + 9 or 12 digits"),
}

COUNTRY_NAMES = {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CY": "Cyprus",
    "CZ": "Czech Republic", "DE": "Germany", "DK": "Denmark", "EE": "Estonia",
    "EL": "Greece", "ES": "Spain", "FI": "Finland", "FR": "France",
    "HR": "Croatia", "HU": "Hungary", "IE": "Ireland", "IT": "Italy",
    "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia", "MT": "Malta",
    "NL": "Netherlands", "PL": "Poland", "PT": "Portugal", "RO": "Romania",
    "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia", "GB": "United Kingdom",
}


def validate_vat(vat_number: str) -> dict:
    """Validate an EU VAT number format."""
    cleaned = vat_number.replace(" ", "").replace("-", "").replace(".", "").upper()

    if len(cleaned) < 4:
        return {
            "valid": False,
            "input": vat_number,
            "error": "VAT number too short",
        }

    country_prefix = cleaned[:2]

    if country_prefix not in VAT_PATTERNS:
        return {
            "valid": False,
            "input": vat_number,
            "country_code": country_prefix,
            "error": f"Unsupported country prefix: {country_prefix}",
            "supported_countries": list(VAT_PATTERNS.keys()),
        }

    pattern, expected_format = VAT_PATTERNS[country_prefix]
    is_valid = bool(pattern.match(cleaned))

    return {
        "valid": is_valid,
        "input": vat_number,
        "vat_number": cleaned,
        "country_code": country_prefix,
        "country_name": COUNTRY_NAMES.get(country_prefix, "Unknown"),
        "expected_format": expected_format,
        "error": None if is_valid else f"Does not match expected format: {expected_format}",
    }
