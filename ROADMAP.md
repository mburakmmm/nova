# Nova HTTP Client — Master TODO & Phase Roadmap

> **Binding Reference:** This roadmap strictly adheres to `AGENTS.md` rules and milestones. It governs the execution order, gating criteria, and invariants across every development turn.

---

## 📊 Phase Status Overview

| Phase | Scope | Status | Version | Tests |
|---|---|---|---|---|
| **Phase 0** | Discovery, Feasibility & Stdlib Audit | ✅ **COMPLETED** | v0.1.0 | 3 audit probes |
| **Phase 1** | Nova MVP (GET/POST, JSON, Headers, URL, Errors) | ✅ **COMPLETED** | v0.1.0 | 6 unit/integration tests |
| **Phase 2** | Client Ergonomics (Auth, CookieJar, Retry, Forms) | ✅ **COMPLETED** | v0.1.0 | 5 unit tests |
| **Phase 3** | Transport Expansion (Methods, Timeout, Binary, Multipart, Redirects) | ✅ **COMPLETED** | v0.3.0 | 18 unit/integration tests |
| **Phase 4** | Advanced Features (Streaming, SSRF Shield, Async Concurrency) | ✅ **COMPLETED** | v0.4.0 | 22 unit/integration tests |
| **Phase 5** | Stable 1.0 Release (API Freeze, Security Audit, SemVer) | ⏳ **NEXT** | v1.0.0 | Full Matrix |

---

## 🛠️ Detailed Breakdown & TODO Items

### ✅ Phase 0 — Discovery and Feasibility (COMPLETED)
- [x] **0.1. Toolchain Audit**: Verified `noxc 2.0.27`, Darwin arm64 platform, LLVM and QBE backends.
- [x] **0.2. Stdlib HTTP Client Audit**: Verified documented `nox.http.get()` and `nox.http.post()`.
- [x] **0.3. Runtime Inspection**: Inspected `runtime/stdlib_shims/http_client.zig`. Confirmed `doRequest` accepts all `std.http.Method` internally, but only `nox_http_get_raw` and `nox_http_post_raw` are exported in `noxrt.o`.
- [x] **0.4. Automatic Transport Effects**: Verified that automatic redirect following and gzip decompression are performed by the stdlib runtime.
- [x] **0.5. Evidence Documentation**: Created `docs/compatibility.md` and `docs/transport-capabilities.md`.

---

### ✅ Phase 1 — Nova MVP (COMPLETED)
- [x] **1.1. Package Scaffolding**: Valid `nox.json` with package metadata and entry point.
- [x] **1.2. Error Taxonomy (`errors.nox`)**: Root `NovaError` with 9 specialized exceptions (`TransportError`, `ConnectionError`, `HttpStatusError`, `InvalidUrlError`, `InvalidHeaderError`, `DecodeError`, `EncodeError`, `RetryExhaustedError`, `UnsupportedFeatureError`).
- [x] **1.3. Case-Insensitive Headers (`headers.nox`)**: RFC 7230 case-insensitive lookups, strict CRLF injection defense.
- [x] **1.4. Safe URL Engine (`url.nox`)**: `base_url` normalization, `nox.url` query parameter encoding, fragment stripping (RFC 7230 §5.1), embedded credentials rejection, and password sanitization helper (`sanitize_url`).
- [x] **1.5. Rich Response (`response.nox`)**: Status predicates (`is_success`, `is_redirect`, `is_client_error`, `is_server_error`, `is_error`), `raise_for_status()`, `json()` decoding via `nox.json`, and `elapsed_ms` duration tracking.
- [x] **1.6. Transport Isolation (`transport.nox`)**: `TransportAdapter` solely interacts with `nox.http`.
- [x] **1.7. Top-Level Facade (`nova.nox`)**: `nova.get()`, `nova.post()`, `nova.post_json()`, `nova.post_form()` convenience wrappers.
- [x] **1.8. Core Integration Tests**: Verified live requests against httpbin (200, 404, 500 status handling).

---

### ✅ Phase 2 — Client Ergonomics (COMPLETED)
- [x] **2.1. Client Session (`client.nox`)**: `Client(base_url, raise_for_status)` with default headers (`User-Agent: Nova/0.1.0`, `Accept: */*`).
- [x] **2.2. Zero Mutable Global State**: Full instance isolation between `Client` objects.
- [x] **2.3. Authentication Helpers (`auth.nox`)**:
  - `BasicAuth`: Base64 UTF-8 encoding, credential redaction in `redacted()`.
  - `BearerAuth`: Token header formatting and masked logging.
  - Precedence Rule: Caller-supplied explicit `Authorization` is never overridden.
