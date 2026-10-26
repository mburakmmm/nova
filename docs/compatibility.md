# Compiler & Environment Compatibility

This document records verified compiler versions, stdlib capabilities, and runtime observations for Nova.

## Toolchain Verification

- **Compiler**: `noxc 2.0.27`
- **Compiler Source**: [https://github.com/mburakmmm/nox-lang](https://github.com/mburakmmm/nox-lang)
- **Platforms Verified**: macOS (Darwin arm64 / Apple Silicon)
- **Backends**: LLVM (default), QBE

## Standard Library Modules Verified

| Module | Verification Status | Used in Nova |
|---|---|---|
| `nox.http` | Verified (`get`, `post`, `HttpResponse`, `HttpError`) | Core transport via `TransportAdapter` |
| `nox.url` | Verified (`parse`, `query_encode`, `query_decode`, `join`) | URL normalization, query encoding |
| `nox.json` | Verified (`parse`, `dump`, `JsonValue`, `JsonError`) | Response body JSON decoding |
| `nox.base64` | Verified (`encode`, `decode`) | Basic authentication header encoding |
| `nox.strings` | Verified (`split`, `trim`, `lower`, `upper`, `replace`, `byte_at`) | Header normalization, CRLF scanning |
| `nox.time` | Verified (`now_ms`, `sleep_ms`) | Latency tracking and backoff delays |
| `nox.test` | Verified (`assert_true`, `assert_eq_int`, `assert_eq_str`) | Comprehensive unit and integration test suite |

## Runtime Observations

1. `nox.http` client runtime (`runtime/stdlib_shims/http_client.zig`) uses Zig's `std.http.Client` over OS threads with self-pipe completion.
2. In the installed `noxrt.o`, only `nox_http_get_raw` and `nox_http_post_raw` are exported for client usage.
3. Redirect handling is automatic and handled internally by `nox.http` without exposed redirect control policies.
4. Automatic gzip/deflate response decoding is performed by `nox.http`.
