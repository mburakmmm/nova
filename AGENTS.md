# AGENTS.md — NOVA HTTP Client for Nox

> Binding instructions for AI coding agents (Cursor, Claude Code, Codex and others) working on **Nova**, a standalone ergonomic HTTP client library for the **Nox programming language**.

## 0. Identity and mission

- **Project:** Nova (`nova`), formerly proposed as Vesper. Never use `vesper` in package names, imports, docs, or release metadata.
- **Purpose:** Provide a pleasant, safe, predictable, production-oriented HTTP client for Nox, inspired by the developer experience of Python Requests and HTTPX.
- **Language:** Nox, not Python. Write the library in Nox whenever the platform supports it.
- **Compiler source:** https://github.com/mburakmmm/nox-lang
- **Language docs:** https://noxlang.com
- **Distribution:** independent Nox package using `nox.json`, `nox.lock`, and the Nox package system.
- **Consumers:** any Nox application; Nyx, Aether, and Aura are optional consumers, not dependencies.
- **Non-goals:** HTTP server framework, web framework, browser, scraper, generic network stack, TLS implementation, or a fork of the Nox compiler.
- **Primary value:** request construction, predictable response handling, session configuration, robust errors, and optional advanced client features on top of the Nox standard library.

**Golden rule: never claim Nova supports an HTTP feature merely because Requests/HTTPX supports it. Implement only capabilities verified in the installed Nox toolchain and tested end to end.**

## 1. Mandatory discovery before editing

Before every substantial change:
1. Read this file, the Nova repository, its tests, README, roadmap, and changelog.
2. Read the latest relevant Nox docs and the Nox compiler repository `AGENTS.md`. Its invariants govern Nox language/runtime changes.
3. Run `noxc version`; record compiler version, OS, supported targets/backends.
4. Inspect actual Nox APIs: `nox.http`, `nox.url`, `nox.json`, `nox.tls`, `nox.time`, `nox.crypto`, `nox.fs`, `nox.test`, async/task APIs and package conventions.
5. Inspect current Nox stdlib source where docs are insufficient.
6. Search the Nova repository for existing equivalents; reuse rather than duplicate.
7. Record evidence, missing capabilities, fallback choices, and exact commands in `docs/compatibility.md`.
8. Build and run the smallest example of each *new* language/API feature before designing around it.
9. Do not invent Nox syntax, compiler flags, decorators, generic types, thread primitives, sockets, timeout hooks, or HTTP APIs.

### Verified baseline from Nox repository documentation (re-check against installed version)

The published `docs/stdlib/http.md` describes:
- `nox.http.get(url, headers) -> HttpResponse`
- `nox.http.post(url, body, headers) -> HttpResponse`
- `HttpResponse.status: int`, `.body: str`, `.headers: dict[str, str]`
- `HttpError` for connection/DNS/TLS failures.
- HTTP and HTTPS, automatic redirects, and automatic gzip/deflate response decoding.
- Non-2xx responses **do not raise** by default.
- Client-side `get`/`post` are ordinary Nox code; server `serve*` APIs are not client extension points.

**Critical limitation:** this documented client API does NOT establish arbitrary methods (PUT/PATCH/DELETE/HEAD), request-level timeouts, redirect policy control, streaming, byte-oriented bodies, multipart upload, proxy configuration, connection pooling, cancellation, or asynchronous client transport. Those features are **conditional roadmap items**, not existing capabilities.

`docs/tools/noxc.md` documents `noxc check <file.nox>`, `noxc run <file.nox>`, `noxc build <file.nox>`, `noxc test`, `noxc fmt <file.nox>`, and `noxc version`; confirm installed behavior.

`docs/tools/packages.md` documents `nox.json`, locked Git dependencies, `noxc fetch`, and `noxc publish`. Do not publish without permission.

## 2. Non-negotiable engineering invariants