- [x] **2.4. Cookie Management (`cookies.nox`)**:
  - Per-client `CookieJar`.
  - Automatic `Set-Cookie` extraction, domain isolation, RFC 6265 §5.3 acceptance checks, and host-only cookie isolation.
- [x] **2.5. Form Submission**: `post_form()` supporting `application/x-www-form-urlencoded`.
- [x] **2.6. Retry Policy (`retry.nox`)**:
  - `RetryPolicy`: Bounded exponential backoff delay calculation.
  - Transient status classification (408, 429, 500, 502, 503, 504).
  - Idempotency Safety: GET/HEAD safe by default; POST requires explicit caller opt-in (`retry_post=True`).
  - `Retry-After` capping to `max_backoff_ms`.
- [x] **2.7. Automated Test Suite**: 15 unit and integration tests passing (`15 passed, 0 failed` in `noxc test`).
- [x] **2.8. Git & Publishing**: Pushed to GitHub repository (`v0.2.2` tag) and submitted to the central index with `noxc publish`.

---

### ✅ Phase 3 — Transport Capability Expansion (COMPLETED — v0.3.0)

#### 3.1. Arbitrary HTTP Methods (PUT, PATCH, DELETE, HEAD, OPTIONS)
- [x] **3.1.1. Explicit Guard**: Calling unsupported methods previously raised `UnsupportedFeatureError`.
- [x] **3.1.2. Upstream Runtime Export**: Added `nox_http_request_raw(method, url, body, has_body, headers, timeout_ms)` in Nox v2.0.31 (`http_client.zig`).
- [x] **3.1.3. Upstream Stdlib Declaration**: Added `nox.http.request`, `put`, `patch`, `delete`, `head`, `options` to `stdlib/nox/http.nox`.
- [x] **3.1.4. Nova Transport Integration**: Wired PUT, PATCH, DELETE, HEAD, OPTIONS in `TransportAdapter.execute()` using `nox.http.request`.
- [x] **3.1.5. Method Tests**: End-to-end integration tests for PUT 200, PATCH 200, DELETE 200, and OPTIONS passing against httpbin (`tests/integration/methods_integration_test.nox`).

#### 3.2. True Request Timeout
- [x] **3.2.1. Principle Compliance**: No fake post-return timing wrapper (§12).
- [x] **3.2.2. Upstream Timeout Hook**: Introduced socket/read timeout (`timeout_ms`) and `nox.http.HttpTimeoutError` in Nox v2.0.31.
- [x] **3.2.3. Nova Client Hook**: Exposed `Client(timeout_ms=...)` and request-level `timeout_ms` parameter; mapped `HttpTimeoutError` to `TimeoutError`.
- [x] **3.2.4. Timeout Tests**: Integration test against live delayed server endpoint (`/delay/5` with 1000ms timeout) verifying `TimeoutError` (`tests/integration/timeout_test.nox`).

#### 3.3. Redirect Control Policy
- [x] **3.3.1. Upstream Redirect Policy Audit**: Verified that Nox runtime sets `redirect_behavior = .unhandled`, yielding raw 3xx status codes for client control.
- [x] **3.3.2. Nova Security Shield**: Configurable `max_redirects`, redirect loop detection, and automatic stripping of `Authorization` and `Cookie` headers on cross-origin redirects.
- [x] **3.3.3. Redirect Tests**: Verified redirect limits, cross-origin credential stripping, and live 302->200 redirect execution (`tests/integration/redirect_integration_test.nox`).

#### 3.4. Multipart Form & File Upload
- [x] **3.4.1. Multipart Encoder**: RFC 7578 compliant boundary generator and payload formatter in pure Nox (`multipart.nox`).
- [x] **3.4.2. File Upload API**: `post_multipart(url, encoder, ...)` and `file_from_path()` integrating `nox.fs.read_to_string`.
- [x] **3.4.3. Multipart Tests**: Verified boundary framing, filesystem file attachment, and live server file delivery against httpbin (`tests/unit/multipart_test.nox` and `tests/integration/multipart_integration_test.nox`).

