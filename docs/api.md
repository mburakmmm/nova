# Nova API Reference

## Top-Level Functions

Imported from `nova`:

```nox
import nova
from nova import Response
```

### `nova.get(url: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
Sends an HTTP GET request.

### `nova.post(url: str, body: str = "", json: str = "", params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
Sends an HTTP POST request with raw text or JSON body.

### `nova.put(url: str, body: str = "", json: str = "", params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
Sends an HTTP PUT request.

### `nova.patch(url: str, body: str = "", json: str = "", params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
Sends an HTTP PATCH request.

### `nova.delete(url: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
Sends an HTTP DELETE request.

### `nova.head(url: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
Sends an HTTP HEAD request.

### `nova.options(url: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
Sends an HTTP OPTIONS request.

### `nova.stream(method: str, url: str, body: str = "", json: str = "", params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> StreamResponse`
Sends a request and returns an incremental `StreamResponse`.

### `nova.set_connection_pool(max_idle: int = 32, idle_timeout_ms: int = 90000) -> None`
Configures process-wide HTTP connection pool parameters.

### `nova.idle_connections() -> int`
Returns the count of active idle connections currently held in the pool.

### `nova.download_to_file(url: str, target_path: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> int`
Streams remote response directly to local disk file without whole-body memory buffering. Returns HTTP status code.

### `nova.upload_file(url: str, source_path: str, method: str = "POST", params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
Streams local disk file directly to remote server without loading file into RAM. Returns Response.

### `nova.post_json(url: str, json_str: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
Sends an HTTP POST request with `Content-Type: application/json`.

### `nova.post_form(url: str, data: dict[str, str], params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
Sends an HTTP POST request with `Content-Type: application/x-www-form-urlencoded`.

### `nova.safe_client(base_url: str = "", timeout_ms: int = 15000, max_redirects: int = 3, ssrf_policy: SSRFPolicy | None = None) -> Client`
Returns a pre-hardened `Client` instance configured for untrusted URLs with active `SSRFPolicy` (blocking private/loopback/metadata ranges), `raise_for_status=True`, default 15s timeout, and strict 3-redirect limit.

---

## `Client` Class

```nox
from nova import Client, create_safe_client, Response, StreamResponse, SSRFPolicy
```

### Constructor
`Client(base_url: str = "", raise_for_status: bool = False, timeout_ms: int = -1, max_redirects: int = 5, ssrf_policy: SSRFPolicy | None = None)`

### Factory Functions
- `create_safe_client(base_url: str = "", timeout_ms: int = 15000, max_redirects: int = 3, ssrf_policy: SSRFPolicy | None = None) -> Client`: Pre-hardened client for untrusted destinations.

### Configuration Methods
- `set_header(name: str, value: str) -> Client`
- `set_basic_auth(username: str, password: str) -> Client`
- `set_bearer_auth(token: str) -> Client`
- `enable_cookies() -> Client`
- `set_retry_policy(policy: RetryPolicy) -> Client`
- `set_ssrf_policy(policy: SSRFPolicy) -> Client`
- `set_connection_pool(max_idle: int = 32, idle_timeout_ms: int = 90000) -> Client`
- `get_idle_connections() -> int`