1. Use valid **statically typed Nox**; do not copy dynamic Python patterns into Nox.
2. Preserve automatic memory management. No user-facing ownership annotations or unsafe lifetime hacks.
3. Prefer public stable stdlib APIs. Do not access undocumented compiler/runtime internals.
4. No compiler/runtime changes, native shim, or vendored transport without explicit approval and a written justification.
5. Never advertise timeout/retry/pooling/streaming/async/cancellation guarantees that the underlying transport cannot fulfill.
6. Never bypass TLS certificate or hostname verification. No insecure TLS mode in the default public API.
7. Never silently retry unsafe requests, leak credentials, or follow unsafe redirects.
8. Keep all behavior deterministic where practical; test ordering and configuration precedence.
9. Never use mutable hidden global session state. Explicit client/session objects hold configuration.
10. Never hide network errors or convert them to misleading success responses.
11. HTTP 4xx/5xx are valid HTTP responses, not transport failures. Optional `raise_for_status` may turn them into explicit status errors.
12. Keep core independent of Nyx, Aether, Aura, and application frameworks.
13. Add no unnecessary dependencies. Audit transitive dependencies and native code.
14. Write tests and docs for every public feature; do not weaken tests to get green CI.
15. Protect user data in logs, exceptions, redirects, caches, and diagnostics.
16. Preserve public API compatibility; document changes and migration paths.
17. Do not use network access or package publishing in tests unless explicitly required; prefer local fixtures.
18. Report unsupported features clearly; do not fake them with no-op options.

## 3. Scope and release philosophy

Nova should grow in independently verifiable layers:

**MVP (must work first):**
- GET and POST over HTTP/HTTPS using the verified Nox stdlib.
- Request headers and request body as supported.
- Response wrapper: status, body, headers, status helpers.
- Safe JSON encode/decode where `nox.json` supports it.
- Query parameter and URL construction via verified `nox.url`.
- Explicit transport errors and opt-in HTTP status errors.
- Small immutable/configurable client abstraction if Nox supports it.
- Real local integration tests, examples, and documentation.

**Next, only when transport supports it:**
- Other HTTP methods; request timeouts; redirect control; retry policy; session defaults.
- Authentication helpers, cookie handling, form encoding, multipart upload.
- Raw bytes, streaming download/upload, cancellation, proxy support.
- Connection reuse/pooling and async API.

Never expand the public API merely to fill a feature checklist.

## 4. Proposed repository layout

Use actual verified Nox package conventions; adapt paths to the compiler's import rules.

```text
nova/
  AGENTS.md
  README.md
  LICENSE
  CHANGELOG.md
  nox.json
  nox.lock                 # if dependencies are present
  docs/
    architecture.md
    compatibility.md
    api.md
    security.md
    transport-capabilities.md
    roadmap.md
    migration.md
  src/                     # only if supported by actual Nox import conventions
    nova/
      client.nox
      request.nox
      response.nox
      errors.nox
      headers.nox
      url.nox
      json.nox
      auth.nox
      retry.nox
      transport.nox
  tests/
    unit/
    integration/
    regression/
    fixtures/
  examples/
    basic_get.nox
    post_json.nox
    query_params.nox
    error_handling.nox
    client_defaults.nox
  benchmarks/
  .github/workflows/
```

Do not create empty placeholder modules. Implement only modules justified by current functionality.

## 5. Architecture and dependency direction

```text
User application / optional framework adapter
                    |
             Nova public API
                    |
    Client config / request / response
                    |
  URL + headers + auth + body + errors
                    |
             Transport adapter
                    |
        Verified Nox stdlib APIs
```

- `transport` is the **only** layer that talks to `nox.http` or a future approved transport.
- A transport capability matrix is mandatory: supported methods, timeout, redirects, raw bytes, streaming, proxy, pooling, async, cancellation, TLS settings.
- Unsupported features must fail explicitly at configuration/usage time or remain absent from the API.
- Request/response representations should not depend on a particular transport implementation.
- Avoid circular imports, hidden initialization, and global mutable singletons.
- Do not conflate transport response decoding with JSON deserialization.
- If the current transport auto-decompresses or follows redirects, document that Nova cannot reverse those effects.

