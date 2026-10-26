# Changelog

All notable changes to **Nova** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
