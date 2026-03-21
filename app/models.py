"""Pydantic models for request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


def _coerce_optional_str(v):
    """Coerce non-string values (e.g. {} from RapidAPI) to None."""
    if v is None or isinstance(v, str):
        return v or None
    return None


def _coerce_str_with_default(v, default: str) -> str:
    """Coerce non-string values to default. For required str fields with defaults."""
    if isinstance(v, str) and v:
        return v
    return default


def _coerce_bool_with_default(v, default: bool) -> bool:
    """Coerce non-bool values (e.g. {} from RapidAPI) to default."""
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    return default


# --- Phone ---
class PhoneValidateRequest(BaseModel):
    number: str = Field(..., description="Phone number to validate", examples=["+14155552671"])
    country_code: str | None = Field(None, description="ISO 3166-1 alpha-2 country code", examples=["US"])

    @field_validator("country_code", mode="before")
    @classmethod
    def clean_country_code(cls, v):
        return _coerce_optional_str(v)


class PhoneFormatRequest(BaseModel):
    number: str = Field(..., description="Phone number to format", examples=["+14155552671"])
    country_code: str | None = Field(None, description="ISO country code", examples=["US"])
    format: str = Field("e164", description="Output format: e164, international, national, rfc3966")

    @field_validator("country_code", mode="before")
    @classmethod
    def clean_country_code(cls, v):
        return _coerce_optional_str(v)

    @field_validator("format", mode="before")
    @classmethod
    def clean_format(cls, v):
        return _coerce_str_with_default(v, "e164")


# --- IBAN ---
class IBANValidateRequest(BaseModel):
    iban: str = Field(..., description="IBAN to validate", examples=["DE89370400440532013000"])


# --- Credit Card ---
class CreditCardValidateRequest(BaseModel):
    number: str = Field(..., description="Credit card number", examples=["4111111111111111"])


# --- VAT ---
class VATValidateRequest(BaseModel):
    vat_number: str = Field(..., description="EU VAT number", examples=["DE123456789"])


# --- Postal Code ---
class PostalCodeValidateRequest(BaseModel):
    code: str = Field(..., description="Postal/ZIP code", examples=["10001"])
    country: str = Field(..., description="ISO country code", examples=["US"])


# --- Date ---
class DateConvertRequest(BaseModel):
    date: str = Field(..., description="Date string to convert", examples=["03/20/2026"])
    from_format: str = Field(..., description="Source format name", examples=["MM/DD/YYYY"])
    to_format: str = Field(..., description="Target format name", examples=["ISO8601"])


class DateDetectRequest(BaseModel):
    date: str = Field(..., description="Date string to detect format of", examples=["2026-03-20"])


# --- Email ---
class EmailValidateRequest(BaseModel):
    email: str = Field(..., description="Email address to validate", examples=["user@example.com"])
    check_mx: bool = Field(True, description="Check MX records for domain")

    @field_validator("check_mx", mode="before")
    @classmethod
    def clean_check_mx(cls, v):
        return _coerce_bool_with_default(v, True)


# --- Password ---
class PasswordAnalyzeRequest(BaseModel):
    password: str = Field(..., description="Password to analyze", examples=["MyP@ss123!"])


# --- Crypto ---
class CryptoValidateRequest(BaseModel):
    address: str = Field(..., description="Wallet address", examples=["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"])
    chain: str | None = Field(None, description="Blockchain: btc, eth (auto-detected if omitted)")

    @field_validator("chain", mode="before")
    @classmethod
    def clean_chain(cls, v):
        return _coerce_optional_str(v)


# --- Bulk ---
class BulkPhoneRequest(BaseModel):
    numbers: list[str] = Field(..., description="List of phone numbers (max 100)", max_length=100)
    country_code: str | None = Field(None, description="Default country code")

    @field_validator("country_code", mode="before")
    @classmethod
    def clean_country_code(cls, v):
        return _coerce_optional_str(v)


# ═══════════════════════════════════════════
# Response Models (for OpenAPI example responses)
# ═══════════════════════════════════════════


class PhoneValidateResponse(BaseModel):
    valid: bool
    possible: bool | None = None
    input: str
    e164: str | None = None
    international: str | None = None
    national: str | None = None
    country_code: int | None = None
    national_number: str | None = None
    number_type: str | None = None
    country: str | None = None
    carrier: str | None = None
    timezones: list[str] | None = None
    error: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"valid": True, "possible": True, "input": "+14155552671", "e164": "+14155552671", "international": "+1 415-555-2671", "national": "(415) 555-2671", "country_code": 1, "national_number": "4155552671", "number_type": "fixed_line_or_mobile", "country": "San Francisco, CA", "carrier": "", "timezones": ["America/Los_Angeles"]}]}}


class PhoneFormatResponse(BaseModel):
    input: str
    formatted: str
    format: str
    valid: bool

    model_config = {"json_schema_extra": {"examples": [{"input": "+14155552671", "formatted": "+1 415-555-2671", "format": "international", "valid": True}]}}


class BulkPhoneResponse(BaseModel):
    total: int
    valid_count: int
    invalid_count: int
    results: list[dict]

    model_config = {"json_schema_extra": {"examples": [{"total": 2, "valid_count": 1, "invalid_count": 1, "results": [{"valid": True, "input": "+14155552671", "e164": "+14155552671"}, {"valid": False, "input": "invalid", "error": "Not a phone number"}]}]}}


class EmailValidateResponse(BaseModel):
    valid: bool
    input: str
    normalized: str | None = None
    local_part: str | None = None
    domain: str | None = None
    is_disposable: bool | None = None
    is_free_provider: bool | None = None
    mx_found: bool | None = None
    mx_records: list[dict] | None = None
    error: str | None = None
    warning: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"valid": True, "input": "test@gmail.com", "normalized": "test@gmail.com", "local_part": "test", "domain": "gmail.com", "is_disposable": False, "is_free_provider": True, "mx_found": True, "mx_records": [{"priority": 5, "host": "gmail-smtp-in.l.google.com"}]}]}}


class IBANValidateResponse(BaseModel):
    valid: bool
    input: str
    iban_formatted: str | None = None
    iban_compact: str | None = None
    country_code: str | None = None
    bank_code: str | None = None
    account_code: str | None = None
    length: int | None = None
    checksum_digits: str | None = None
    bic: str | None = None
    bank_name: str | None = None
    error: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"valid": True, "input": "DE89370400440532013000", "iban_formatted": "DE89 3704 0044 0532 0130 00", "iban_compact": "DE89370400440532013000", "country_code": "DE", "bank_code": "37040044", "account_code": "0532013000", "length": 22, "checksum_digits": "89", "bic": "COBADEFFXXX", "bank_name": "Commerzbank"}]}}


class CreditCardValidateResponse(BaseModel):
    valid: bool
    input: str
    card_type: str | None = None
    luhn_valid: bool | None = None
    length: int | None = None
    bin: str | None = None
    last_four: str | None = None
    masked: str | None = None
    error: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"valid": True, "input": "4111111111111111", "card_type": "visa", "luhn_valid": True, "length": 16, "bin": "411111", "last_four": "1111", "masked": "************1111"}]}}


class VATValidateResponse(BaseModel):
    valid: bool
    input: str
    vat_number: str | None = None
    country_code: str | None = None
    country_name: str | None = None
    expected_format: str | None = None
    error: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"valid": True, "input": "DE123456789", "vat_number": "DE123456789", "country_code": "DE", "country_name": "Germany", "expected_format": "DE + 9 digits", "error": None}]}}


class PostalCodeValidateResponse(BaseModel):
    valid: bool
    input: str
    country: str
    example_format: str | None = None
    error: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"valid": True, "input": "10001", "country": "US", "example_format": "12345 or 12345-6789", "error": None}]}}


class DateConvertResponse(BaseModel):
    input: str | None = None
    from_format: str | None = None
    to_format: str | None = None
    result: str | None = None
    iso8601: str | None = None
    timestamp: int | None = None
    day_of_week: str | None = None
    error: str | None = None
    supported_formats: list[str] | None = None

    model_config = {"json_schema_extra": {"examples": [{"input": "03/15/2024", "from_format": "US", "to_format": "ISO8601", "result": "2024-03-15", "iso8601": "2024-03-15", "timestamp": 1710460800, "day_of_week": "Friday"}]}}


class DateDetectResponse(BaseModel):
    input: str
    detected_formats: list[dict]
    best_match: dict | None = None
    ambiguous: bool

    model_config = {"json_schema_extra": {"examples": [{"input": "2024-03-15", "detected_formats": [{"format": "ISO8601", "pattern": "%Y-%m-%d", "parsed": "2024-03-15"}], "best_match": {"format": "ISO8601", "pattern": "%Y-%m-%d", "parsed": "2024-03-15"}, "ambiguous": False}]}}


class PasswordAnalyzeResponse(BaseModel):
    input_length: int
    score: int
    strength: str
    entropy_bits: float
    character_analysis: dict | None = None
    warnings: dict | None = None
    suggestions: list[str] | None = None
    error: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"input_length": 11, "score": 54, "strength": "moderate", "entropy_bits": 56.9, "character_analysis": {"has_lowercase": True, "has_uppercase": False, "has_digits": True, "has_special": False, "character_types": 2}, "warnings": {"is_common": False, "has_sequential": True, "has_repeated": False}, "suggestions": ["Add uppercase letters", "Add special characters (!@#$%...)"]}]}}


class CryptoValidateResponse(BaseModel):
    chain: str | None = None
    input: str
    valid: bool
    address_type: str | None = None
    format: str | None = None
    checksum_valid: bool | None = None
    error: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"chain": "bitcoin", "input": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "valid": True, "address_type": "p2pkh_legacy", "format": "base58check"}]}}