## 6. Public API design

The following is a **conceptual contract**, NOT executable Nox code until compiled and verified.

- `get(url, ...)`, `post(url, ...)`
- `Client(config)` with `get(...)`, `post(...)`, and a general `request(...)` only if arbitrary methods are supported.
- `Request`: method, URL, headers, body, options.
- `Response`: status code, headers, body, optional parsed JSON, helpers.
- `NovaError` hierarchy; transport errors and status errors distinguished.
- `raise_for_status(response)` or response method.
- `json(response)` / `response.json()` only if the Nox API can implement it cleanly.

### Design requirements
- Avoid giant parameter lists; prefer typed option/config objects if supported.
- No runtime keyword-argument emulation or untyped `Any` workaround.
- No API names borrowed blindly from Python.
- Clearly distinguish text body, JSON body, and binary body; no silent ambiguity.
- Define response body ownership and lifetime where necessary.
- Prefer stable, simple names; reserve future expansion only when justified.
- Every public example must compile under CI.

## 7. Request semantics

### HTTP methods
- GET/POST are baseline.
- PUT/PATCH/DELETE/HEAD/OPTIONS are gated by real transport support.
- Never implement DELETE by calling GET or PUT by calling POST.
- Validate method tokens if custom methods are supported.
- HEAD responses must not expose fabricated body content.

### URLs and query parameters
- Use `nox.url` where possible.
- Support absolute `http://` and `https://` URLs; document other schemes as unsupported.
- Validate scheme, host, port, authority, path, query, fragment handling.
- URL fragments are never transmitted in an HTTP request.
- Preserve existing query parameters and append new ones predictably.
- Percent-encode keys/values correctly; do not double-encode.
- Define repeated query keys and parameter ordering.
- Reject embedded credentials in URL or explicitly sanitize them in errors/logs.
- Handle IPv6 literals, IDNs, UTF-8, spaces, empty values, and reserved characters per documented support.
- If `base_url` is implemented, specify exact relative URL resolution and host boundary rules.

### Headers
- HTTP header names are case-insensitive; normalize lookup semantics.
- Reject CR/LF and invalid header-name characters to prevent header injection.
- Define merge precedence: per-request > client defaults > library defaults.
- Handle duplicate headers correctly; do not merge `Set-Cookie` with commas.
- Never accidentally duplicate or override transport-controlled `Host`, `Content-Length`, `Transfer-Encoding`, or `Accept-Encoding`.
- Do not promise preservation of repeated headers if underlying `dict[str,str]` loses duplicates.
- Define behavior for `Content-Type`, `Accept`, and `User-Agent`.
- Do not send `Authorization` to a different origin after redirects.

### Bodies
- GET request bodies are unsupported unless deliberately implemented and tested.
- For POST, use the transport's actual body type.
- JSON encoding must use verified `nox.json` APIs; set correct media type only when appropriate.
- Form encoding, multipart and binary uploads are **not** MVP requirements.
- Define empty body vs absent body vs JSON null.
- Validate encoding and content length where Nova controls them.
- Never claim zero-copy upload or streaming when the stdlib buffers strings.

## 8. Response semantics

- Expose actual status and decoded body from transport; never fabricate missing headers or raw wire bytes.
- Keep headers case-insensitive for lookup.
- Distinguish empty body from JSON `null`.
- JSON parsing failure is a JSON/decoding error, not an HTTP status error.
- Define behavior for `204`, `205`, `304`, `HEAD`, and invalid JSON.
- Define `is_success`, `is_redirect`, `is_client_error`, `is_server_error` precisely.
- Optional `raise_for_status` should retain safe status, URL, and limited sanitized context.
- No implicit exception for 4xx/5xx unless the caller explicitly enables it.
- Document that auto-decompression and redirects may already have happened in `nox.http`.

