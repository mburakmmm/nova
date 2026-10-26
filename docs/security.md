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

## 6. Cookie Isolation

Nova uses an explicit `CookieJar` per `Client` instance. There is NO global mutable cookie jar. Cookies are scoped to domains and are not transmitted cross-origin.
