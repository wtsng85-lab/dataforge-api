"""Comprehensive API tests for DataForge."""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


# --- Health ---

@pytest.mark.anyio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "DataForge"


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# --- Phone ---

@pytest.mark.anyio
async def test_phone_validate_valid(client):
    resp = await client.get("/phone/validate", params={"number": "+14155552671"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["country_code"] == 1
    assert data["e164"] == "+14155552671"


@pytest.mark.anyio
async def test_phone_validate_with_country(client):
    resp = await client.get("/phone/validate", params={"number": "0201234567", "country_code": "NL"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True


@pytest.mark.anyio
async def test_phone_validate_invalid(client):
    resp = await client.get("/phone/validate", params={"number": "notaphone"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False


@pytest.mark.anyio
async def test_phone_format_e164(client):
    resp = await client.get("/phone/format", params={"number": "+14155552671", "format": "international"})
    assert resp.status_code == 200
    data = resp.json()
    assert "+" in data["formatted"]


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


# --- IBAN ---

@pytest.mark.anyio
async def test_iban_valid(client):
    resp = await client.get("/iban/validate", params={"iban": "DE89370400440532013000"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["country_code"] == "DE"
    assert data["bank_code"] == "37040044"


@pytest.mark.anyio
async def test_iban_valid_with_spaces(client):
    resp = await client.get("/iban/validate", params={"iban": "DE89 3704 0044 0532 0130 00"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


@pytest.mark.anyio
async def test_iban_invalid(client):
    resp = await client.get("/iban/validate", params={"iban": "DE00000000000000000000"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False


@pytest.mark.anyio
async def test_iban_post(client):
    resp = await client.post("/iban/validate", json={"iban": "GB29NWBK60161331926819"})
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


# --- Credit Card ---

@pytest.mark.anyio
async def test_cc_visa_valid(client):
    resp = await client.get("/creditcard/validate", params={"number": "4111111111111111"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["card_type"] == "visa"
    assert data["last_four"] == "1111"


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


# --- VAT ---

@pytest.mark.anyio
async def test_vat_germany_valid(client):
    resp = await client.get("/vat/validate", params={"vat_number": "DE123456789"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["country_code"] == "DE"


@pytest.mark.anyio
async def test_vat_france_valid(client):
    resp = await client.get("/vat/validate", params={"vat_number": "FR12345678901"})
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


# --- Postal Code ---

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


# --- Date ---

@pytest.mark.anyio
async def test_date_convert_us_to_iso(client):
    resp = await client.get("/date/convert", params={
        "date": "03/20/2026",
        "from_format": "MM/DD/YYYY",
        "to_format": "ISO8601",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"] == "2026-03-20"


@pytest.mark.anyio
async def test_date_convert_iso_to_eu(client):
    resp = await client.get("/date/convert", params={
        "date": "2026-03-20",
        "from_format": "ISO8601",
        "to_format": "DD/MM/YYYY",
    })
    assert resp.status_code == 200
    assert resp.json()["result"] == "20/03/2026"


@pytest.mark.anyio
async def test_date_convert_invalid_format(client):
    resp = await client.get("/date/convert", params={
        "date": "2026-03-20",
        "from_format": "INVALID",
        "to_format": "ISO8601",
    })
    assert resp.status_code == 200
    assert "error" in resp.json()


@pytest.mark.anyio
async def test_date_detect_iso(client):
    resp = await client.get("/date/detect", params={"date": "2026-03-20"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["best_match"] is not None
    assert data["best_match"]["format"] == "ISO8601"


@pytest.mark.anyio
async def test_date_detect_ambiguous(client):
    # 01/02/2026 could be Jan 2 or Feb 1
    resp = await client.get("/date/detect", params={"date": "01/02/2026"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ambiguous"] is True
    assert len(data["detected_formats"]) >= 2


# --- Latency check ---

@pytest.mark.anyio
async def test_response_time_header(client):
    resp = await client.get("/health")
    assert "X-Response-Time" in resp.headers