## 9. Error taxonomy

Implement using supported Nox exception patterns. Suggested conceptual categories:

- `NovaError`: common base.
- `TransportError`: failed to establish/complete a request.
- `ConnectionError`: connection failure when distinguishable.
- `DnsError`: DNS failure when distinguishable.
- `TlsError`: TLS failure when distinguishable.
- `TimeoutError`: **only** if a real timeout guarantee exists.
- `InvalidUrlError`: URL validation.
- `InvalidHeaderError`: invalid header.
- `EncodeError`: body/JSON encoding.
- `DecodeError`: response decoding.
- `HttpStatusError`: explicitly requested raise on status.
- `UnsupportedFeatureError`: a capability unavailable in the selected transport.
- `RetryExhaustedError`: only after retries exist.

Do not pretend the underlying `HttpError` exposes DNS vs TLS vs connection subtypes if it does not. Preserve original error cause where supported; otherwise document information loss. Avoid sensitive raw payloads in errors.

## 10. Authentication

**After MVP**, support only verified, explicit mechanisms:

- Basic auth: UTF-8/byte encoding and Base64 per standards; HTTPS strongly recommended.
- Bearer token: correct header formatting and token redaction.
- Custom authentication hook: only if supported without unsafe dynamic dispatch.
- Do not log credentials or include them in error reprs.
- Never forward sensitive credentials to a different origin during redirects.
- Define precedence if caller supplies both explicit `Authorization` and an auth helper.
- Token refresh and OAuth2 are separate optional integrations, not core requirements.
- No secret persistence by default.

## 11. Redirect handling

The documented `nox.http` client automatically follows redirects.

**Until the transport exposes control, Nova must not claim:**
- `allow_redirects=false`
- `max_redirects`
- redirect history
- manual cross-origin credential stripping
- method-preserving redirects
- redirect-loop prevention beyond transport behavior

Before adding redirect options:
1. Inspect transport implementation and current security behavior.
2. Confirm redirect limits and HTTPS downgrade behavior.
3. Verify 301/302/303/307/308 method/body semantics.
4. Verify credentials and cookies are not leaked cross-origin.
5. Test relative and absolute `Location`, loops, malformed destinations.
6. Reject unsupported controls rather than silently ignoring them.

## 12. Timeout and cancellation

The documented client API does not expose a timeout parameter. Never fake a timeout by timing a synchronous call *after it returns*.

- Distinguish DNS/connect, TLS handshake, read, write, overall timeout when transport permits.
- Timeouts must actually interrupt/terminate work or safely return without leaked resources.
- Use monotonic clocks for elapsed durations.
- Define whether timeout includes retries, redirects, and backoff.
- Cancellation must propagate to active I/O if advertised.
- No thread-spawning timeout wrapper that leaves uncontrolled background requests.
- If unsupported, omit timeout options and document limitation.

## 13. Retry policy

Retry is **conditional** on safe transport behavior and available timing controls.

- Default: **no automatic retries**.
- Opt-in policy with bounded attempts, bounded delay, optional exponential backoff and jitter.
- Retry transient transport errors only when semantics and idempotency permit.
- Default safe method allowlist should be conservative (GET/HEAD where supported); POST never automatically retried without explicit caller opt-in/idempotency guarantees.
- Consider 408, 429, 500, 502, 503, 504 only under explicit policy.
- Respect `Retry-After` seconds/date when correctly parsed.
- Never retry invalid URLs, certificate failures, authentication failures, or validation errors.
- Avoid replaying non-rewindable request bodies.
- Bound total attempts, total elapsed time, and backoff.
- Test exact attempts and delays with injected clocks/transports, not real sleeps.
- Never label a failed operation successful after exhausting attempts.

