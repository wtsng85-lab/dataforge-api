# DataForge v2.1.0 — Universal Data Formatter & Validator API

The Swiss Army knife for structured data validation. One API to validate, format, and parse phone numbers, emails, IBANs, credit cards, crypto wallets, passwords, VAT numbers, postal codes, and dates worldwide.

**Zero AI. Zero external APIs. Sub-50ms responses.**

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
```

## API Endpoints (16 endpoints, 9 modules)

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/phone/validate` | Validate phone number, detect carrier/country/timezone |
| GET/POST | `/phone/format` | Format to E.164, international, national, RFC3966 |
| POST | `/phone/bulk-validate` | Validate up to 100 numbers per request |
| GET/POST | `/email/validate` | Syntax check, MX lookup, disposable email detection |
| GET/POST | `/iban/validate` | Validate IBAN, extract BIC and bank name |
| GET/POST | `/creditcard/validate` | Luhn algorithm check, card type detection |
| GET/POST | `/vat/validate` | EU VAT format validation (28 countries + UK) |
| GET/POST | `/postalcode/validate` | Postal/ZIP code validation (30+ countries) |
| GET | `/postalcode/countries` | List supported countries |
| GET/POST | `/date/convert` | Convert between 15+ date formats |
| GET/POST | `/date/detect` | Auto-detect date format |
| GET | `/date/formats` | List supported date formats |
| GET/POST | `/password/analyze` | Strength scoring, entropy, common password check |
| GET/POST | `/crypto/validate` | Bitcoin & Ethereum address validation |
| GET | `/crypto/chains` | List supported blockchains |
| GET | `/health` | Health check with uptime |

## Examples

### Phone
```bash
curl "http://localhost:8000/phone/validate?number=%2B14155552671" -H "X-API-Key: YOUR_KEY"
# {"valid":true,"e164":"+14155552671","country":"San Francisco, CA",...}
```

### Email
```bash
curl "http://localhost:8000/email/validate?email=test@gmail.com" -H "X-API-Key: YOUR_KEY"
# {"valid":true,"is_disposable":false,"mx_found":true,...}
```

### IBAN
```bash
curl "http://localhost:8000/iban/validate?iban=DE89370400440532013000" -H "X-API-Key: YOUR_KEY"
# {"valid":true,"bic":"COBADEFFXXX","bank_name":"Commerzbank",...}
```

### Crypto
```bash
curl "http://localhost:8000/crypto/validate?address=0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18" -H "X-API-Key: YOUR_KEY"
# {"valid":true,"chain":"ethereum","address_type":"account",...}
```

### Password
```bash
curl "http://localhost:8000/password/analyze?password=MyP@ss123!" -H "X-API-Key: YOUR_KEY"
# {"score":71,"strength":"strong","entropy_bits":65.5,...}
```

## Architecture

```
app/
  main.py           # FastAPI app with middleware stack
  config.py         # Settings from .env
  middleware.py      # Auth, rate limiting, caching, timing, versioning
  models.py         # Pydantic request/response schemas
  routers/          # API endpoint handlers
    phone.py, email.py, iban.py, creditcard.py, vat.py,
    postalcode.py, date.py, password.py, crypto.py
  validators/       # Pure logic validators (no I/O)
    phone.py, email.py, iban.py, creditcard.py, vat.py,
    postalcode.py, date.py, password.py, crypto.py
tests/
  test_api.py       # 77 integration tests
```

## Middleware Stack

1. **CORS** — Allow all origins
2. **RapidAPI Auth** — Verify X-RapidAPI-Proxy-Secret or X-API-Key
3. **Rate Limiting** — 120 req/min per client (IP/API key/RapidAPI user)
4. **Response Cache** — GET requests cached 5 min, 10k entries max
5. **Request Timing** — X-Response-Time header on every response
6. **Request ID** — Unique X-Request-ID for traceability
7. **API Version** — X-API-Version header on every response

## Deployment

### Railway (Production)
Auto-deploys from GitHub `master` branch.
```bash
git push origin master  # Triggers Railway auto-deploy
```

Environment variables: `API_KEY`, `RAPIDAPI_PROXY_SECRET`, `PORT=8000`, `ENVIRONMENT=production`

### Docker
```bash
docker build -t dataforge-api .
docker run -p 8000:8000 -e ENVIRONMENT=production dataforge-api
```

## RapidAPI Pricing

| Plan | Requests/mo | Price |
|------|------------|-------|
| Basic (Free) | 500 | $0 |
| Pro | 10,000 | $7.99 |
| Ultra | 100,000 | $24.99 |
| Mega | 1,000,000 | $79.99 |

## Tech Stack

- **FastAPI** (async Python)
- **phonenumbers** — Phone validation
- **schwifty** — IBAN/BIC validation
- **dnspython** — MX record lookup
- **Luhn algorithm** — Credit card validation
- **Base58Check/Bech32** — Bitcoin address validation
- **EIP-55** — Ethereum checksum validation
- **Regex patterns** — VAT, postal codes, email syntax
- **Pure Python** — Date conversion, password analysis

Zero AI/ML. Zero external API calls. Sub-50ms responses.

## License

MIT
