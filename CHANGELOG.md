# Changelog

All notable changes to **Nova** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.1] - 2026-11-12

### Security & Stream Hardening (external audit of v0.6.0)
- **Streaming Line-Length Ordering Bug Fixed (P1)**: `StreamResponse.read_line()` now enforces `max_line_bytes` immediately upon finding a newline (`nl >= 0`) and also on EOF tails without newline. Previously, a single chunk containing a newline on an over-long line could return without raising `DecodeError`.
- **SSRF Allowlist DNS Rebinding Prevention (P1)**: In `ssrf.nox`, `validate_target()` now validates resolved IPs against private/loopback/link-local ranges even for explicitly allowlisted hostnames when a `HostResolver` is configured (`skip_dns_for_allowlist: bool = False`). Added `set_skip_dns_for_allowlist(bool)` for intentional private internal hosts.
- **Pre-hardened Safe Client Factory (P2)**: Added `create_safe_client()` and `nova.safe_client()` with default `SSRFPolicy` active, `raise_for_status=True`, default 15s timeout, and strict 3-redirect limit.
- **Public Suffix List (PSL) Expansion (P2)**: Expanded curated subset in `psl.nox` with additional national ccTLD/SLDs (`.gov.uk`, `.ac.uk`, `.org.uk`, `.com.tr`, `.edu.tr`, `.gov.tr`, `.co.jp`, `.ne.jp`, `.com.br`, `.bel.tr`, `.k12.tr`, etc.) and common cloud platforms (`deno.dev`, `supabase.co`, `render.com`, `modal.run`, `koyeb.app`, `pages.dev`).
- **Concurrency & Stress Testing (P2)**: Added `tests/integration/concurrency_stress_test.nox` testing concurrent fiber tasks with `MockTransport` and streaming lines across independent tasks.
- **Test Suite**: 32 tests passing with 0 failures (`32 passed, 0 failed`).

## [0.6.0] - 2026-11-11

### Security & Standards Hardening (external audit of v0.5.0)
- **CI fixed (P0)**: `tests/fixtures/` was an empty directory not tracked by git → `file_transfer_integration_test` failed with `FsError` on Linux CI. Added `tests/fixtures/.gitkeep`.
- **SSRF (P0/P1)** — `ssrf.nox` rewritten:
  - Real IPv4/IPv6 parser (`parse_ip`, `classify_ip`): inet_aton forms (`2130706433`, `0x7f000001`, `0177.0.0.1`, `127.1`), compressed/expanded IPv6, zone IDs, mapped/compatible/translated/NAT64/6to4 embedded IPv4, ULA, site-local, multicast, documentation, Teredo. String-prefix checks removed (no more `fc.example.com` false positives).
  - **DNS-resolution validation**: `HostResolver` / `StaticResolver`, `SSRFPolicy.set_resolver()`, `validate_resolved()` — every resolved IP is validated, fail-closed on empty/invalid answers.
  - `SSRFPolicy.set_strict_hostnames()`: only IP literals and allow-listed hostnames pass.
  - Trailing-dot `localhost.` bypass closed.
  - Remaining DNS-rebinding TOCTOU window documented (needs Nox runtime support, `NOX_LIMITATIONS.md` §14).
- **Redirect (P1)**: `Cookie` header (including manually configured) is now stripped on every cross-origin hop; jar cookies are re-applied for the new URL only. Verified by a real `Client.send()` flow and by a mutation check.
- **CookieJar (P1)**: `Expires` + `Max-Age` (precedence, deletion, expired never sent, `purge_expired`), embedded curated Public Suffix subset + `add_public_suffix()`, RFC 6265 default-path, `SameSite` recorded, multiple `Set-Cookie` values (`\n`-joined) processed independently.
- **Headers**: `set_multi()`, `get_all()`, `response_headers_from_dict()` (request-side CRLF defense unchanged).
- **Streaming (P1)**: lazy `read_line()`, `for_each_line(LineHandler)`, `for_each_chunk(ChunkHandler)` with `max_line_bytes`; `iter_lines`/`iter_bytes` documented as buffering.
- **Retry (P2)**: opt-in `full`/`equal` jitter (deterministic sample for tests), `Retry-After` HTTP-date (new `httpdate.nox`), overflow-safe backoff, one-year Retry-After ceiling.
- **Architecture (P2)**: `Transport` interface, `Client.set_transport()`, in-memory `MockTransport` → network-free end-to-end tests.
- **Pool (P2)**: process-wide scope documented and exposed (`Client.connection_pool_scope()`).
- New Nox limitations recorded: §14 DNS API / IP pinning, §15 lazy iterators, §16 duplicate response headers, §17 per-client pool, §18 notes.
- **Tests**: 10 new test files (httpdate, ssrf_advanced, cookies_advanced, retry_advanced, redirect_security, stream_lazy, transport_injection …).

