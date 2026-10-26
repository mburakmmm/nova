# Nova Roadmap & Upstream RFCs

This roadmap documents the phases of Nova and proposals for the upstream Nox compiler and standard library runtime.

## Completed (Phase 0 - 2)

- [x] Full architectural scaffolding adhering to `Nova_AGENTS.md`.
- [x] Verified GET/POST client over HTTP and HTTPS.
- [x] URL resolution with base_url, path join, and safe query encoding.
- [x] Case-insensitive `Headers` with CRLF injection guards.
- [x] Basic and Bearer authentication with credential redaction.
- [x] Per-client `CookieJar` with domain isolation and `Set-Cookie` parsing.
- [x] Configurable `RetryPolicy` with exponential backoff and idempotency safety.
- [x] Rich `Response` wrapper with predicates, `raise_for_status()`, and `json()` decoding.
- [x] Structured error hierarchy (`NovaError` and 9 specialized exceptions).
- [x] 11 unit and integration tests passing end-to-end under `noxc test`.

---

## Upstream Proposal for Nox Runtime (`nox-lang`)

### 1. Export Generic HTTP Method in `noxrt.o`
In `nox-lang/runtime/stdlib_shims/http_client.zig`, the internal `doRequest` function already accepts `method: std.http.Method`. However, only `nox_http_get_raw` and `nox_http_post_raw` are exported:

```zig
// Proposal: Export generic request shim
export fn nox_http_request_raw(
    rt: ?*anyopaque,
    method: ?[*:0]const u8,
    url: ?[*:0]const u8,
    body: ?[*:0]const u8,
    headers: ?*anyopaque
) callconv(.c) ?*anyopaque
```

Once exported in `noxrt.o` and declared in `stdlib/nox/http.nox`, Nova can immediately enable `PUT`, `PATCH`, `DELETE`, `HEAD`, and `OPTIONS` without changing Nova's public API structure.

### 2. Request Timeout Parameter
Add a `timeout_ms: i64` parameter to `std.http.Client` request configuration in `http_client.zig` to enable true request-level socket/read timeouts.

### 3. Binary & Multipart Streaming
When byte buffers (`buffer.nox` / `std.ArrayList(u8)`) are integrated with `http_client.zig`, Nova can support true binary downloads and streaming file uploads.