## 14. Cookies and sessions

Cookie support is **not** part of MVP.

If implemented:
- Use standards-aligned domain/path/expiry/Secure/HttpOnly/SameSite semantics.
- Separate cookie jar per client; no hidden global cookie jar.
- Prevent cross-origin cookie leakage.
- Handle multiple `Set-Cookie` headers; if stdlib flattens them, state limitations and do not offer a broken cookie jar.
- Persist cookies only on explicit request with safe permissions.
- Define thread-safety, cleanup, and concurrency behavior.
- A `Client` object may still provide default headers/configuration without claiming TCP connection pooling or cookie persistence.

## 15. Async, concurrency and connection pooling

- Do not assume `async def` makes synchronous `nox.http.get` nonblocking.
- An async client is allowed only with verified nonblocking transport integration.
- Do not promise HTTP/2, HTTP/3, multiplexing, keep-alive pooling, or concurrent request limits without transport support.
- If pooling is implemented, define max connections, idle timeout, origin isolation, TLS identity, cleanup, and thread safety.
- Avoid shared mutable state races.
- Cancellation must release sockets and other resources.
- Benchmarks must distinguish concurrency from true async I/O.

## 16. TLS, proxies, streaming, and files

### TLS
- Default to verified TLS with certificate and hostname checks.
- No implicit fallback from HTTPS to HTTP.
- Do not offer `verify=false` as a convenience default.
- Custom CA bundles, mTLS, TLS version control, certificate pinning: conditional on transport support and reviewed security design.

### Proxies
- HTTP/HTTPS/SOCKS proxy support requires explicit implementation and tests.
- Handle proxy auth securely and prevent proxy credential leaks.
- Do not assume OS proxy environment variables are honored.

### Streaming / binary
- Current documented `HttpResponse.body` is `str`; this is not proof of binary-safe response handling.
- Do not market file downloads, raw bytes, streaming, chunked uploads, or large-file efficiency until a verified byte-oriented transport exists.
- For any file output: atomic writes where possible, size limits, path safety, cleanup on failure, and tests.
- Multipart boundaries, filename escaping, and content length must be standards-compliant if implemented.

## 17. Security and SSRF

- Treat URLs, headers, JSON, credentials, and response bodies as untrusted.
- Validate input before network calls; reject unsupported schemes.
- Avoid CRLF injection, request smuggling, conflicting content lengths, and invalid authority.
- Never put auth tokens in logs or error messages.
- Default logs must redact `Authorization`, `Proxy-Authorization`, `Cookie`, `Set-Cookie`, API keys, and userinfo in URLs.
- Provide configurable response/request size caps **only if enforceable by the transport**; otherwise document that the full response may be buffered.
- Nova is a general HTTP client, **not automatically an SSRF firewall**. Document the risk when callers pass user-controlled URLs.
- If optional SSRF controls are offered, account for DNS rebinding, IPv4/IPv6, redirects, loopback, private/link-local ranges, and DNS resolution consistency.
- Do not claim redirect credential protection when redirect handling is hidden in stdlib.
- No arbitrary shell execution, dynamic native plugin loading, or filesystem access from untrusted input.
- Keep dependencies minimal and audit native/FFI surfaces.

## 18. Testing strategy

Use `nox.test` and `noxc test` as documented and verified. Build local deterministic HTTP test fixtures using supported Nox server APIs or a separately controlled test server. Do not rely on public internet services in CI.

**Mandatory tests for every supported feature:**
- Success and failure.
- Boundaries and malformed input.
- Security-sensitive behavior.
- Cross-platform/backend behavior where claimed.
- No credential leakage.
- Deterministic errors and config precedence.
- Regression case for each bug fix.