## [0.5.0] - 2026-11-11

### Added — Phase 5 Native Socket Streaming, Connection Pooling & File Transfer
- **Native Zero-Copy Socket Streaming (`stream.nox`)**:
  - Direct integration with Nox standard library `nox.http.stream()` and `HttpStream`.
  - True chunked streaming over live socket connections without buffering entire responses into memory.
  - Implemented Pythonic context manager support: `with client.stream("GET", url) as s:` (`__enter__` and `__exit__`).
  - `StreamResponse.read_chunk()` and `read_all()` directly consume live socket chunks with fallback to in-memory buffers when testing.
  - Added socket lifecycle control via `StreamResponse.close()`.
  - Verified live in `tests/integration/stream_integration_test.nox`.
- **HTTP Connection Pooling & Keep-Alive (`client.nox`, `nova.nox`)**:
  - Leverages Nox v2.0.126 / v2.0.128 connection pooling primitives (`nox.http.client_pool`, `nox.http.client_idle_connections`).
  - Added `Client.set_connection_pool(max_idle, idle_timeout_ms)` and `Client.get_idle_connections()`.
  - Added top-level convenience functions `nova.set_connection_pool()` and `nova.idle_connections()`.
  - Dramatically reduces latency across consecutive requests by reusing open TCP/TLS connections.
  - Verified in `tests/integration/pool_integration_test.nox`.
- **Large File Streaming Transfer (`transfer.nox`, `nova/transfer.nox`)**:
  - Added dedicated streaming file transfer module backed by `nox.transfer.download_to_file` and `nox.transfer.upload_file`.
  - Efficiently downloads directly from socket to filesystem and streams file uploads directly to socket without RAM blowup.
  - Exposes `download_file(cli, url, target_path, ...)` and `upload_file(cli, url, source_path, method, ...)`.
  - Top-level shortcuts in `nova.nox`: `nova.download_to_file(...)` and `nova.upload_file(...)`.
  - Verified in `tests/integration/file_transfer_integration_test.nox`.
- **Transparent Proxy Support**:
  - Automatic detection and support for standard proxy environment variables (`HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`) with secure `CONNECT` tunneling provided by Nox v2.0.129.
- **Resolved Upstream Limitations**:
  - Verified `HEAD` request keep-alive hang resolution (`http_client.zig:909` in Nox v2.1.2) with live `HEAD 200` integration test.
  - Verified `spawn` class method thunk synthesis (`checker.zig:2912` in Nox v2.1.5) and imported `async def` recognition.
  - Documented compiler ARC codegen heap temporary workaround in `NOX_LIMITATIONS.md`.
- **Test Suite Expansion**:
  - 24 tests passing (`24 passed, 0 failed (24 total)` in `noxc test`).

## [0.4.0] - 2026-10-29

### Added — Phase 4 SSRF Protection Shield & Streaming Reader
- **SSRF Protection Shield (`ssrf.nox`)**:
  - `SSRFPolicy` defense-in-depth shield enforcing strict origin restrictions.
  - Blocks RFC 1918 private IPv4 networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
  - Blocks loopback (`127.0.0.0/8`, `0.0.0.0/8`, `localhost`, `*.localhost`).
  - Blocks cloud provider metadata endpoints (`169.254.169.254`, `169.254.0.0/16`, `metadata.google.internal`, `instance-data`).
  - Blocks restricted IPv6 addresses (loopback `[::1]`, link-local `fe80::/10`, unique-local `fc00::/7`).
  - Blocks IPv4-mapped IPv6 evasion attempts (`::ffff:127.0.0.1`, `::ffff:169.254.169.254`).
  - Integrated into initial requests and redirect hops (`Client.send()`), raising `SSRFSecurityError`.
  - Comprehensive unit test suite in `tests/unit/ssrf_test.nox`.
- **Streaming Response Reader (`stream.nox`)**:
  - `StreamResponse` model supporting incremental consumption of HTTP payloads.
  - `read_chunk(chunk_size)` and `read_chunk_bytes(chunk_size) -> Buffer` for partial reads.
  - `iter_bytes(chunk_size) -> list[Buffer]` for block-by-block processing.
  - `iter_lines() -> list[str]` with CRLF newline splitting.
  - Added `Client.stream()` and top-level `nova.stream()`.
  - Unit tests in `tests/unit/stream_test.nox` and live stream integration test against `httpbin.org/stream/5` in `tests/integration/stream_integration_test.nox`.
