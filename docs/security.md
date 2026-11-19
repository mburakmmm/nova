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

By default, Nova's `RetryPolicy` retries RFC 9110 idempotent methods (`GET`, `HEAD`, `OPTIONS`, `PUT`, `DELETE`). `PUT`/`DELETE` retries can be disabled via `retry_put_delete=False`, while retrying `POST` requires explicit caller opt-in (`retry_post=True`).

## 6. RFC 6265 Cookie Security & Storage Model

Nova uses an explicit `CookieJar` per `Client` instance. There is NO global mutable cookie jar.
- **Domain Acceptance Validation (RFC 6265 §5.3 Step 5)**: When extracting `Set-Cookie` from responses, the client validates that the request host domain-matches the cookie's `Domain` attribute. For example, `evil.example.net` cannot set cookies for `example.com`. Unrelated cookies are rejected during extraction.
- **Host-Only Cookie Isolation (RFC 6265 §5.3 Step 6)**: Cookies set without an explicit `Domain` attribute are marked `host_only = True`. Host-only cookies are strictly restricted to the exact originating host and are NEVER transmitted to subdomains or sibling domains.
- **Public Suffix Rejection**: single-label domains (`com`) and multi-label public suffixes from the embedded PSL subset (`co.uk`, `github.io`, …) are rejected; see §12.
- **Strict Dot-Matching**: For domain cookies, matching requires `host == domain` or `host` ending with `"." + domain`, preventing `notexample.com` from matching `example.com`.
- **Secure Flag Gating**: Cookies marked `Secure` are only transmitted over `https://`.

## 7. Cross-Origin Redirect Security (Credential Stripping)

When following redirects across different origins (`not is_same_origin(req.url, next_url)`):
- Sensitive headers (`Authorization`, `Proxy-Authorization` and `Cookie`) are automatically stripped before sending the request to the new origin.
- Destination cookies are re-scoped to the new target URL via `CookieJar.apply_to_request()`.
- Redirect loops are prevented with configurable `max_redirects` bounds (`Client(max_redirects=5)`).

## 8. Header Token & Control Character Validation (RFC 7230 §3.2 & §3.2.6)

- Header names are strictly validated against RFC 7230 §3.2.6 token characters: whitespace, colons, slashes, delimiters (`()<>@,;:\"/[]?={}`), and control characters are rejected.
- Header values reject all ASCII control characters (`0x00 - 0x1F` except HTAB `0x09`) and DEL (`0x7F`), preventing HTTP response splitting, header injection, and smuggling.

## 9. Retry-After Upper Bound Protection

When handling HTTP 429 / 503 responses with a `Retry-After` header:
- The delay is capped to the policy's `max_backoff_ms` (default 30,000 ms), preventing malicious or misconfigured servers from causing client denial of service through multi-year sleep delays.

## 10. SSRF Protection Shield (Defense in Depth)

SSRF occurs when an application fetches a remote resource from a user-supplied URL without restricting access to internal networks. Nova enforces `SSRFPolicy` on the initial URL **and on every redirect hop** (also `stream()` and `transfer`).

### Layer 1 — URL / hostname policy
Allowlist (`allow_host`), blocklist (`block_host`), `localhost` / `*.localhost` / trailing-dot FQDN forms, cloud metadata names (`metadata.google.internal`, `instance-data`).

### Layer 2 — Real IPv4 / IPv6 parsing (v0.6.0)
Hosts are parsed with a real parser — **not** string prefixes:
- IPv4 in every `inet_aton` form: `127.0.0.1`, `127.1`, `2130706433`, `0x7f000001`, `0x7f.0.0.1`, `0177.0.0.1`.
- IPv6 in every notation: compressed/expanded, zone IDs, dotted tails.
- Embedded IPv4 is classified: IPv4-mapped (`::ffff:7f00:1`), IPv4-compatible, IPv4-translated, NAT64 (`64:ff9b::/96`), 6to4 (`2002::/16`).
- Ranges: loopback, unspecified, link-local (`169.254/16`, `fe80::/10`), private (RFC 1918, CGNAT, `fc00::/7`, site-local), documentation/benchmark ranges, multicast/reserved, Teredo.
- A hostname such as `fc.example.com` / `fe80.example.com` is never mistaken for an IPv6 literal.

