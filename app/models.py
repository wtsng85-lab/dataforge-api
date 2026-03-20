"""Pydantic models for request/response schemas."""

from pydantic import BaseModel, Field


# --- Phone ---
class PhoneValidateRequest(BaseModel):
    number: str = Field(..., description="Phone number to validate", examples=["+14155552671"])
    country_code: str | None = Field(None, description="ISO 3166-1 alpha-2 country code", examples=["US"])


class PhoneFormatRequest(BaseModel):
    number: str = Field(..., description="Phone number to format", examples=["+14155552671"])
    country_code: str | None = Field(None, description="ISO country code", examples=["US"])
    format: str = Field("e164", description="Output format: e164, international, national, rfc3966")


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


# --- Bulk ---
class BulkPhoneRequest(BaseModel):
    numbers: list[str] = Field(..., description="List of phone numbers (max 100)", max_length=100)
    country_code: str | None = Field(None, description="Default country code")


