# Compiler & Environment Compatibility

This document records verified compiler versions, stdlib capabilities, and runtime observations for Nova.

## Toolchain Verification

- **Compiler**: `noxc 2.1.186`
- **Compiler Source**: [https://github.com/mburakmmm/nox-lang](https://github.com/mburakmmm/nox-lang)
- **Platforms Verified (Full Native + `noxclibs`)**: macOS (Darwin arm64 / Apple Silicon), Linux (Ubuntu x86-64 / arm64), Windows (x86-64)
- **Pure-Nox Cross-Compilation Targets Verified (`nova.nox` core)**: `wasm32-wasi`, `wasm32-freestanding`, `ios-arm64`, `android-arm64`
- **Backends**: LLVM (default), QBE

## Standard Library Modules Verified

| Module | Verification Status | Used in Nova |
|---|---|---|
| `nox.http` | Verified (`get`, `post`, `request`, `stream`, `stream_upload`, `set_http3`, `client_pool`, `HttpStream`) | Core transport via `TransportAdapter` |
| `nox.url` | Verified (`parse`, `query_encode`, `query_decode`, `join`) | URL normalization, query encoding |
| `nox.json` | Verified (`parse`, `dump`, `dump_pretty`, `JsonValue`, `JsonError`) | Default JSON decoding & WASM/mobile `NoxJsonReader` fallback |
| `nox.yyjson` | Verified Desktop-only (`noxclibs.a`) | Optional accelerated `YyJsonReader` (`yyjson_adapter.nox`) |
| `nox.brotli` | Verified Desktop-only (`noxclibs.a`) | Optional `Content-Encoding: br` decoding (`brotli_codec.nox`) |
| `nox.base64` | Verified (`encode`, `decode`) | Basic authentication header encoding |
| `nox.bytes` | Verified (`from_str`, `to_str`) | Binary `Buffer` bridging |
| `nox.strings` | Verified (`split`, `trim`, `lower`, `upper`, `replace`, `byte_at`, `byte_len`) | Header normalization, CRLF scanning, UTF-8 byte limits, O(1) PSL build |
| `nox.time` | Verified (`now_ms`, `sleep_ms`, `instant_now`) | Latency tracking and backoff delays |
| `nox.test` | Verified (`assert_true`, `assert_eq_int`, `assert_eq_str`) | Comprehensive unit and integration test suite |

## Runtime & Target Boundary Observations

1. `nox.http` client runtime (`runtime/stdlib_shims/http_client.zig`) supports `request`, `stream`, `stream_upload`, connection pooling (`client_pool`), proxy env vars, HTTP/2, and Alt-Svc HTTP/3 (`set_http3`).
2. `nox.http` automatically decodes `gzip` and `deflate` response bodies; `Content-Encoding: br` is passed through raw and handled cleanly by `BrotliDecoder` (desktop) or rejected explicitly by `FallbackContentDecoder` (WASM/mobile).
3. Modules backed by `noxclibs.a` (`nox.brotli`, `nox.yyjson`) are desktop-only (macOS, Linux, Windows) and rejected on `wasm32-*` and mobile (`ios-*`, `android-*`). Nova isolates those into opt-in `brotli_codec.nox` and `yyjson_adapter.nox` so core `nova` always compiles cleanly on WASM and mobile with pure-Nox fallbacks (`FallbackContentDecoder`, `NoxJsonReader`).
4. Windows parity (`v2.1.147`+) supports fiber-cooperative client networking, proxy tunnels, and TLS/HTTP/2/HTTP/3 (OpenSSL 3.5+ runtime DLLs).
5. `nox.json` declares `"source": "nox"` and `noxc sbom` produces CycloneDX 1.5 metadata.
