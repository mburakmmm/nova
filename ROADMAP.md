# Nova HTTP Client — Master TODO & Phase Roadmap

> **Binding Reference:** This roadmap strictly adheres to `AGENTS.md` rules and milestones. It governs the execution order, gating criteria, and invariants across every development turn.

---

## 📊 Phase Status Overview

| Phase | Scope | Status | Version | Tests |
|---|---|---|---|---|
| **Phase 0** | Discovery, Feasibility & Stdlib Audit | ✅ **COMPLETED** | v0.1.0 | 3 audit probes |
| **Phase 1** | Nova MVP (GET/POST, JSON, Headers, URL, Errors) | ✅ **COMPLETED** | v0.1.0 | 6 unit/integration tests |
| **Phase 2** | Client Ergonomics (Auth, CookieJar, Retry, Forms) | ✅ **COMPLETED** | v0.1.0 | 5 unit tests |
| **Phase 3** | Transport Expansion (Methods, Timeout, Binary, Multipart) | 🟡 **CURRENT MILESTONE** | v0.2.0 | Planned |
| **Phase 4** | Advanced Features (Streaming, Async, Pooling, Proxy) | ⏳ **PLANNED** | v0.3.0+ | Planned |
| **Phase 5** | Stable 1.0 Release (API Freeze, Security Audit, SemVer) | ⏳ **PENDING** | v1.0.0 | Full Matrix |

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
  - Automatic `Set-Cookie` extraction and domain isolation.
- [x] **2.5. Form Submission**: `post_form()` supporting `application/x-www-form-urlencoded`.
- [x] **2.6. Retry Policy (`retry.nox`)**:
  - `RetryPolicy`: Bounded exponential backoff delay calculation.
  - Transient status classification (408, 429, 500, 502, 503, 504).
  - Idempotency Safety: GET/HEAD safe by default; POST requires explicit caller opt-in (`retry_post=True`).
- [x] **2.7. Automated Test Suite**: 11 unit and integration tests passing (`11 passed, 0 failed` in `noxc test`).
- [x] **2.8. Git & Publishing**: Pushed to GitHub repository (`v0.1.0` tag) and submitted to the central index with `noxc publish`.

---

### 🟡 Phase 3 — Transport Capability Expansion (CURRENT MILESTONE)

> [!IMPORTANT]
> **AGENTS.md Invariant (§2 & §22 Phase 3):** If the standard library lacks a required capability, Nova must not fake it with no-op code or GET/POST emulation. Features must be unlocked upstream in `nox-lang` first or implemented purely in Nox where possible.

#### 3.1. Arbitrary HTTP Methods (PUT, PATCH, DELETE, HEAD, OPTIONS)
- [x] **3.1.1. Explicit Guard**: Calling unsupported methods raises `UnsupportedFeatureError` (no fake simulation).
- [ ] **3.1.2. Upstream Runtime Export**: Add generic `nox_http_request_raw(rt, method, url, body, headers)` export to `runtime/stdlib_shims/http_client.zig`.
- [ ] **3.1.3. Upstream Stdlib Declaration**: Add `request(method, url, body, headers)` to `stdlib/nox/http.nox`.
- [ ] **3.1.4. Nova Transport Integration**: Wire PUT, PATCH, DELETE, HEAD, OPTIONS in `TransportAdapter.execute()`.
- [ ] **3.1.5. Method Tests**: End-to-end integration tests for PUT 200/204, DELETE 200/204, and HEAD empty body.

#### 3.2. True Request Timeout
- [x] **3.2.1. Principle Compliance**: No fake post-return timing wrapper (§12).
- [ ] **3.2.2. Upstream Timeout Hook**: Introduce socket/read timeout (`timeout_ms`) in Zig `std.http.Client` request configuration.
- [ ] **3.2.3. Nova Client Hook**: Expose `Client(timeout_ms=...)` and request-level `timeout_ms`.
- [ ] **3.2.4. Timeout Tests**: Deterministic test using unresponsive local test socket verifying `TimeoutError`.

#### 3.3. Redirect Control Policy
- [ ] **3.3.1. Upstream Redirect Policy**: Expose redirect behavior toggle (`follow_redirects=false`, `max_redirects`).
- [ ] **3.3.2. Nova Security Shield**: Strip `Authorization` header on cross-origin redirects.
- [ ] **3.3.3. Redirect Tests**: Verify redirect limits and credential stripping.

#### 3.4. Multipart Form & File Upload
- [x] **3.4.1. Multipart Encoder**: RFC 7578 compliant boundary generator and payload formatter in pure Nox (`multipart.nox`).
- [x] **3.4.2. File Upload API**: `post_multipart(url, encoder, ...)` and `file_from_path()` integrating `nox.fs.read_to_string`.
- [x] **3.4.3. Multipart Tests**: Verified boundary framing, filesystem file attachment, and live server file delivery against httpbin (`tests/unit/multipart_test.nox` and `tests/integration/multipart_integration_test.nox`).

---

### ⏳ Phase 4 — Advanced Features (PLANNED)
- [ ] **4.1. Binary Body Support**: Byte-oriented response handling (`buffer.nox` / raw bytes) beyond NUL-terminated strings.
- [ ] **4.2. Streaming Download & Upload**: Chunked streaming for large files without whole-payload memory buffering.
- [ ] **4.3. Connection Pooling**: TCP/TLS connection reuse across multiple client requests.
- [ ] **4.4. Async Client**: Cooperative fiber async transport (`async def get()` / `await client.get()`).
- [ ] **4.5. HTTP / SOCKS Proxy**: Proxy forwarding with secure proxy authentication.
- [ ] **4.6. SSRF Protection Shield**: Configurable private IP blocklist (RFC 1918, loopback, link-local).

---

### ⏳ Phase 5 — Stable 1.0 Release
- [ ] **5.1. Public API Review**: Final SemVer compatibility guarantee.
- [ ] **5.2. Benchmarks**: Latency and memory benchmarks against baseline `nox.http`.
- [ ] **5.3. Cross-Platform Matrix**: CI validation across macOS, Linux, and Windows with LLVM & QBE backends.
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
