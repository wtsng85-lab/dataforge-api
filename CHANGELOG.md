# Changelog

## [2.1.0] - 2026-03-21

### Added
- X-API-Version response header on every request
- Updated README to v2.1.0 with all 16 endpoints documented
- CHANGELOG.md for version tracking

### Changed
- Version bumped to 2.1.0 across codebase

## [2.0.0] - 2026-03-21

### Added
- Email validation endpoint (`/email/validate`) — syntax, MX lookup, disposable detection
- Password analysis endpoint (`/password/analyze`) — entropy, strength scoring, common passwords
- Crypto wallet validation (`/crypto/validate`) — Bitcoin (Base58/Bech32) and Ethereum (EIP-55)
- Request ID middleware (X-Request-ID header)
- GitHub Actions CI/CD pipeline (pytest, Python 3.12)
- 14 new test cases for email, password, crypto, and request ID

### Fixed
- Removed dev mode authentication bypass (security)
- Fixed rate limiter memory leak (dict → TTLCache)
- Phone format error response now includes `valid: false`
- Global exception handler now logs with `logger.exception()`

### Changed
- Total test count: 77 (was 63)
- Version bumped from 1.0.0 to 2.0.0

## [1.0.0] - 2026-03-20

### Added
- Phone number validation, formatting, and bulk validation
- IBAN validation with BIC/bank lookup
- Credit card validation (Luhn, card type detection)
- VAT number validation (28 EU countries + UK)
- Postal code validation (30+ countries)
- Date format conversion and detection (15+ formats)
- RapidAPI authentication middleware
- Rate limiting (120 req/min per client)
- Response caching (5 min TTL, 10k entries)
- Request timing headers
- 63 integration tests
- Docker support
- Railway deployment config