### Core integration matrix
- GET 200, GET 404, GET 500.
- POST text, POST JSON, empty body.
- Custom headers, header case, invalid CRLF header.
- Query encoding: spaces, Unicode, `%`, `&`, repeated keys.
- Valid JSON, invalid JSON, empty JSON response.
- HTTP vs HTTPS with a controlled trusted test certificate.
- DNS failure, refused connection, TLS verification failure.
- Redirect success/loop/cross-origin auth where controllable; otherwise document transport limitation.
- gzip/deflate behavior inherited from stdlib.
- Large response behavior and documented limitations.
- Concurrent calls only when supported and claimed.
- Timeouts/retries/multipart/streaming only after real implementation.

**Testing rules:**
- Never replace network behavior with mocks exclusively; at least one real local integration test per transport feature.
- Use mock/injected transport for deterministic retry/configuration tests when architecture permits.
- No `sleep`-based flaky tests when a fake clock can be used.
- Never disable certificate validation just to make HTTPS tests pass.
- No skip or deletion of failing tests to pass CI.
- Test both LLVM and QBE backends if relevant and available; mark unsupported combinations.
- Document exact test commands and results.

## 19. Performance and resource discipline

- Measure baseline overhead compared with direct `nox.http.get/post`.
- Benchmark small JSON, large text, headers/query construction, and repeated calls.
- Use a local server to avoid external network variance.
- Record Nox version, backend, OS, optimization, payload sizes, iterations, and timing method.
- Do not claim pooling or speedups without measurement.
- Bound allocations when possible; document underlying full-body buffering.
- Never trade TLS validation, correct URL handling, or response integrity for speed.
- Avoid premature caching and hidden mutable global state.

## 20. Documentation requirements

English is the primary documentation language; Turkish translations may be added.

`README.md` must include:
- What Nova is and is not.
- Minimum verified Nox version and supported platforms.
- Installation via actual Nox package mechanism.
- Compiling GET/POST quick start.
- Headers, query params, JSON, and error handling.
- Security and transport limitations.
- Explicit feature matrix: **implemented / conditional / unsupported**.
- License, changelog, contribution guide.

`docs/transport-capabilities.md` must track:
| Capability | Verified stdlib | Nova implemented | Tests | Limitation |
|---|---|---|---|---|
| GET/POST | documented | TBD | TBD | response body is text |
| HTTPS | documented | TBD | TBD | verify runtime behavior |
| Redirect following | documented | TBD | TBD | no documented control |
| gzip/deflate | documented | TBD | TBD | auto-decoded |
| PUT/PATCH/DELETE | not documented | no | n/a | requires transport |
| Request timeout | not documented | no | n/a | requires transport |
| Streaming/raw bytes | not documented | no | n/a | requires transport |
| Async/pooling/proxy | not documented | no | n/a | requires transport |

**All snippets must compile in CI.** Mark design-only pseudocode as `PSEUDOCODE — NOT IMPLEMENTED`. Do not include fictional Nox imports.

## 21. Package management, CI, and release

- Use real `nox.json` fields (`name`, `version`, `entry`, `requires`) per Nox docs.
- Use `nova` as package name/import alias where verified.
- Pin dependencies and commit `nox.lock` if present.
- CI: formatting, compile/typecheck, unit tests, local integration tests, examples, supported OS/backend matrix.
- Run `noxc check` on relevant `.nox` files; `noxc test` for test suite; `noxc run` for examples; `noxc build` for deliverables. Verify local invocation and exit codes.
- Avoid unrequested automatic dependency updates.
- Follow SemVer; pre-1.0 breaking changes still require changelog notes.
- Never run `noxc publish`, push tags, publish releases, or modify another repository without explicit user approval.
- Do not call Nova “production-ready” until tests, security review, and documented support matrix justify it.

## 22. Development roadmap

### Phase 0 — Discovery and feasibility
Deliver:
- Capability audit of Nox HTTP client and stdlib.
- Minimal GET/POST examples that compile.
- `docs/compatibility.md`, `docs/transport-capabilities.md`, architecture decisions.
- Feature feasibility matrix.
**Exit:** evidence-backed, runnable proof; no speculative API.

