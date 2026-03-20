"""Phone number validation and formatting."""

import phonenumbers
from phonenumbers import geocoder, carrier, timezone as pn_timezone


def validate_phone(number: str, country_code: str | None = None) -> dict:
    """Validate and parse a phone number."""
    try:
        region = country_code.upper() if country_code else None
        parsed = phonenumbers.parse(number, region)
    except phonenumbers.NumberParseException as e:
        return {
            "valid": False,
            "input": number,
            "error": str(e),
        }

    is_valid = phonenumbers.is_valid_number(parsed)
    is_possible = phonenumbers.is_possible_number(parsed)

    result = {
        "valid": is_valid,
        "possible": is_possible,
        "input": number,
        "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
        "international": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
        "national": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
        "country_code": parsed.country_code,
        "national_number": str(parsed.national_number),
        "number_type": _number_type_str(phonenumbers.number_type(parsed)),
    }

    if is_valid:
        result["country"] = geocoder.description_for_number(parsed, "en")
        result["carrier"] = carrier.name_for_number(parsed, "en")
        timezones = pn_timezone.time_zones_for_number(parsed)
        result["timezones"] = list(timezones) if timezones else []

    return result


def format_phone(number: str, country_code: str | None = None, fmt: str = "e164") -> dict:
    """Format a phone number to a specific format."""
    try:
        region = country_code.upper() if country_code else None
        parsed = phonenumbers.parse(number, region)
    except phonenumbers.NumberParseException as e:
        return {"valid": False, "error": str(e), "input": number}

    format_map = {
        "e164": phonenumbers.PhoneNumberFormat.E164,
        "international": phonenumbers.PhoneNumberFormat.INTERNATIONAL,
        "national": phonenumbers.PhoneNumberFormat.NATIONAL,
        "rfc3966": phonenumbers.PhoneNumberFormat.RFC3966,
    }

    pn_fmt = format_map.get(fmt.lower(), phonenumbers.PhoneNumberFormat.E164)
    return {
        "input": number,
        "formatted": phonenumbers.format_number(parsed, pn_fmt),
        "format": fmt.lower(),
        "valid": phonenumbers.is_valid_number(parsed),
    }


def _number_type_str(nt: int) -> str:
    type_map = {
        0: "fixed_line",
        1: "mobile",
        2: "fixed_line_or_mobile",
        3: "toll_free",
        4: "premium_rate",
        5: "shared_cost",
        6: "voip",
        7: "personal_number",
        8: "pager",
        9: "uan",
        10: "voicemail",
        99: "unknown",
    }
    return type_map.get(nt, "unknown")
