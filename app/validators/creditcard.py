"""Credit card number validation using Luhn algorithm and BIN lookup."""

import re

# BIN (Bank Identification Number) patterns for card type detection
CARD_PATTERNS = [
    ("visa", re.compile(r"^4[0-9]{12}(?:[0-9]{3})?$")),
    ("mastercard", re.compile(r"^5[1-5][0-9]{14}$|^2(?:2[2-9][1-9]|2[3-9][0-9]|[3-6][0-9]{2}|7[01][0-9]|720)[0-9]{12}$")),
    ("amex", re.compile(r"^3[47][0-9]{13}$")),
    ("discover", re.compile(r"^6(?:011|5[0-9]{2})[0-9]{12}$")),
    ("diners_club", re.compile(r"^3(?:0[0-5]|[68][0-9])[0-9]{11}$")),
    ("jcb", re.compile(r"^(?:2131|1800|35\d{3})\d{11}$")),
    ("unionpay", re.compile(r"^62[0-9]{14,17}$")),
    ("maestro", re.compile(r"^(?:5[0678]\d\d|6304|6390|67\d\d)\d{8,15}$")),
]


def luhn_check(number: str) -> bool:
    """Validate a number using the Luhn algorithm."""
    digits = [int(d) for d in number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    return total % 10 == 0


def detect_card_type(number: str) -> str:
    """Detect card network from number."""
    for card_type, pattern in CARD_PATTERNS:
        if pattern.match(number):
            return card_type
    return "unknown"


def validate_credit_card(number: str) -> dict:
    """Validate a credit card number."""
    cleaned = re.sub(r"[\s\-]", "", number)

    if not cleaned.isdigit():
        return {
            "valid": False,
            "input": number,
            "error": "Card number must contain only digits",
        }

    if len(cleaned) < 13 or len(cleaned) > 19:
        return {
            "valid": False,
            "input": number,
            "error": f"Invalid length: {len(cleaned)} digits (expected 13-19)",
        }

    is_valid = luhn_check(cleaned)
    card_type = detect_card_type(cleaned)

    return {
        "valid": is_valid,
        "input": number,
        "card_type": card_type,
        "luhn_valid": is_valid,
        "length": len(cleaned),
        "bin": cleaned[:6],
        "last_four": cleaned[-4:],
        "masked": f"{'*' * (len(cleaned) - 4)}{cleaned[-4:]}",
    }
