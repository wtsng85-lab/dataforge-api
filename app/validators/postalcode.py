"""Postal/ZIP code validation by country."""

import re

POSTAL_PATTERNS = {
    "US": (re.compile(r"^\d{5}(-\d{4})?$"), "12345 or 12345-6789"),
    "GB": (re.compile(r"^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$", re.I), "SW1A 1AA"),
    "CA": (re.compile(r"^[A-Z]\d[A-Z]\s?\d[A-Z]\d$", re.I), "K1A 0B1"),
    "DE": (re.compile(r"^\d{5}$"), "01234"),
    "FR": (re.compile(r"^\d{5}$"), "75001"),
    "IT": (re.compile(r"^\d{5}$"), "00100"),
    "ES": (re.compile(r"^\d{5}$"), "28001"),
    "NL": (re.compile(r"^\d{4}\s?[A-Z]{2}$", re.I), "1234 AB"),
    "BE": (re.compile(r"^\d{4}$"), "1000"),
    "AT": (re.compile(r"^\d{4}$"), "1010"),
    "CH": (re.compile(r"^\d{4}$"), "8001"),
    "AU": (re.compile(r"^\d{4}$"), "2000"),
    "JP": (re.compile(r"^\d{3}-?\d{4}$"), "100-0001"),
    "BR": (re.compile(r"^\d{5}-?\d{3}$"), "01001-000"),
    "IN": (re.compile(r"^\d{6}$"), "110001"),
    "RU": (re.compile(r"^\d{6}$"), "101000"),
    "CN": (re.compile(r"^\d{6}$"), "100000"),
    "KR": (re.compile(r"^\d{5}$"), "03171"),
    "SE": (re.compile(r"^\d{3}\s?\d{2}$"), "111 22"),
    "NO": (re.compile(r"^\d{4}$"), "0001"),
    "DK": (re.compile(r"^\d{4}$"), "1000"),
    "FI": (re.compile(r"^\d{5}$"), "00100"),
    "PL": (re.compile(r"^\d{2}-?\d{3}$"), "00-001"),
    "PT": (re.compile(r"^\d{4}-?\d{3}$"), "1000-001"),
    "CZ": (re.compile(r"^\d{3}\s?\d{2}$"), "110 00"),
    "MX": (re.compile(r"^\d{5}$"), "01000"),
    "SG": (re.compile(r"^\d{6}$"), "018956"),
    "NZ": (re.compile(r"^\d{4}$"), "6011"),
    "ZA": (re.compile(r"^\d{4}$"), "0001"),
    "IE": (re.compile(r"^[A-Z\d]{3}\s?[A-Z\d]{4}$", re.I), "D02 AF30"),
}


def validate_postal_code(code: str, country: str) -> dict:
    """Validate a postal/ZIP code for a given country."""
    country_upper = country.upper()

    if country_upper not in POSTAL_PATTERNS:
        return {
            "valid": False,
            "input": code,
            "country": country_upper,
            "error": f"Unsupported country: {country_upper}",
            "supported_countries": sorted(POSTAL_PATTERNS.keys()),
        }

    pattern, example = POSTAL_PATTERNS[country_upper]
    is_valid = bool(pattern.match(code.strip()))

    return {
        "valid": is_valid,
        "input": code,
        "country": country_upper,
        "example_format": example,
        "error": None if is_valid else f"Invalid format for {country_upper}. Expected format like: {example}",
    }
