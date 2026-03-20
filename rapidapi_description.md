# DataForge — Universal Data Formatter & Validator API

## Stop subscribing to 6 different validation APIs.

DataForge is the **Swiss Army knife for structured data validation**. One API, one subscription — validate phone numbers, IBANs, credit cards, VAT numbers, postal codes, and dates worldwide.

### What You Get

| Endpoint | What It Does |
|----------|-------------|
| `/phone/validate` | Validate phone numbers, detect carrier, country, timezone |
| `/phone/format` | Format to E.164, international, national, RFC3966 |
| `/phone/bulk-validate` | Validate up to 100 phone numbers per request |
| `/iban/validate` | Validate IBANs, extract bank code, BIC, bank name |
| `/creditcard/validate` | Luhn check, detect card type (Visa/MC/Amex/Discover) |
| `/vat/validate` | EU VAT number format validation (28 countries + UK) |
| `/postalcode/validate` | Validate ZIP/postal codes for 30+ countries |
| `/date/convert` | Convert between 15+ date formats |
| `/date/detect` | Auto-detect date format with ambiguity flagging |

### Why DataForge?

- **Blazing fast** — Sub-50ms response times, pure logic (no AI/ML overhead)
- **One API** — Replace 6 separate API subscriptions
- **30+ countries** — International postal codes, EU VAT, phone numbers worldwide
- **GET + POST** — Every endpoint supports both methods
- **Bulk operations** — Validate up to 100 items per request

### Use Cases

- **Fintech & Payments** — Validate IBANs and credit cards at checkout
- **E-commerce** — Validate international addresses and phone numbers
- **SaaS Registration** — Clean and normalize user data on signup
- **Data Pipelines** — Bulk validate and convert dates, phones, postal codes
- **CRM Enrichment** — Detect carriers, format phone numbers, validate addresses

### Pricing

| Plan | Requests/mo | Price |
|------|------------|-------|
| Free | 500 | $0 |
| Basic | 10,000 | $7.99 |
| Pro | 100,000 | $24.99 |
| Ultra | 1,000,000 | $79.99 |

### Quick Start (cURL)

```bash
# Validate a phone number
curl "https://dataforge.p.rapidapi.com/phone/validate?number=%2B14155552671" \
  -H "X-RapidAPI-Key: YOUR_KEY"

# Validate an IBAN
curl "https://dataforge.p.rapidapi.com/iban/validate?iban=DE89370400440532013000" \
  -H "X-RapidAPI-Key: YOUR_KEY"

# Validate a credit card
curl "https://dataforge.p.rapidapi.com/creditcard/validate?number=4111111111111111" \
  -H "X-RapidAPI-Key: YOUR_KEY"
```

### Quick Start (Python)

```python
import requests

url = "https://dataforge.p.rapidapi.com/phone/validate"
params = {"number": "+14155552671"}
headers = {"X-RapidAPI-Key": "YOUR_KEY"}

response = requests.get(url, headers=headers, params=params)
print(response.json())
```

### Quick Start (JavaScript)

```javascript
const response = await fetch(
  "https://dataforge.p.rapidapi.com/phone/validate?number=%2B14155552671",
  { headers: { "X-RapidAPI-Key": "YOUR_KEY" } }
);
const data = await response.json();
console.log(data);
```
