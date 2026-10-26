# Nova Roadmap & Upstream RFCs

> This document synchronizes with [ROADMAP.md](../ROADMAP.md).

For the full phase-by-phase breakdown and checklist, see the root [ROADMAP.md](../ROADMAP.md).

## Completed Phases
- **Phase 0 — Discovery and Feasibility**: Complete.
- **Phase 1 — Nova MVP**: Complete.
- **Phase 2 — Client Ergonomics**: Complete.

## Current Milestone (Phase 3)
- **Arbitrary HTTP Methods**: PUT/PATCH/DELETE/HEAD/OPTIONS. (Requires upstream `nox_http_request_raw` export).
- **Request Timeout**: Socket/read timeout hooks. (Requires upstream `std.http.Client` timeout integration).
- **Multipart Form Upload**: RFC 7578 pure Nox multipart builder.
- **Redirect Policy**: Cross-origin credential stripping.

## Upstream RFC Proposals for `nox-lang`

### 1. Export Generic HTTP Method in `noxrt.o`
In `nox-lang/runtime/stdlib_shims/http_client.zig`:

```zig
export fn nox_http_request_raw(
    rt: ?*anyopaque,
    method: ?[*:0]const u8,
    url: ?[*:0]const u8,
    body: ?[*:0]const u8,
    headers: ?*anyopaque
) callconv(.c) ?*anyopaque
```

### 2. Request Timeout Parameter
Add `timeout_ms: i64` configuration in `http_client.zig` to pass to `std.http.Client`.

### 3. Binary & Streaming Support
Expose raw byte buffer responses (`buffer.nox`) in `http_client.zig` to avoid NUL-byte truncation in binary payloads.