#### 3.5. Binary Body & Buffer Access
- [x] **3.5.1. Upstream Binary Preservation**: `HttpResponse.body` preserves embedded NUL and non-UTF-8 bytes; `nox.bytes.from_str` introduced in Nox v2.0.31.
- [x] **3.5.2. Nova Response Binary API**: Added `Response.bytes() -> Buffer` using `nox.bytes.from_str(self.body)`.
- [x] **3.5.3. Binary Tests**: Verified byte preservation and `Buffer` length/values on binary payloads (`tests/unit/binary_response_test.nox`).

---

### ✅ Phase 4 — Advanced Features & Security Shield (COMPLETED — v0.4.0)
- [x] **4.1. SSRF Protection Shield (`ssrf.nox`)**:
  - `SSRFPolicy` defense-in-depth shield with configurable private IP, loopback, link-local, and cloud metadata blocking.
  - Blocks RFC 1918 private IPv4 (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.0/8`, `0.0.0.0/8`), cloud metadata (`169.254.169.254`, `169.254.0.0/16`).
  - Blocks IPv6 loopback (`::1`), link-local (`fe80::/10`), unique-local (`fc00::/7`), and IPv4-mapped IPv6 evasion (`::ffff:127.0.0.1`, `::ffff:169.254.169.254`).
  - Enforced on initial requests and redirect destinations in `Client.send()`.
  - Comprehensive unit test suite in `tests/unit/ssrf_test.nox`.
- [x] **4.2. Streaming Response Reader (`stream.nox`)**:
  - `StreamResponse` model with incremental consumption APIs: `read_chunk(chunk_size)`, `read_chunk_bytes(chunk_size) -> Buffer`, `iter_bytes(chunk_size)`, `iter_lines()`, `read_all()`.
  - `Client.stream()` and top-level `nova.stream()`.
  - Unit tests in `tests/unit/stream_test.nox` and live integration test against `httpbin.org/stream/5` in `tests/integration/stream_integration_test.nox`.
- [x] **4.3. Async Concurrency with Nox Fibers**:
  - Verified concurrent non-blocking HTTP requests across fiber task pool via `spawn` and `Task[T]`.
  - Added live concurrent integration test in `tests/integration/async_concurrency_test.nox`.
  - Documented compiler limitations regarding `spawn` method calls and cross-module import symbol behavior in `NOX_LIMITATIONS.md`.
- [x] **4.4. Binary Body & Buffer Preservation**:
  - Embedded NUL byte and binary data handling via `Response.bytes() -> Buffer`.
  - Unit test in `tests/unit/binary_response_test.nox`.
- [x] **4.5. Upstream Transport Matrix & Limitation Tracking**:
  - Documented HEAD request keep-alive socket hang in `NOX_LIMITATIONS.md`.
  - Documented missing runtime persistent connection pooling and proxy dialer in `docs/transport-capabilities.md`.

---

### ⏳ Phase 5 — Stable 1.0 Release (IN PROGRESS)
- [ ] **5.1. Public API Review**: Final SemVer compatibility guarantee.
- [x] **5.2. Microbenchmarks (`benchmarks/bench_nova.nox`)**: URL resolution (1.3 µs), case-insensitive header lookup (33 ns), SSRF validation (0.5 µs), and multipart framing (< 1 µs).
- [x] **5.3. Cross-Platform Matrix (`.github/workflows/ci.yml`)**: Automated CI validation across macOS and Linux with `noxc test`.
- [ ] **5.4. Security Checklist Sign-off**: Complete verification of the AGENTS.md security checklist.
- [ ] **5.5. Official 1.0 Release**: Tag `v1.0.0` and update `nox.json` / central index.

---

## 🧭 Per-Turn Agent Protocol

Every development turn must follow this checklist:
1. **Rule Check**: Confirm no conflict with `AGENTS.md` invariants.
2. **Minimal Slice**: Implement only one verifiable vertical slice at a time.
3. **Static Typing**: Follow Nox static typing patterns (`self: T`, narrowed optionals with `if x is not None:`).
4. **Test-Driven**: Add unit and integration tests under `tests/unit/` or `tests/integration/`.
5. **Full Suite Green**: Verify `noxc test` passes with 0 failures before any commit.
6. **Documentation**: Update `README.md`, `CHANGELOG.md`, and relevant `docs/` files.
7. **Roadmap Tracking**: Mark completed checkboxes in this file.
