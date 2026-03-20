"""Password strength analysis with entropy calculation and policy checking."""

import math
import re
import string

# Common weak passwords (top 50)
COMMON_PASSWORDS = frozenset({
    "123456", "password", "12345678", "qwerty", "123456789", "12345",
    "1234", "111111", "1234567", "dragon", "123123", "baseball",
    "abc123", "football", "monkey", "letmein", "shadow", "master",
    "666666", "qwertyuiop", "123321", "mustang", "1234567890",
    "michael", "654321", "superman", "1qaz2wsx", "7777777", "121212",
    "000000", "qazwsx", "123qwe", "killer", "trustno1", "jordan",
    "jennifer", "zxcvbnm", "asdfgh", "hunter", "buster", "soccer",
    "harley", "batman", "andrew", "tigger", "sunshine", "iloveyou",
    "2000", "charlie", "robert",
})

_SEQUENTIAL_PATTERNS = [
    string.ascii_lowercase,
    string.ascii_uppercase,
    string.digits,
    "qwertyuiop", "asdfghjkl", "zxcvbnm",
    "QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM",
]


def _has_sequential(password: str, length: int = 3) -> bool:
    """Check for sequential character patterns."""
    for seq in _SEQUENTIAL_PATTERNS:
        for i in range(len(seq) - length + 1):
            if seq[i:i + length] in password:
                return True
    return False


def _has_repeated(password: str, count: int = 3) -> bool:
    """Check for repeated characters (e.g., 'aaa')."""
    for i in range(len(password) - count + 1):
        if len(set(password[i:i + count])) == 1:
            return True
    return False


def _calculate_entropy(password: str) -> float:
    """Calculate password entropy in bits."""
    charset_size = 0
    if re.search(r"[a-z]", password):
        charset_size += 26
    if re.search(r"[A-Z]", password):
        charset_size += 26
    if re.search(r"\d", password):
        charset_size += 10
    if re.search(r"[^a-zA-Z0-9]", password):
        charset_size += 32
    if charset_size == 0:
        return 0.0
    return len(password) * math.log2(charset_size)


def analyze_password(password: str) -> dict:
    """Analyze password strength and return detailed assessment."""
    length = len(password)

    if length == 0:
        return {
            "input_length": 0,
            "score": 0,
            "strength": "invalid",
            "entropy_bits": 0.0,
            "error": "Password cannot be empty",
        }

    # Character analysis
    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[^a-zA-Z0-9]", password))

    char_types = sum([has_lower, has_upper, has_digit, has_special])

    # Weakness detection
    is_common = password.lower() in COMMON_PASSWORDS
    has_seq = _has_sequential(password)
    has_rep = _has_repeated(password)

    entropy = round(_calculate_entropy(password), 1)

    # Scoring (0-100)
    score = 0

    # Length contribution (up to 40 points)
    score += min(40, length * 4)

    # Character diversity (up to 30 points)
    score += char_types * 7.5

    # Entropy bonus (up to 20 points)
    score += min(20, entropy / 4)

    # Penalties
    if is_common:
        score = min(score, 5)
    if has_seq:
        score -= 15
    if has_rep:
        score -= 10
    if length < 8:
        score -= 20

    score = max(0, min(100, int(score)))

    # Strength label
    if score >= 80:
        strength = "very_strong"
    elif score >= 60:
        strength = "strong"
    elif score >= 40:
        strength = "moderate"
    elif score >= 20:
        strength = "weak"
    else:
        strength = "very_weak"

    # Suggestions
    suggestions = []
    if length < 8:
        suggestions.append("Use at least 8 characters")
    if length < 12:
        suggestions.append("Consider using 12+ characters for better security")
    if not has_upper:
        suggestions.append("Add uppercase letters")
    if not has_lower:
        suggestions.append("Add lowercase letters")
    if not has_digit:
        suggestions.append("Add numbers")
    if not has_special:
        suggestions.append("Add special characters (!@#$%...)")
    if is_common:
        suggestions.append("This is a commonly used password — choose something unique")
    if has_seq:
        suggestions.append("Avoid sequential patterns (abc, 123, qwerty)")
    if has_rep:
        suggestions.append("Avoid repeated characters (aaa, 111)")

    return {
        "input_length": length,
        "score": score,
        "strength": strength,
        "entropy_bits": entropy,
        "character_analysis": {
            "has_lowercase": has_lower,
            "has_uppercase": has_upper,
            "has_digits": has_digit,
            "has_special": has_special,
            "character_types": char_types,
        },
        "warnings": {
            "is_common": is_common,
            "has_sequential": has_seq,
            "has_repeated": has_rep,
        },
        "suggestions": suggestions,
    }
