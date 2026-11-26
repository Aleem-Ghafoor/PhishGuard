# Scanner API Hardening — PR #27

## Scope

This document records the scanner endpoint changes introduced by PR #27 (`fix/scanner-hardening`). The scan endpoint remains public for both guests and authenticated users.

## Request flow

1. The client sends a POST request to the scan API.
2. A per-client-IP limiter checks the request counter.
3. Requests above the configured limit are rejected with HTTP 429.
4. The URL validator checks input, HTTP/HTTPS scheme, hostname, and port syntax/range.
5. Valid URLs are passed to the scanner service and ML predictor.
6. Authenticated successful scans are saved to scan history; guest scans are not persisted.
7. Unexpected inference errors are logged server-side and a generic error response is returned.

## Rate-limit policy

| Setting | Value |
|---|---:|
| Maximum requests | 10 |
| Window | 60 seconds |
| Key basis | Client IP digest |
| Excess response | HTTP 429 |

The limiter uses Django's cache framework. The PR configures local-memory cache for development. Local-memory cache is process-local and is not sufficient for consistent enforcement across multiple workers or instances. Use a shared cache backend (for example Redis) in such deployments. Proxy/load-balancer deployments must also configure and verify trusted client-IP handling; do not blindly trust arbitrary forwarded headers.

## Validation and error handling

The validator accepts HTTP and HTTPS URLs and rejects missing/unsupported schemes, missing hostnames, malformed input, non-numeric/out-of-range ports, empty ports, and whitespace in the URL. Unexpected scan exceptions are recorded with server-side stack traces; the client receives a generic message rather than internal exception details.

## Tests and validation status

PR #27 adds automated tests for URL validation, successful scan API responses, the per-IP request limit, and generic error handling with server-side logging. The PR description explicitly states that the tests have **not yet been executed locally**. Run:

```bash
python manage.py test scanner
```

Do not describe these tests as passing until the command has been run and its result reviewed.

## Deployment boundary

The current cache setting is for local development. A production deployment should use a shared cache, configure trusted proxy/client-IP handling, and verify rate-limit behaviour under concurrent requests and across workers. PR #27 does not claim production deployment or end-to-end browser validation.