- **Async Concurrency Integration**:
  - Verified non-blocking concurrent request execution using Nox's native fiber scheduler (`spawn` and `Task[T]`).
  - Added `tests/integration/async_concurrency_test.nox`.
- **Compiler Limitations & Insights Documented**:
  - Documented `spawn` class method limitation and cross-module import symbol behavior in `NOX_LIMITATIONS.md`.
  - Documented `HEAD` keep-alive socket hang root cause.
- **Test Suite Expansion**:
  - 22 tests passing (`22 passed, 0 failed (22 total)` in `noxc test`).

## [0.3.0] - 2026-10-29

### Added — Phase 3 Transport Expansion
- **Full HTTP Method Suite**:
  - Live native support for `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS` via Nox stdlib `nox.http.request()`.
  - Added `Client.put()`, `Client.patch()`, `Client.delete()`, `Client.head()`, `Client.options()`.
  - Added top-level convenience functions: `nova.put()`, `nova.patch()`, `nova.delete()`, `nova.head()`, `nova.options()`, `nova.request()`.
  - Live verified against httpbin in `tests/integration/methods_integration_test.nox`.
- **True Socket Request Timeout**:
  - `Client(timeout_ms=...)` and request-level `timeout_ms` parameter.
  - Native runtime socket shutdown via `nox.http.HttpTimeoutError` mapped to `nova.TimeoutError` (subclass of `TransportError`).
  - No fake post-return timing wrapper; verified against live `/delay/5` endpoint in `tests/integration/timeout_test.nox`.
- **Binary Body Access (`Buffer`)**:
  - Embedded NUL byte preservation and raw bytes access.
  - Added `Response.bytes() -> Buffer` utilizing stdlib `nox.bytes.from_str()`.
  - Verified in `tests/unit/binary_response_test.nox`.
- **Test Suite Expansion**:
  - 18 unit and integration tests passing (`18 passed, 0 failed`).

## [0.2.2] - 2026-10-26

### Security & Protocol Hardening (Reviewer Audit v0.2.2 Fixes)
- **Cookie Acceptance Validation (RFC 6265 §5.3 Step 5)**:
  - Validates that the responding request-host domain-matches the cookie's `Domain` attribute during extraction.
  - Rejects attempts by unrelated domains (e.g. `evil.example.net` setting `Domain=example.com`) or parent origins setting subdomains.
  - Rejects public suffix / top-level domains without dots (e.g., `Domain=com`, `Domain=org`).
- **Host-Only Cookie Isolation (RFC 6265 §5.3 Step 6)**:
  - Added `host_only: bool` to `Cookie` model.
  - Cookies set without an explicit `Domain` attribute are marked host-only and are strictly restricted to the exact originating host (never sent to subdomains).
- **RFC 3986 §5.2 Relative Reference Resolution**:
  - Rewrote URL reference resolution to strictly follow RFC 3986 §5.2.
  - Origin-relative paths (`/get`) replace the path component of the base URL, resolving `https://httpbin.org/redirect/1` with `/get` to `https://httpbin.org/get`.
  - Directory-relative paths (`users`) correctly append to base path directories (`https://api.example.com/v1/users`).
- **End-to-End Real Redirect Integration Test**:
  - Added `tests/integration/redirect_integration_test.nox` verifying live 302 -> 200 resolution, `max_redirects = 0` raw 302 preservation, and `max_redirects = 1` redirect loop defense.
- **Retry-After Upper Bound Protection**:
  - Capped `Retry-After` delay in `Client.send()` to `policy.max_backoff_ms` (default 30,000 ms) to prevent sleep DoS from malicious servers.
- **Header Value RFC 7230 §3.2 Validation**:
  - Rejects all ASCII control characters (`0x00 - 0x1F` except HTAB `0x09`) and DEL (`0x7F`) in header values.
- **Multipart Memory Documentation**:
  - Clarified in `multipart.nox` and documentation that current multipart file uploading operates with in-memory string buffering, pending upstream runtime binary buffer support.

## [0.2.1] - 2026-10-26

### Security & Protocol Hardening (Reviewer Audit Fixes)
- **RFC 6265 Cookie Isolation & Management (`cookies.nox`)**:
  - `Cookie` class with `name`, `value`, `domain`, `path`, `secure`, `http_only`.
  - Composite key `(name, domain, path)` allowing distinct cookies with the same name across domains or paths.
  - Subdomain dot-matching per RFC 6265 §5.1.3 (rejecting suffixes like `notexample.com` matching `example.com`).
  - Path-matching verification per RFC 6265 §5.1.4.
  - HTTPS-only transmission gating for `secure` cookies.
