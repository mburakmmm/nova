# Transport Capabilities Matrix

This matrix tracks HTTP capabilities supported by the underlying Nox runtime versus what Nova implements and exposes.

| Capability | Verified stdlib (`nox.http`) | Nova Implemented | Tests | Limitations / Notes |
|---|---|---|---|---|
| **GET Request** | Yes | Yes | `tests/integration/live_http_test.nox` | Fully supported over HTTP/HTTPS |
| **POST Request** | Yes | Yes | `tests/integration/live_http_test.nox` | Supports text body, JSON, and URL-encoded forms |
| **HTTPS Support** | Yes | Yes | `tests/integration/live_http_test.nox` | TLS hostname and certificate verification enabled |
| **Status Helpers** | Partial (`status: int`) | Yes (`is_success`, `is_error`, etc.) | `tests/unit/response_test.nox` | Full HTTP status classification helpers |
| **raise_for_status** | No | Yes | `tests/unit/response_test.nox` | Opt-in error raising for 4xx/5xx responses |
| **JSON Decoding** | Via `nox.json` | Yes (`resp.json()`) | `tests/unit/response_test.nox` | Strict `DecodeError` on malformed payloads |
| **Case-Insensitive Headers** | `dict[str, str]` | Yes (`Headers`) | `tests/unit/headers_test.nox` | Lookup insensitive, CRLF injection guarded |
| **Query Merging** | Via `nox.url` | Yes | `tests/unit/url_test.nox` | Predictable encoding, fragment stripped |
| **Basic & Bearer Auth** | No | Yes (`BasicAuth`, `BearerAuth`) | `tests/unit/auth_test.nox` | Credential redaction in string reprs |
| **Cookie Jar** | No | Yes (`CookieJar`) | `tests/unit/cookies_test.nox` | Per-client isolation, `Set-Cookie` extraction |
| **Exponential Backoff** | No | Yes (`RetryPolicy`) | `tests/unit/retry_test.nox` | Transient status codes, POST safety guard |
| **PUT / PATCH / DELETE** | No (not exported in `noxrt.o`) | Explicit `UnsupportedFeatureError` | `tests/integration/unsupported_methods_test.nox` | Awaiting upstream `nox_http_request_raw` export |
| **Request Timeout** | No | Documented / Unsupported | N/A | Underlying `std.http.Client` lacks client timeout hook |
| **Streaming / Binary** | No | Documented / Unsupported | N/A | `HttpResponse.body` in runtime is `str` |
| **Connection Pooling** | No | Documented / Unsupported | N/A | Requires native transport socket management |
| **Async Client** | Synchronous worker thread | Documented / Unsupported | N/A | Fiber-cooperative, but synchronous client API |
