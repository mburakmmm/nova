# Security & Best Practices

Nova takes defensive security seriously. Every HTTP client handles untrusted user input, external networks, and sensitive tokens.

## 1. CRLF Injection Prevention

HTTP header injection occurs when untrusted input contains carriage returns (`\r` / `\x0D`) or line feeds (`\n` / `\x0A`), allowing an attacker to inject arbitrary headers or split HTTP responses.

Nova's `Headers.set()` and `validate_header_entry()` scan both header names and values for `\r` and `\n` characters before any request is queued. If detected, an immediate `InvalidHeaderError` is raised.

## 2. Embedded Credentials Rejection

URLs formatted as `https://user:password@host/path` present significant security risks, as passwords can leak into logs, proxies, referrers, and error traces.

Nova's `resolve_url()` inspects `u.userinfo`. If userinfo is present in the URL, `InvalidUrlError` is immediately raised. Callers must use explicit `BasicAuth` or `BearerAuth` headers instead.

## 3. URL Sanitization in Logs & Errors

When errors occur or URLs are represented, `sanitize_url()` redacts any userinfo passwords to `user:***@host`, preventing secrets from appearing in error traces or logs.

## 4. URL Fragment Stripping

Per RFC 7230 §5.1, URI fragments (`#section`) are client-side only and MUST NOT be transmitted in HTTP request lines. Nova's `resolve_url()` automatically strips fragments before sending requests to the transport.

## 5. Idempotent Retry Safety

Blindly retrying non-idempotent HTTP requests (such as `POST`) upon encountering transient server errors can cause duplicate payments, orders, or data mutations.

By default, Nova's `RetryPolicy` only retries idempotent methods (`GET`, `HEAD`, `OPTIONS`). Retrying `POST` requires explicit caller opt-in (`retry_post=True`).

## 6. RFC 6265 Cookie Security & Storage Model

Nova uses an explicit `CookieJar` per `Client` instance. There is NO global mutable cookie jar.
- **Domain Acceptance Validation (RFC 6265 §5.3 Step 5)**: When extracting `Set-Cookie` from responses, the client validates that the request host domain-matches the cookie's `Domain` attribute. For example, `evil.example.net` cannot set cookies for `example.com`. Unrelated cookies are rejected during extraction.
- **Host-Only Cookie Isolation (RFC 6265 §5.3 Step 6)**: Cookies set without an explicit `Domain` attribute are marked `host_only = True`. Host-only cookies are strictly restricted to the exact originating host and are NEVER transmitted to subdomains or sibling domains.
- **Public Suffix Rejection**: Cookies specifying a top-level domain or public suffix without a dot (e.g., `Domain=com`, `Domain=org`) are rejected immediately.
- **Strict Dot-Matching**: For domain cookies, matching requires `host == domain` or `host` ending with `"." + domain`, preventing `notexample.com` from matching `example.com`.
- **Secure Flag Gating**: Cookies marked `Secure` are only transmitted over `https://`.

## 7. Cross-Origin Redirect Security (Credential Stripping)

When following redirects across different origins (`not is_same_origin(req.url, next_url)`):
- Sensitive headers (`Authorization` and `Proxy-Authorization`) are automatically stripped before sending the request to the new origin.
- Destination cookies are re-scoped to the new target URL via `CookieJar.apply_to_request()`.
- Redirect loops are prevented with configurable `max_redirects` bounds (`Client(max_redirects=5)`).

## 8. Header Token & Control Character Validation (RFC 7230 §3.2 & §3.2.6)

- Header names are strictly validated against RFC 7230 §3.2.6 token characters: whitespace, colons, slashes, delimiters (`()<>@,;:\"/[]?={}`), and control characters are rejected.
- Header values reject all ASCII control characters (`0x00 - 0x1F` except HTAB `0x09`) and DEL (`0x7F`), preventing HTTP response splitting, header injection, and smuggling.

## 9. Retry-After Upper Bound Protection

When handling HTTP 429 / 503 responses with a `Retry-After` header:
- The delay is capped to the policy's `max_backoff_ms` (default 30,000 ms), preventing malicious or misconfigured servers from causing client denial of service through multi-year sleep delays.