- **RFC 7230 §3.2.6 Header Token Validation (`headers.nox`)**:
  - Strict validation of header names: only allowed US-ASCII visible characters and RFC 7230 delimiters.
  - Rejection of delimiters `()<>@,;:\"/[]?={}` and whitespace in header names.
  - CRLF and NUL character injection prevention in both names and values.
- **RFC 3986 URL Normalization & IPv6 Support (`url.nox`)**:
  - Dot-segment path normalization (`normalize_path`) resolving `.` and `..` relative segments cleanly.
  - Full preservation of IPv6 bracketed literal hosts (e.g., `http://[::1]:8080/api`).
- **Client-Side Redirect Security (`client.nox`)**:
  - Redirect loop detection and configurable `max_redirects` limit (`Client(max_redirects=5)`).
  - Cross-origin credential defense: automatically strips `Authorization` and `Cookie` headers when following redirects across origins (`not is_same_origin(req.url, next_url)`).
- **Retry Backoff Calculation Fix (`retry.nox`)**:
  - Fixed initial retry delay calculation so `attempt <= 1` returns the exact `backoff_factor_ms` rather than double.

## [0.2.0] - 2026-10-26

### Added
- **Multipart Form-Data & File Uploads (`multipart.nox`)**:
  - `MultipartEncoder`: RFC 7578 compliant boundary generator and payload builder.
  - `MultipartFile`: In-memory file container with custom MIME types.
  - `file_from_path()`: Automatic disk file loader using `nox.fs.read_to_string`.
  - `Client.post_multipart()` and `nova.post_multipart()` convenience APIs.
- **Retry-After Header Support**:
  - Respects HTTP 429 / 503 `Retry-After` header in seconds per AGENTS.md §13.
- **Multipart Test Suite**:
  - `tests/unit/multipart_test.nox`: Unit verification for boundary framing and file loaders.
  - `tests/integration/multipart_integration_test.nox`: Live multipart upload against httpbin.
- **New Example**:
  - `examples/multipart_upload.nox`.

## [0.1.0] - 2026-10-26

### Added
- **Core HTTP Client (`Client`)**: Ergonomic, session-style HTTP client with `base_url`, default headers, cookie handling, and retry policy.
- **Top-Level Convenience Functions**: `nova.get()`, `nova.post()`, `nova.post_json()`, `nova.post_form()`, `nova.put()`, `nova.patch()`, `nova.delete()`.
- **Response Wrapper (`Response`)**:
  - Semantic status checks: `is_success()`, `is_redirect()`, `is_client_error()`, `is_server_error()`, `is_error()`.
  - Opt-in error raising: `raise_for_status()`.
  - JSON decoding: `resp.json()` into stdlib `JsonValue` with explicit `DecodeError` on failure.
  - Elapsed request time tracking (`elapsed_ms`).
- **Safe Headers (`Headers`)**:
  - RFC 7230 case-insensitive lookup.
  - Strict CRLF injection prevention in header names and values.
  - Clean header merge precedence (request overrides client defaults).
- **URL Handling & Query String**:
  - Clean `base_url` and relative path joining.
  - Automatic query parameter merging and encoding via `nox.url`.
  - Strict fragment stripping (RFC 7230 §5.1).
  - Embedded credentials rejection and `sanitize_url()` redaction for logs/errors.
- **Authentication**:
  - `BasicAuth` with Base64 encoding and safe password redaction.
  - `BearerAuth` with token masking.
  - Precedence protection ensuring explicit caller `Authorization` header is not overridden.
- **Cookie Jar (`CookieJar`)**:
  - Per-client session cookie management.
  - Automatic extraction from `Set-Cookie` headers.
  - Domain isolation preventing cross-origin cookie leakage.
- **Retry Policy (`RetryPolicy`)**:
  - Exponential backoff with bounded delays (`calculate_delay_ms`).
  - Transient HTTP status code classification (408, 429, 500, 502, 503, 504).
  - Idempotency safety: GET/HEAD safe by default; POST retries require explicit opt-in.
- **Structured Error Hierarchy**:
  - `NovaError` (base), `TransportError`, `ConnectionError`, `HttpStatusError`, `InvalidUrlError`, `InvalidHeaderError`, `DecodeError`, `EncodeError`, `RetryExhaustedError`, `UnsupportedFeatureError`.
- **Comprehensive Test Suite**:
  - 11 unit and integration tests passing end-to-end under `noxc test`.
- **Complete Documentation & Examples**:
  - Architecture, Compatibility, API Reference, Security, Transport Capabilities, Roadmap.