### Request Methods
- `get(url: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
- `post(url: str, body: str = "", json: str = "", params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
- `put(url: str, body: str = "", json: str = "", params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
- `patch(url: str, body: str = "", json: str = "", params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
- `delete(url: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
- `head(url: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
- `options(url: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
- `post_multipart(url: str, encoder: MultipartEncoder, params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
- `stream(method: str, url: str, body: str = "", json: str = "", params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> StreamResponse`
- `request(method: str, url: str, body: str = "", json: str = "", params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`

---

## `Response` Class

```nox
from nova import Response
```

### Properties
- `status_code: int`: HTTP status code (e.g. 200, 404).
- `body: str`: Raw response body as string.
- `headers: Headers`: Case-insensitive response headers.
- `url: str`: Final request URL.
- `method: str`: HTTP method used.
- `elapsed_ms: int`: Total request duration in milliseconds.

### Predicates & Helpers
- `is_success() -> bool`: Returns `True` if `200 <= status_code <= 299`.
- `is_redirect() -> bool`: Returns `True` if `300 <= status_code <= 399`.
- `is_client_error() -> bool`: Returns `True` if `400 <= status_code <= 499`.
- `is_server_error() -> bool`: Returns `True` if `500 <= status_code <= 599`.
- `is_error() -> bool`: Returns `True` if `status_code >= 400`.
- `raise_for_status() -> None`: Raises `HttpStatusError` if `status_code >= 400`.
- `json() -> JsonValue`: Parses body using `nox.json.parse()`. Raises `DecodeError` on failure.
- `text() -> str`: Returns body string.
- `bytes() -> Buffer`: Returns raw response body as a binary `Buffer` (preserving embedded NUL and arbitrary byte values).

---

## `StreamResponse` Class

```nox
from nova import StreamResponse
```

### Properties
- `status_code: int`: HTTP status code.
- `headers: Headers`: Case-insensitive headers.
- `url: str`: Request URL.
- `method: str`: HTTP method.
- `is_closed: bool`: Flag indicating if the stream has been closed.

### Methods
- `read_chunk(chunk_size: int = 8192) -> str`: Reads up to `chunk_size` characters as text. Returns `""` on EOF.
- `read_chunk_bytes(chunk_size: int = 8192) -> Buffer`: Reads up to `chunk_size` bytes as a binary `Buffer`. Returns an empty `Buffer` on EOF.
- `iter_bytes(chunk_size: int = 8192) -> list[Buffer]`: Yields all chunks as a list of binary `Buffer` blocks.
- `iter_lines() -> list[str]`: Yields lines split by `\n` (stripping trailing `\r`).
- `read_all() -> str`: Reads all remaining characters until EOF.
- `close() -> None`: Closes the stream and releases the underlying socket.
- `__enter__() -> StreamResponse`: Context manager entry.
- `__exit__(exc_type, exc_val, exc_tb) -> None`: Closes stream automatically upon exiting `with` block.

---

## `nova.transfer` Module

```nox
from nova.transfer import download_file, upload_file, download, upload
```

- `download_file(cli: Client, url: str, target_path: str, params: dict | None = None, headers: dict | None = None, timeout_ms: int = -1) -> int`: Streams directly from socket to file on disk. Returns status code.
- `upload_file(cli: Client, url: str, source_path: str, method: str = "POST", params: dict | None = None, headers: dict | None = None, timeout_ms: int = -1) -> Response`: Streams directly from file on disk to socket.
- `download(url: str, target_path: str, ...) -> int`: Top-level standalone shortcut.
- `upload(url: str, source_path: str, ...) -> Response`: Top-level standalone shortcut.

---

## `SSRFPolicy` Class

```nox
from nova import SSRFPolicy
```

### Constructor
`SSRFPolicy(allow_private: bool = False, allow_loopback: bool = False, allow_link_local: bool = False)`

- `validate_target(url_str: str) -> None`: Validates target host and scheme. Raises `SSRFSecurityError` if the destination targets restricted IP ranges (IPv4/IPv6 private, loopback, link-local, cloud metadata `169.254.169.254`, IPv4-mapped IPv6, or dangerous hostnames).
- `allow_host(host: str) -> SSRFPolicy`: Adds host to explicit allowlist.
- `block_host(host: str) -> SSRFPolicy`: Adds host to explicit blocklist.
- `set_resolver(resolver: HostResolver) -> SSRFPolicy`: Attaches a DNS resolver to validate all resolved IP addresses (fail-closed).
- `set_skip_dns_for_allowlist(skip: bool = True) -> SSRFPolicy`: When `False` (default), allowlisted hostnames also have their resolved IPs validated against private ranges.
- `set_strict_hostnames(enabled: bool = True) -> SSRFPolicy`: Requires all targets to be validated IP literals or explicitly allowed hostnames.

---

## `RetryPolicy` Class

```nox
from nova import RetryPolicy
```

### Constructor
`RetryPolicy(max_retries: int = 0, backoff_factor_ms: int = 100, max_backoff_ms: int = 10000, retry_on_transport_error: bool = True, retry_post: bool = False)`

- `calculate_delay_ms(attempt: int) -> int`: Returns bounded exponential backoff duration.
- `is_status_retryable(status_code: int) -> bool`: Identifies transient status codes (408, 429, 500, 502, 503, 504).

---

## v0.6.0 additions

### `SSRFPolicy`
- `set_resolver(r: HostResolver) -> SSRFPolicy` — validate every resolved IP (fail-closed).
- `set_strict_hostnames(enabled: bool = True) -> SSRFPolicy` — only IP literals and allow-listed hostnames.
- `validate_resolved(url: str, host: str, ips: list[str]) -> None`
- `HostResolver.resolve(host: str) -> list[str]` (subclass), `StaticResolver.add(host, ips)`.
- `parse_ip(host: str) -> IPAddress`, `classify_ip(ip) -> str` (`""`, `loopback`, `link_local`, `private`, `reserved`).

### `StreamResponse` (lazy)
- `read_line() -> str | None`, `for_each_line(handler: LineHandler) -> int`, `for_each_chunk(handler: ChunkHandler, chunk_size: int = 4096) -> int`, `max_line_bytes` (default 1 MiB).

### `CookieJar`
- `add_public_suffix(suffix)`, `purge_expired() -> int`, `now_override_s` (deterministic clock); `Cookie.expires`, `Cookie.same_site`.

### `Headers`
- `set_multi(name, values)`, `get_all(name) -> list[str]`; `response_headers_from_dict(d)`.

### `RetryPolicy`
- `set_jitter(mode: str)` (`"none"`, `"full"`, `"equal"`), `next_delay_ms(attempt)`, `jittered_delay_ms(attempt, sample_permille)`; `parse_retry_after_ms(value, now_s)`.

### Transport injection
- `Transport` (base), `TransportAdapter` (nox.http), `MockTransport` (`add_response`, `add_error`, `route`, `requests`), `Client.set_transport(t)`.
- `Client.connection_pool_scope() -> str` — always `"process"`.
