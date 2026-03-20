"""Comprehensive API tests for DataForge."""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


# ========================== Health ==========================

@pytest.mark.anyio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "DataForge"
    assert "endpoints" in data


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data


# ========================== Phone ==========================

@pytest.mark.anyio
async def test_phone_validate_valid(client):
    resp = await client.get("/phone/validate", params={"number": "+14155552671"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["country_code"] == 1
    assert data["e164"] == "+14155552671"
    assert "timezones" in data
    assert "carrier" in data


@pytest.mark.anyio
async def test_phone_validate_with_country(client):
    resp = await client.get("/phone/validate", params={"number": "0201234567", "country_code": "NL"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_phone_validate_invalid(client):
    resp = await client.get("/phone/validate", params={"number": "notaphone"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False
    assert "error" in data


@pytest.mark.anyio
async def test_phone_validate_empty_string(client):
    resp = await client.get("/phone/validate", params={"number": ""})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False


@pytest.mark.anyio
async def test_phone_validate_post(client):
    resp = await client.post("/phone/validate", json={"number": "+442071234567"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True
    assert resp.json()["country_code"] == 44


@pytest.mark.anyio
async def test_phone_format_international(client):
    resp = await client.get("/phone/format", params={"number": "+14155552671", "format": "international"})
    assert resp.status_code == 200
    data = resp.json()
    assert "+" in data["formatted"]


@pytest.mark.anyio
async def test_phone_format_national(client):
    resp = await client.get("/phone/format", params={"number": "+14155552671", "format": "national"})
    assert resp.status_code == 200
    assert resp.json()["format"] == "national"


@pytest.mark.anyio
async def test_phone_format_rfc3966(client):
    resp = await client.get("/phone/format", params={"number": "+14155552671", "format": "rfc3966"})
    assert resp.status_code == 200
    assert "tel:" in resp.json()["formatted"]


@pytest.mark.anyio
async def test_phone_bulk_validate(client):
    resp = await client.post("/phone/bulk-validate", json={
        "numbers": ["+14155552671", "+442071234567", "invalid"],
        "country_code": None,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert data["valid_count"] == 2
    assert data["invalid_count"] == 1
    assert len(data["results"]) == 3


@pytest.mark.anyio
async def test_phone_bulk_empty_list(client):
    resp = await client.post("/phone/bulk-validate", json={"numbers": []})
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


# ========================== IBAN ==========================

@pytest.mark.anyio
async def test_iban_valid_de(client):
    resp = await client.get("/iban/validate", params={"iban": "DE89370400440532013000"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["country_code"] == "DE"
    assert data["bank_code"] == "37040044"
    assert data["bic"] is not None


@pytest.mark.anyio
async def test_iban_valid_with_spaces(client):
    resp = await client.get("/iban/validate", params={"iban": "DE89 3704 0044 0532 0130 00"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_iban_valid_gb(client):
    resp = await client.post("/iban/validate", json={"iban": "GB29NWBK60161331926819"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["country_code"] == "GB"


@pytest.mark.anyio
async def test_iban_invalid_checksum(client):
    resp = await client.get("/iban/validate", params={"iban": "DE00000000000000000000"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is False


@pytest.mark.anyio
async def test_iban_garbage_input(client):
    resp = await client.get("/iban/validate", params={"iban": "NOTANIBAN"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is False


# ========================== Credit Card ==========================

@pytest.mark.anyio
async def test_cc_visa_valid(client):
    resp = await client.get("/creditcard/validate", params={"number": "4111111111111111"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["card_type"] == "visa"
    assert data["last_four"] == "1111"
    assert data["masked"] == "************1111"


@pytest.mark.anyio
async def test_cc_mastercard(client):
    resp = await client.get("/creditcard/validate", params={"number": "5500000000000004"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["card_type"] == "mastercard"


@pytest.mark.anyio
async def test_cc_amex(client):
    resp = await client.get("/creditcard/validate", params={"number": "378282246310005"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["card_type"] == "amex"


@pytest.mark.anyio
async def test_cc_discover(client):
    resp = await client.get("/creditcard/validate", params={"number": "6011111111111117"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["card_type"] == "discover"


@pytest.mark.anyio
async def test_cc_invalid_luhn(client):
    resp = await client.get("/creditcard/validate", params={"number": "4111111111111112"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False
    assert data["luhn_valid"] is False


@pytest.mark.anyio
async def test_cc_with_spaces(client):
    resp = await client.get("/creditcard/validate", params={"number": "4111 1111 1111 1111"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_cc_with_dashes(client):
    resp = await client.get("/creditcard/validate", params={"number": "4111-1111-1111-1111"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_cc_too_short(client):
    resp = await client.get("/creditcard/validate", params={"number": "411111"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False
    assert "length" in data.get("error", "").lower()


@pytest.mark.anyio
async def test_cc_non_digits(client):
    resp = await client.get("/creditcard/validate", params={"number": "abcdefghijklmnop"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is False


@pytest.mark.anyio
async def test_cc_post(client):
    resp = await client.post("/creditcard/validate", json={"number": "4111111111111111"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


# ========================== VAT ==========================

@pytest.mark.anyio
async def test_vat_germany_valid(client):
    resp = await client.get("/vat/validate", params={"vat_number": "DE123456789"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["country_code"] == "DE"
    assert data["country_name"] == "Germany"


@pytest.mark.anyio
async def test_vat_france_valid(client):
    resp = await client.get("/vat/validate", params={"vat_number": "FR12345678901"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_vat_netherlands_valid(client):
    resp = await client.get("/vat/validate", params={"vat_number": "NL123456789B01"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_vat_invalid_format(client):
    resp = await client.get("/vat/validate", params={"vat_number": "DE12345"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is False


@pytest.mark.anyio
async def test_vat_unsupported_country(client):
    resp = await client.get("/vat/validate", params={"vat_number": "XX123456789"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False
    assert "Unsupported" in data["error"]


@pytest.mark.anyio
async def test_vat_with_spaces(client):
    resp = await client.get("/vat/validate", params={"vat_number": "DE 123 456 789"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_vat_lowercase(client):
    resp = await client.get("/vat/validate", params={"vat_number": "de123456789"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_vat_too_short(client):
    resp = await client.get("/vat/validate", params={"vat_number": "DE"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is False


@pytest.mark.anyio
async def test_vat_post(client):
    resp = await client.post("/vat/validate", json={"vat_number": "ATU12345678"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


# ========================== Postal Code ==========================

@pytest.mark.anyio
async def test_postal_us_valid(client):
    resp = await client.get("/postalcode/validate", params={"code": "10001", "country": "US"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_postal_us_zip_plus4(client):
    resp = await client.get("/postalcode/validate", params={"code": "10001-1234", "country": "US"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_postal_uk_valid(client):
    resp = await client.get("/postalcode/validate", params={"code": "SW1A 1AA", "country": "GB"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_postal_germany_valid(client):
    resp = await client.get("/postalcode/validate", params={"code": "10115", "country": "DE"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_postal_japan_valid(client):
    resp = await client.get("/postalcode/validate", params={"code": "100-0001", "country": "JP"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_postal_canada_valid(client):
    resp = await client.get("/postalcode/validate", params={"code": "K1A 0B1", "country": "CA"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_postal_invalid(client):
    resp = await client.get("/postalcode/validate", params={"code": "ABCDE", "country": "US"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is False


@pytest.mark.anyio
async def test_postal_unsupported_country(client):
    resp = await client.get("/postalcode/validate", params={"code": "12345", "country": "ZZ"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False
    assert "Unsupported" in data["error"]


@pytest.mark.anyio
async def test_postal_countries_list(client):
    resp = await client.get("/postalcode/countries")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 30
    assert "US" in data["countries"]
    assert "GB" in data["countries"]


@pytest.mark.anyio
async def test_postal_post(client):
    resp = await client.post("/postalcode/validate", json={"code": "75001", "country": "FR"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


# ========================== Date ==========================

@pytest.mark.anyio
async def test_date_convert_us_to_iso(client):
    resp = await client.get("/date/convert", params={
        "date": "03/20/2026", "from_format": "MM/DD/YYYY", "to_format": "ISO8601",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"] == "2026-03-20"
    assert data["day_of_week"] == "Friday"


@pytest.mark.anyio
async def test_date_convert_iso_to_eu(client):
    resp = await client.get("/date/convert", params={
        "date": "2026-03-20", "from_format": "ISO8601", "to_format": "DD/MM/YYYY",
    })
    assert resp.status_code == 200
    assert resp.json()["result"] == "20/03/2026"


@pytest.mark.anyio
async def test_date_convert_iso_to_dot(client):
    resp = await client.get("/date/convert", params={
        "date": "2026-03-20", "from_format": "ISO8601", "to_format": "DD.MM.YYYY",
    })
    assert resp.status_code == 200
    assert resp.json()["result"] == "20.03.2026"


@pytest.mark.anyio
async def test_date_convert_invalid_source_format(client):
    resp = await client.get("/date/convert", params={
        "date": "2026-03-20", "from_format": "INVALID", "to_format": "ISO8601",
    })
    assert resp.status_code == 200
    assert "error" in resp.json()


@pytest.mark.anyio
async def test_date_convert_invalid_date_value(client):
    resp = await client.get("/date/convert", params={
        "date": "not-a-date", "from_format": "ISO8601", "to_format": "US",
    })
    assert resp.status_code == 200
    assert "error" in resp.json()


@pytest.mark.anyio
async def test_date_convert_post(client):
    resp = await client.post("/date/convert", json={
        "date": "20/03/2026", "from_format": "DD/MM/YYYY", "to_format": "ISO8601",
    })
    assert resp.status_code == 200
    assert resp.json()["result"] == "2026-03-20"


@pytest.mark.anyio
async def test_date_detect_iso(client):
    resp = await client.get("/date/detect", params={"date": "2026-03-20"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["best_match"] is not None
    assert data["best_match"]["format"] == "ISO8601"
    assert data["ambiguous"] is False


@pytest.mark.anyio
async def test_date_detect_ambiguous(client):
    resp = await client.get("/date/detect", params={"date": "01/02/2026"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ambiguous"] is True
    assert len(data["detected_formats"]) >= 2


@pytest.mark.anyio
async def test_date_detect_no_match(client):
    resp = await client.get("/date/detect", params={"date": "not-a-date"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["best_match"] is None
    assert len(data["detected_formats"]) == 0


@pytest.mark.anyio
async def test_date_detect_post(client):
    resp = await client.post("/date/detect", json={"date": "20.03.2026"})
    assert resp.status_code == 200
    assert resp.json()["best_match"]["format"] == "DD.MM.YYYY"


@pytest.mark.anyio
async def test_date_formats_list(client):
    resp = await client.get("/date/formats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 15
    assert "ISO8601" in data["formats"]


# ========================== Middleware ==========================

@pytest.mark.anyio
async def test_response_time_header(client):
    resp = await client.get("/health")
    assert "X-Response-Time" in resp.headers
    ms = float(resp.headers["X-Response-Time"].replace("ms", ""))
    assert ms < 500  # Should be very fast


@pytest.mark.anyio
async def test_rate_limit_headers(client):
    resp = await client.get("/phone/validate", params={"number": "+14155552671"})
    assert resp.status_code == 200
    assert "X-RateLimit-Limit" in resp.headers
    assert "X-RateLimit-Remaining" in resp.headers
    assert "X-RateLimit-Reset" in resp.headers


@pytest.mark.anyio
async def test_cache_miss_then_hit(client):
    # First request should be MISS
    resp1 = await client.get("/iban/validate", params={"iban": "DE89370400440532013000"})
    assert resp1.status_code == 200
    # Second identical request should be HIT
    resp2 = await client.get("/iban/validate", params={"iban": "DE89370400440532013000"})
    assert resp2.status_code == 200
    assert resp2.headers.get("X-Cache") == "HIT"


@pytest.mark.anyio
async def test_cache_not_applied_to_post(client):
    resp = await client.post("/iban/validate", json={"iban": "DE89370400440532013000"})
    assert resp.status_code == 200
    assert resp.headers.get("X-Cache") is None


@pytest.mark.anyio
async def test_openapi_docs_accessible(client):
    resp = await client.get("/docs")
    assert resp.status_code == 200


@pytest.mark.anyio
async def test_openapi_json(client):
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert data["info"]["title"] == "DataForge"
    assert len(data["paths"]) >= 10
