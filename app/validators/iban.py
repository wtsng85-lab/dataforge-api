"""IBAN validation and parsing."""

import schwifty


def validate_iban(iban_str: str) -> dict:
    """Validate an IBAN and extract bank information."""
    cleaned = iban_str.replace(" ", "").replace("-", "").upper()

    try:
        iban = schwifty.IBAN(cleaned)
    except ValueError as e:
        return {
            "valid": False,
            "input": iban_str,
            "error": str(e),
        }

    result = {
        "valid": True,
        "input": iban_str,
        "iban_formatted": iban.formatted,
        "iban_compact": iban.compact,
        "country_code": iban.country_code,
        "bank_code": iban.bank_code,
        "account_code": iban.account_code,
        "length": len(iban.compact),
        "checksum_digits": iban.compact[2:4],
    }

    try:
        bic = iban.bic
        if bic:
            result["bic"] = str(bic)
            result["bank_name"] = bic.bank_names[0] if hasattr(bic, "bank_names") and bic.bank_names else None
    except Exception:
        result["bic"] = None
        result["bank_name"] = None

    return result
