# DataForge — Universal Data Formatter & Validator API

The Swiss Army knife for structured data validation. One API to validate, format, and parse phone numbers, IBANs, credit cards, VAT numbers, postal codes, and dates worldwide.

## Quick Start

```bash
# Setup
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
source .venv/Scripts/activate    # Windows
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload

# Test
pip install pytest httpx anyio pytest-anyio
pytest tests/ -v

# CLI
python cli.py setup   # Setup environment
python cli.py dev     # Dev server with reload
python cli.py test    # Run tests
python cli.py spotlight  # Open /docs in browser
python cli.py ship    # Deploy to Railway
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/phone/validate` | Validate phone number, detect carrier/country/timezone |
| GET | `/phone/format` | Format to E.164, international, national, RFC3966 |
| POST | `/phone/bulk-validate` | Validate up to 100 numbers per request |
| GET/POST | `/iban/validate` | Validate IBAN, extract BIC and bank name |
| GET/POST | `/creditcard/validate` | Luhn algorithm check, card type detection |
| GET/POST | `/vat/validate` | EU VAT format validation (28 countries + UK) |
| GET/POST | `/postalcode/validate` | Postal/ZIP code validation (30+ countries) |
| GET | `/postalcode/countries` | List supported countries |
| GET/POST | `/date/convert` | Convert between 15+ date formats |
| GET/POST | `/date/detect` | Auto-detect date format |
| GET | `/date/formats` | List supported date formats |
| GET | `/health` | Health check with uptime |

## Examples

### Phone
```bash
curl "http://localhost:8000/phone/validate?number=%2B14155552671"
# {"valid":true,"e164":"+14155552671","country":"San Francisco, CA",...}
```

### IBAN
```bash
curl "http://localhost:8000/iban/validate?iban=DE89370400440532013000"
# {"valid":true,"country_code":"DE","bic":"COBADEFFXXX","bank_name":"Commerzbank",...}
```

### Credit Card
```bash
curl "http://localhost:8000/creditcard/validate?number=4111111111111111"
# {"valid":true,"card_type":"visa","luhn_valid":true,...}
```

### Date Convert
```bash
curl "http://localhost:8000/date/convert?date=03/20/2026&from_format=MM/DD/YYYY&to_format=ISO8601"
# {"result":"2026-03-20","day_of_week":"Friday",...}
```

## Architecture

```
app/
  main.py           # FastAPI app with middleware stack
  config.py         # Settings from .env
  middleware.py      # Auth, rate limiting, caching, timing
  models.py         # Pydantic request/response schemas
  routers/          # API endpoint handlers
    phone.py, iban.py, creditcard.py, vat.py, postalcode.py, date.py
  validators/       # Pure logic validators (no I/O)
    phone.py, iban.py, creditcard.py, vat.py, postalcode.py, date.py
tests/
  test_api.py       # 32+ integration tests
```

## Middleware Stack

1. **CORS** — Allow all origins
2. **RapidAPI Auth** — Verify X-RapidAPI-Proxy-Secret or X-API-Key
3. **Rate Limiting** — 120 req/min per client (IP/API key/RapidAPI user)
4. **Response Cache** — GET requests cached 5 min, 10k entries max
5. **Request Timing** — X-Response-Time header on every response

## Deployment

### Railway
```bash
railway login
railway init
railway up
# Set env vars: ENVIRONMENT=production, RAPIDAPI_PROXY_SECRET=xxx
```

### Docker
```bash
docker build -t dataforge-api .
docker run -p 8000:8000 -e ENVIRONMENT=production dataforge-api
```

## RapidAPI Pricing

| Plan | Requests/mo | Price |
|------|------------|-------|
| Free | 500 | $0 |
| Basic | 10,000 | $7.99 |
| Pro | 100,000 | $24.99 |
| Ultra | 1,000,000 | $79.99 |

## Tech Stack

- **FastAPI** (async Python)
- **phonenumbers** — Phone validation
- **schwifty** — IBAN/BIC validation
- **Luhn algorithm** — Credit card validation
- **Regex patterns** — VAT, postal codes
- **Pure Python** — Date conversion/detection

Zero AI/ML. Zero external API calls. Sub-50ms responses.

## License

MIT