### Phase 1 — Nova MVP
Deliver:
- Verified GET/POST wrapper.
- URL/query construction and safe headers.
- Response/status helpers.
- JSON encoding/decoding.
- Clear transport vs HTTP-status vs JSON errors.
- Local integration tests and README examples.
**Exit:** all implemented features compile, run, and pass tests.

### Phase 2 — Client ergonomics
Deliver:
- Client-level default headers/base URL/options (only where supported).
- Basic/Bearer authentication with redaction.
- Form encoding if implementable.
- Configuration precedence and client isolation tests.
**Exit:** no hidden global state, no credential leaks.

### Phase 3 — Transport capability expansion
Evaluate one at a time:
- Additional methods.
- True timeouts/cancellation.
- Redirect controls.
- Retry policy.
- Cookies.
- Binary body and multipart.
**Gate:** if stdlib lacks a required capability, document an upstream proposal and seek approval before any native transport/compiler change.

### Phase 4 — Advanced features
Conditional:
- Streaming, proxies, async transport, connection pooling.
- Optional framework adapters.
- Performance tuning and cross-platform hardening.
**Exit:** explicit capability evidence, security tests, benchmark reports.

### Phase 5 — Stable 1.0
- Public API review and compatibility guarantees.
- Release documentation, security checklist, migration notes.
- Full supported CI matrix.
- Explicit user authorization before release.

## 23. Agent task protocol

For each task:
1. Identify exact acceptance criteria.
2. Inspect affected code, tests, current stdlib docs, and compiler behavior.
3. State whether required transport features actually exist.
4. Design the smallest compatible solution.
5. Implement one vertical slice.
6. Add unit and local integration tests.
7. Format, type-check, build, run tests/examples.
8. Review API stability, TLS, redirects, auth, errors, and resource usage.
9. Update docs, compatibility matrix, and changelog.
10. Report changed files, exact commands, actual results, limitations, and next tasks.

### If blocked
- Stop rather than fabricate support.
- Produce a minimal reproduction and cite exact missing API.
- Offer the smallest supported alternative.
- Request approval for native code, stdlib/compiler modifications, or public API scope changes.
- Do not quietly substitute external CLI tools such as `curl` as the default production transport.

## 24. Definition of Done

A feature is complete only when:
- [ ] Nox syntax and APIs are verified against installed compiler.
- [ ] Implementation compiles and examples run.
- [ ] Unit and local integration tests pass.
- [ ] Errors and status behavior are documented.
- [ ] Header, URL, JSON, and credential handling are secure.
- [ ] No fake timeout, async, redirect, or pooling promises.
- [ ] No unexpected dependencies or framework coupling.
- [ ] Supported OS/backend matrix is tested or explicitly limited.
- [ ] No failing tests hidden or skipped.
- [ ] README/API/capability matrix/changelog updated.
- [ ] Agent reports actual results and limitations.

## 25. First instruction to the coding agent

**Build Nova, not an imaginary HTTPX clone.**

1. Audit `nox.http`, `nox.url`, `nox.json`, Nox package tooling and installed `noxc`.
2. Document what is actually supported, especially the GET/POST-only documented client API and automatic redirects/decompression.
3. Scaffold a minimal independent `nova` package with a valid manifest.
4. Implement one compiled GET request and one compiled POST request with a local HTTP fixture.
5. Add response status helpers, safe headers, query parameters, JSON helpers, and explicit errors **only using verified APIs**.
6. Add tests for 200/404/500, invalid JSON, query encoding, transport failure, and HTTPS verification where feasible.
7. Produce a factual Phase 2 backlog, marking every unsupported transport feature.
8. Do not add native shims or modify the Nox compiler without asking.

**Quality bar:** a small, genuinely working Nox-native HTTP client is more valuable than an extensive API whose advertised guarantees cannot be implemented.
