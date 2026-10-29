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

### `nova.post_json(url: str, json_str: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
Sends an HTTP POST request with `Content-Type: application/json`.

### `nova.post_form(url: str, data: dict[str, str], params: dict[str, str] | None = None, headers: dict[str, str] | None = None, timeout_ms: int = -1) -> Response`
Sends an HTTP POST request with `Content-Type: application/x-www-form-urlencoded`.

---

## `Client` Class

```nox
from nova import Client, Response, StreamResponse, SSRFPolicy
```

### Constructor
`Client(base_url: str = "", raise_for_status: bool = False, timeout_ms: int = -1, max_redirects: int = 5)`

### Configuration Methods
- `set_header(name: str, value: str) -> Client`
- `set_basic_auth(username: str, password: str) -> Client`
- `set_bearer_auth(token: str) -> Client`
- `enable_cookies() -> Client`
- `set_retry_policy(policy: RetryPolicy) -> Client`
- `set_ssrf_policy(policy: SSRFPolicy) -> Client`

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
- `close() -> None`: Closes the stream.

---

## `SSRFPolicy` Class

```nox
from nova import SSRFPolicy
```

### Constructor
`SSRFPolicy(allow_private: bool = False, allow_loopback: bool = False, allow_link_local: bool = False)`

- `validate_url(url_str: str) -> None`: Validates target host and scheme. Raises `SSRFSecurityError` if the destination targets restricted IP ranges (IPv4/IPv6 private, loopback, link-local, cloud metadata `169.254.169.254`, IPv4-mapped IPv6, or dangerous hostnames).

---

## `RetryPolicy` Class

```nox
from nova import RetryPolicy
```

### Constructor
`RetryPolicy(max_retries: int = 0, backoff_factor_ms: int = 100, max_backoff_ms: int = 10000, retry_on_transport_error: bool = True, retry_post: bool = False)`

- `calculate_delay_ms(attempt: int) -> int`: Returns bounded exponential backoff duration.
- `is_status_retryable(status_code: int) -> bool`: Identifies transient status codes (408, 429, 500, 502, 503, 504).
