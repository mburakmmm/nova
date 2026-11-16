# Transport Capabilities Matrix

This matrix tracks HTTP capabilities supported by the underlying Nox runtime versus what Nova implements and exposes.

| Capability | Verified stdlib (`nox.http`) | Nova Implemented | Tests | Limitations / Notes |
|---|---|---|---|---|
| **GET Request** | Yes | Yes | `tests/integration/live_http_test.nox` | Fully supported over HTTP/HTTPS |
| **POST Request** | Yes | Yes | `tests/integration/live_http_test.nox` | Supports text body, JSON, forms, and multipart |
| **PUT / PATCH / DELETE / OPTIONS** | Yes (`nox.http.request` in v2.0.31) | Yes (`client.put/patch/delete/options`) | `tests/integration/methods_integration_test.nox` | Native runtime execution |
| **HEAD Request** | Yes (`nox.http.head` in v2.0.31, v2.1.2) | Yes (`client.head()`) | `tests/integration/methods_integration_test.nox` | Keep-alive hang resolved upstream in Nox v2.1.2; body skipped cleanly |
| **HTTPS Support** | Yes | Yes | `tests/integration/live_http_test.nox` | TLS hostname and certificate verification enabled |
| **Request Timeout** | Yes (`nox.http.HttpTimeoutError` in v2.0.31) | Yes (`Client(timeout_ms=...)` & `nova.TimeoutError`) | `tests/integration/timeout_test.nox` | Native socket-level timeout with immediate connection tear-down |
| **Status Helpers** | Partial (`status: int`) | Yes (`is_success`, `is_error`, etc.) | `tests/unit/response_test.nox` | Full HTTP status classification helpers |
| **raise_for_status** | No | Yes | `tests/unit/response_test.nox` | Opt-in error raising for 4xx/5xx responses |
| **JSON Decoding** | Via `nox.json` | Yes (`resp.json()`) | `tests/unit/response_test.nox` | Strict `DecodeError` on malformed payloads |
| **Binary Body (`Buffer`)** | Yes (`nox.bytes.from_str` in v2.0.31) | Yes (`Response.bytes() -> Buffer`) | `tests/unit/binary_response_test.nox` | Embedded NUL byte preservation and raw Buffer access |
| **Streaming Response** | Yes (`nox.http.stream` in v2.0.69) | Yes (`StreamResponse` / `client.stream`) | `tests/integration/stream_integration_test.nox` | Zero-copy socket streaming, `read_chunk()`, context manager `with` |
| **Large File Transfer** | Yes (`nox.transfer` in v2.0.69) | Yes (`nova.transfer` / `download_file`, `upload_file`) | `tests/integration/file_transfer_integration_test.nox` | Streaming file download and upload directly to/from disk |
| **Connection Pooling** | Yes (`nox.http.client_pool` in v2.0.126) | Yes (`client.set_connection_pool`, `get_idle_connections`) | `tests/integration/pool_integration_test.nox` | **Process-wide** pool (not per-Client); reuses open TCP/TLS connections per origin |
| **HTTP / HTTPS Proxy** | Yes (`v2.0.129`) | Yes (Transparent upstream support) | Upstream verified | Automatically honors `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY` with `CONNECT` tunnel |
| **SSRF Protection** | No | Yes (`SSRFPolicy`) | `tests/unit/ssrf_test.nox` | Private IP blocklist, cloud metadata, IPv6 evasion, and redirect checks |
| **Case-Insensitive Headers** | `dict[str, str]` | Yes (`Headers`) | `tests/unit/headers_test.nox` | Lookup insensitive, RFC 7230 token/CRLF validation |
| **Query Merging** | Via `nox.url` | Yes | `tests/unit/url_test.nox` | Predictable encoding, fragment stripped, IPv6 literal support |
| **Basic & Bearer Auth** | No | Yes (`BasicAuth`, `BearerAuth`) | `tests/unit/auth_test.nox` | Credential redaction in string representations |
| **Cookie Jar** | No | Yes (`CookieJar`, `Cookie`) | `tests/unit/cookies_test.nox` | RFC 6265 §5.3 acceptance checks, host-only isolation, secure gating |
| **Redirect Control** | Runtime raw 3xx behavior | Yes (`max_redirects`, loop detection) | `tests/integration/redirect_integration_test.nox` | Cross-origin `Authorization` and `Cookie` stripping |
| **Exponential Backoff** | No | Yes (`RetryPolicy`) | `tests/unit/retry_test.nox` | Transient status codes, POST safety guard, Retry-After cap |
| **Multipart Form & File Upload** | No | Yes (`MultipartEncoder`, `MultipartFile`) | `tests/integration/multipart_integration_test.nox` | RFC 7578 multipart MIME streaming and file attachments |
| **Concurrent Execution** | Fiber/Task pool (`spawn` / `Task[T]`) | Verified (Method & import spawn supported in v2.1.5) | `tests/integration/async_concurrency_test.nox` | Concurrent non-blocking requests across task pool |
| **Transport Injection** | n/a | Yes (`Transport`, `Client.set_transport`, `MockTransport`) | `tests/unit/transport_injection_test.nox` | Network-free end-to-end tests of retry/redirect/cookie flows |
| **DNS-aware SSRF** | No DNS API, no IP pinning | Partial (`HostResolver`, `strict_hostnames`) | `tests/unit/ssrf_advanced_test.nox` | DNS-rebinding TOCTOU remains (needs runtime connect-to-IP) |
| **Lazy Streaming** | `HttpStream.read_chunk` | Yes (`read_line`, `for_each_line`, `for_each_chunk`) | `tests/unit/stream_lazy_test.nox` | `iter_lines`/`iter_bytes` buffer the whole body |
| **Multiple Set-Cookie** | No (runtime keeps last value) | Ready (`\n`-joined multi-values) | `tests/unit/cookies_advanced_test.nox` | Needs runtime fix (NOX_LIMITATIONS §16) |
| **Cookie Expiry / PSL** | n/a | Yes (`Expires`, `Max-Age`, O(1) hash map over 8,650+ Mozilla PSL suffixes) | `tests/unit/cookies_advanced_test.nox`, `tests/integration/mn_worker_stress_test.nox` | Full Mozilla PSL loaded into frozen O(1) dict |
| **Retry jitter / HTTP-date Retry-After** | n/a | Yes | `tests/unit/retry_advanced_test.nox` | Jitter is opt-in |
| **Streaming Request Upload** | Yes (`nox.http.stream_upload`) | Yes (`UploadStream`, `Client.stream_upload`, `nova.stream_upload`) | `tests/unit/stream_upload_http3_test.nox`, `tests/integration/stream_upload_integration_test.nox` | Supports chunked (`-1`) and fixed `Content-Length`; requires `POST`/`PUT`/`PATCH` |
| **HTTP/3 (QUIC / Alt-Svc)** | Yes (`nox.http.set_http3` in v2.1.116) | Yes (`Client.set_http3`, `nova.set_http3`, `http3_scope`) | `tests/unit/stream_upload_http3_test.nox`, `tests/integration/stream_upload_integration_test.nox` | **Process-wide** toggle; requires OpenSSL 3.5+ on desktop; silently falls back to HTTP/2 / HTTP/1.1 |
| **Brotli (`Content-Encoding: br`)** | Desktop opt-in (`nox.brotli`) / None on WASM+mobile | Opt-in `brotli_codec.BrotliDecoder`; protected pure-Nox `FallbackContentDecoder` | `tests/unit/brotli_desktop_test.nox`, `tests/unit/codec_fallback_test.nox` | Desktop (`macOS`/`Linux`/`Windows`) only; WASM & mobile fail explicitly via `UnsupportedFeatureError` |
| **Fast JSON Adapter (`yyjson`)** | Desktop opt-in (`nox.yyjson`) / Pure `nox.json` everywhere | Opt-in `yyjson_adapter.YyJsonReader`; guaranteed `NoxJsonReader` fallback | `tests/unit/json_adapters_test.nox` | Same `JsonReader`/`JsonDocument` contract across desktop & WASM/mobile |
| **WASM & Mobile Core Build** | Core `noxc check/build` | Yes (`nova.nox` 100% pure-Nox) | CI (`wasm32-wasi`, `wasm32-freestanding`, `ios-arm64`, `android-arm64`) | Opt-in `brotli_codec` and `yyjson_adapter` must not be imported on WASM/mobile |