### Layer 3 — DNS-resolution validation & verified IP pinning (v0.6.0–v0.8.0)
A hostname can resolve to a private address (or flip between public and private — DNS rebinding). Nova provides:
- `NoxDnsResolver(timeout_ms=3000, doh_url="")` — `HostResolver` backed by `nox.dns.resolve` (system `getaddrinfo` on desktop/mobile; explicit `doh_url` on WASM).
- `SSRFPolicy.set_resolver(HostResolver)` — hostnames are resolved and **every** returned IP is validated; invalid output or an empty answer is rejected (**fail-closed**).
- `SSRFPolicy.set_pin_resolved_ip(True)` & `SSRFPolicy.validate_and_pin(url)` — pins the canonical verified IP onto `Request.connect_ip` (`nox.http.request(..., connect_ip=...)`) on buffered requests and every redirect hop, eliminating DNS-rebinding TOCTOU while keeping TLS SNI and certificate hostname verification on the original hostname. (`stream()` / `stream_upload()` raise `UnsupportedFeatureError` when `pin_resolved_ip` is active because stdlib streaming lacks `connect_ip`.)
- `SSRFPolicy.skip_dns_for_allowlist` (`bool`, default `False`) — when a resolver is configured, allowlisted hostnames also have their resolved IPs validated against private/loopback/metadata ranges, preventing DNS rebinding attacks on allowlisted partner domains. Use `set_skip_dns_for_allowlist(True)` only for internal names intentionally pointing to private IPs.
- `SSRFPolicy.validate_resolved(url, host, ips)` — public API for callers that own a resolver.
- `SSRFPolicy.set_require_dns_or_allowlist(True)` — fail-closed mode when no `HostResolver` is attached: rejects arbitrary unverified hostnames unless they resolve via a `HostResolver` or appear in the explicit allowlist.
- `SSRFPolicy.set_strict_hostnames(True)` — only IP literals and explicitly allow-listed hostnames pass.

### Layer 4 — Safe Client Factory (`nova.safe_client()`) (v0.6.1–v0.8.0)
For applications that fetch user-supplied URLs (crawlers, webhooks, proxies), `create_safe_client()` / `nova.safe_client()` returns a pre-hardened `Client`:
- Active `SSRFPolicy()` with `NoxDnsResolver(timeout_ms)` + `pin_resolved_ip = True` enabled by default (`use_system_dns=True`, `pin_dns=True`)
- `allow_https_downgrade = False` (blocks `https://` -> `http://` redirect downgrades with `SSRFSecurityError`)
- Optional `resolver: HostResolver | None = None` parameter to plug custom DNS validation (`StaticResolver` / custom subclass)
- Optional `require_dns_or_allowlist: bool = False` fail-closed guard when disabling system DNS
- `raise_for_status = True` (fails loudly on 4xx / 5xx)
- `timeout_ms = 15000` (bounded request timeout prevents slowloris hangs)
- `max_redirects = 3` (tight redirect limit against loops)

> [!NOTE]
> **Custom CA TLS Verification (`Client.set_ca_file`)**: For internal enterprise CAs or deterministic local TLS tests, `Client.set_ca_file(path)` delegates strict PEM CA verification to `nox.http.request(..., ca_file=...)` on buffered requests while preserving full hostname checks (no `verify=False` mode is ever exposed). `stream()` and `stream_upload()` fail explicitly with `UnsupportedFeatureError` if `ca_file` is configured.

## 11. Cross-Origin Redirects: Credential & Cookie Stripping (v0.6.0 / v0.8.0)

On a cross-origin hop (scheme, host or port differs — including `https → http`), Nova strips `Authorization`, `Proxy-Authorization` **and `Cookie`** — including a `Cookie` header you set manually on the client. `create_safe_client()` / `set_allow_https_downgrade(False)` blocks `https → http` redirect downgrades outright with `SSRFSecurityError`. Cookies from an enabled `CookieJar` are re-applied *for the new URL only*.

## 12. Cookie Expiry, Public Suffixes, Multiple Set-Cookie (v0.6.0 / v0.8.0)

- `Expires` (IMF-fixdate / RFC 850 / asctime) and `Max-Age` (precedence over `Expires`); `Max-Age<=0` or a past `Expires` deletes the stored cookie; expired cookies are never sent.
- Public-suffix rejection embeds the **full official Mozilla Public Suffix List** (`8,692` exact + `314` wildcard `*.` + `8` exception `!` prevailing rules) and provides `scripts/update_psl.py --apply` for automated updates, alongside runtime `CookieJar.add_public_suffix()` (including wildcard and exception rules). A host that *is* a public suffix may only set host-only cookies.
- RFC 6265 default-path, `SameSite` recorded.
- Multiple `Set-Cookie` headers delivered `\n`-joined by `nox.http` (`v2.1.195+`) are extracted cleanly into `Headers.get_all("Set-Cookie")` and stored as separate cookies by `CookieJar` (`tests/integration/multi_set_cookie_test.nox`).

## 13. Lazy Streaming & UTF-8 Byte-Bound Memory (v0.6.0 / v0.6.2)

`read_line()`, `for_each_line(handler)` and `for_each_chunk(handler)` consume a body with memory bounded by one chunk plus the current line (`max_line_bytes`, default 1 MiB, raises `DecodeError`).
In v0.6.2, `max_line_bytes` measures **raw bytes** via `nox.strings.byte_len()` rather than character counts (`len()`), preventing multi-byte UTF-8 sequences (Turkish characters, emojis) from exceeding memory bounds. `iter_lines()` / `iter_bytes()` buffer the whole body and are documented as such.

## 14. Retry Hardening (v0.6.0)

Optional `full` / `equal` jitter, `Retry-After` as delta-seconds **or HTTP-date** (capped at one year, then by `max_backoff_ms`), overflow-safe exponent. POST is still never retried unless opted in.
