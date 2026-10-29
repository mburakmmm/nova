# Transport Capabilities Matrix

This matrix tracks HTTP capabilities supported by the underlying Nox runtime versus what Nova implements and exposes.

| Capability | Verified stdlib (`nox.http`) | Nova Implemented | Tests | Limitations / Notes |
|---|---|---|---|---|
| **GET Request** | Yes | Yes | `tests/integration/live_http_test.nox` | Fully supported over HTTP/HTTPS |
| **POST Request** | Yes | Yes | `tests/integration/live_http_test.nox` | Supports text body, JSON, forms, and multipart |
| **PUT / PATCH / DELETE / OPTIONS** | Yes (`nox.http.request` in v2.0.31) | Yes (`client.put/patch/delete/options`) | `tests/integration/methods_integration_test.nox` | Native native runtime execution |
| **HEAD Request** | Yes (`nox.http.head` in v2.0.31) | Yes (`client.head()`) | Supported | RFC 7230 §3.3.3: upstream keep-alive body skip recommended |
| **HTTPS Support** | Yes | Yes | `tests/integration/live_http_test.nox` | TLS hostname and certificate verification enabled |
| **Request Timeout** | Yes (`nox.http.HttpTimeoutError` in v2.0.31) | Yes (`Client(timeout_ms=...)` & `nova.TimeoutError`) | `tests/integration/timeout_test.nox` | Native socket-level timeout with immediate connection tear-down |
| **Status Helpers** | Partial (`status: int`) | Yes (`is_success`, `is_error`, etc.) | `tests/unit/response_test.nox` | Full HTTP status classification helpers |
| **raise_for_status** | No | Yes | `tests/unit/response_test.nox` | Opt-in error raising for 4xx/5xx responses |
| **JSON Decoding** | Via `nox.json` | Yes (`resp.json()`) | `tests/unit/response_test.nox` | Strict `DecodeError` on malformed payloads |
| **Binary Body (`Buffer`)** | Yes (`nox.bytes.from_str` in v2.0.31) | Yes (`Response.bytes() -> Buffer`) | `tests/unit/binary_response_test.nox` | Embedded NUL byte preservation and raw Buffer access |
| **Streaming Response** | Memory buffered in runtime | Yes (`StreamResponse` / `client.stream`) | `tests/integration/stream_integration_test.nox` | Chunked text/binary reading, `iter_bytes`, `iter_lines` |
| **SSRF Protection** | No | Yes (`SSRFPolicy`) | `tests/unit/ssrf_test.nox` | Private IP blocklist, cloud metadata, IPv6 evasion, and redirect checks |
| **Case-Insensitive Headers** | `dict[str, str]` | Yes (`Headers`) | `tests/unit/headers_test.nox` | Lookup insensitive, RFC 7230 token/CRLF validation |
| **Query Merging** | Via `nox.url` | Yes | `tests/unit/url_test.nox` | Predictable encoding, fragment stripped, IPv6 literal support |
| **Basic & Bearer Auth** | No | Yes (`BasicAuth`, `BearerAuth`) | `tests/unit/auth_test.nox` | Credential redaction in string representations |
| **Cookie Jar** | No | Yes (`CookieJar`, `Cookie`) | `tests/unit/cookies_test.nox` | RFC 6265 §5.3 acceptance checks, host-only isolation, secure gating |
| **Redirect Control** | Runtime raw 3xx behavior | Yes (`max_redirects`, loop detection) | `tests/integration/redirect_integration_test.nox` | Cross-origin `Authorization` and `Cookie` stripping |
| **Exponential Backoff** | No | Yes (`RetryPolicy`) | `tests/unit/retry_test.nox` | Transient status codes, POST safety guard, Retry-After cap |
| **Multipart Form & File Upload** | No | Yes (`MultipartEncoder`, `MultipartFile`) | `tests/integration/multipart_integration_test.nox` | RFC 7578 multipart MIME streaming and file attachments |
| **Concurrent Execution** | Fiber/Task pool (`spawn` / `Task[T]`) | Verified | `tests/integration/async_concurrency_test.nox` | Multiple non-blocking concurrent requests across fiber scheduler |
| **Connection Pooling** | No (new `std.http.Client` per request) | Documented / Unsupported | N/A | Requires native persistent socket connection pool in Zig runtime |
| **HTTP / SOCKS Proxy** | No | Documented / Unsupported | N/A | Requires native proxy dialer in Zig runtime |
