# Nova API Reference

## Top-Level Functions

Imported from `nova`:

```nox
import nova
from nova import Response
```

### `nova.get(url: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None) -> Response`
Sends an HTTP GET request.

### `nova.post(url: str, body: str = "", json: str = "", params: dict[str, str] | None = None, headers: dict[str, str] | None = None) -> Response`
Sends an HTTP POST request with raw text or JSON body.

### `nova.post_json(url: str, json_str: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None) -> Response`
Sends an HTTP POST request with `Content-Type: application/json`.

### `nova.post_form(url: str, data: dict[str, str], params: dict[str, str] | None = None, headers: dict[str, str] | None = None) -> Response`
Sends an HTTP POST request with `Content-Type: application/x-www-form-urlencoded`.

---

## `Client` Class

```nox
from nova import Client, Response
```

### Constructor
`Client(base_url: str = "", raise_for_status: bool = False)`

### Configuration Methods
- `set_header(name: str, value: str) -> Client`
- `set_basic_auth(username: str, password: str) -> Client`
- `set_bearer_auth(token: str) -> Client`
- `enable_cookies() -> Client`
- `set_retry_policy(policy: RetryPolicy) -> Client`

### Request Methods
- `get(url: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None) -> Response`
- `post(url: str, body: str = "", json: str = "", params: dict[str, str] | None = None, headers: dict[str, str] | None = None) -> Response`
- `post_json(url: str, json_str: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None) -> Response`
- `post_form(url: str, data: dict[str, str], params: dict[str, str] | None = None, headers: dict[str, str] | None = None) -> Response`
- `request(method: str, url: str, body: str = "", json: str = "", params: dict[str, str] | None = None, headers: dict[str, str] | None = None) -> Response`

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

---

## `RetryPolicy` Class

```nox
from nova import RetryPolicy
```

### Constructor
`RetryPolicy(max_retries: int = 0, backoff_factor_ms: int = 100, max_backoff_ms: int = 10000, retry_on_transport_error: bool = True, retry_post: bool = False)`

- `calculate_delay_ms(attempt: int) -> int`: Returns bounded exponential backoff duration.
- `is_status_retryable(status_code: int) -> bool`: Identifies transient status codes (408, 429, 500, 502, 503, 504).
