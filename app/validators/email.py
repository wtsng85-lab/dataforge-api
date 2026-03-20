"""Email address validation with syntax, MX record, and disposable domain detection."""

import re
import socket

_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)

# Common disposable/temporary email domains
DISPOSABLE_DOMAINS = frozenset({
    "mailinator.com", "guerrillamail.com", "guerrillamail.de", "tempmail.com",
    "throwaway.email", "yopmail.com", "sharklasers.com", "guerrillamailblock.com",
    "grr.la", "dispostable.com", "trashmail.com", "trashmail.me", "trashmail.net",
    "10minutemail.com", "tempail.com", "burnermail.io", "temp-mail.org",
    "fakeinbox.com", "mailnesia.com", "maildrop.cc", "discard.email",
    "getnada.com", "mohmal.com", "emailondeck.com", "crazymailing.com",
    "tmail.ws", "tmpmail.net", "tmpmail.org", "bupmail.com", "mailtemp.net",
    "tempinbox.com", "disposableemailaddresses.emailmiser.com",
    "harakirimail.com", "mailexpire.com", "mailforspam.com", "safetymail.info",
    "spamgourmet.com", "trashymail.com", "mytemp.email", "tempr.email",
    "guerrillamail.info", "guerrillamail.net", "guerrillamail.org",
    "mailcatch.com", "meltmail.com", "throwam.com",
})

# Common free email providers
FREE_PROVIDERS = frozenset({
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
    "icloud.com", "mail.com", "zoho.com", "protonmail.com", "proton.me",
    "yandex.com", "gmx.com", "gmx.net", "live.com", "msn.com",
    "qq.com", "163.com", "126.com", "foxmail.com",
})


def validate_email(email: str, check_mx: bool = True) -> dict:
    """Validate an email address with syntax check, MX lookup, and disposable detection."""
    stripped = email.strip()

    # Basic syntax check
    if not stripped or not _EMAIL_RE.match(stripped):
        return {
            "valid": False,
            "input": email,
            "error": "Invalid email syntax",
        }

    parts = stripped.rsplit("@", 1)
    if len(parts) != 2:
        return {"valid": False, "input": email, "error": "Invalid email syntax"}

    local_part, domain = parts
    domain_lower = domain.lower()

    # Length checks (RFC 5321)
    if len(local_part) > 64:
        return {"valid": False, "input": email, "error": "Local part exceeds 64 characters"}
    if len(domain) > 253:
        return {"valid": False, "input": email, "error": "Domain exceeds 253 characters"}

    is_disposable = domain_lower in DISPOSABLE_DOMAINS
    is_free = domain_lower in FREE_PROVIDERS

    # MX record check
    mx_found = None
    mx_records = []
    if check_mx:
        try:
            import dns.resolver
            answers = dns.resolver.resolve(domain, "MX")
            mx_records = sorted(
                [{"priority": r.preference, "host": str(r.exchange).rstrip(".")} for r in answers],
                key=lambda x: x["priority"],
            )
            mx_found = True
        except Exception:
            # Fallback: try socket-based A record check
            try:
                socket.getaddrinfo(domain, None)
                mx_found = True
            except socket.gaierror:
                mx_found = False

    result = {
        "valid": True,
        "input": email,
        "normalized": f"{local_part}@{domain_lower}",
        "local_part": local_part,
        "domain": domain_lower,
        "is_disposable": is_disposable,
        "is_free_provider": is_free,
    }

    if mx_found is not None:
        result["mx_found"] = mx_found
        if mx_records:
            result["mx_records"] = mx_records
        if not mx_found:
            result["valid"] = False
            result["error"] = "Domain has no valid mail server"

    if is_disposable:
        result["warning"] = "Disposable/temporary email address detected"

    return result
