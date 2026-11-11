# Nova — Modern HTTP Client for Nox

[![Nox Version](https://img.shields.io/badge/noxc-2.1.52-blue.svg)](https://github.com/mburakmmm/nox-lang)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-31%20passed-brightgreen.svg)]()

> A pleasant, safe, predictable, production-oriented HTTP client for the **Nox programming language**, inspired by Python Requests and HTTPX.

---

## Table of Contents

- [What Nova Is (and Is Not)](#what-nova-is-and-is-not)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Key Features](#key-features)
  - [JSON Requests and Responses](#json-requests-and-responses)
  - [Streaming Response Reader](#streaming-response-reader)
  - [SSRF Protection Shield](#ssrf-protection-shield)
  - [Form Submission](#form-submission)
  - [Multipart Form & File Upload](#multipart-form--file-upload)
  - [Binary Body & Buffer Access](#binary-body--buffer-access)
  - [Case-Insensitive Headers & CRLF Defense](#case-insensitive-headers--crlf-defense)
  - [Query Parameters & URL Joining](#query-parameters--url-joining)
  - [Authentication & Redaction](#authentication--redaction)
  - [Cookie Management](#cookie-management)
  - [Retry Policy & Exponential Backoff](#retry-policy--exponential-backoff)
  - [Async Concurrency with Nox Tasks](#async-concurrency-with-nox-tasks)
  - [Error Hierarchy](#error-hierarchy)
- [Feature Matrix](#feature-matrix)
- [Running Tests](#running-tests)
- [License & Changelog](#license--changelog)

---

## What Nova Is (and Is Not)

**Nova is:**
- An ergonomic HTTP client for any Nox application.
- A request construction, URL normalization, and response handling layer.
- A defense-in-depth security wrapper against CRLF injection, credential leakage, and unsafe retries.

**Nova is NOT:**
- An HTTP server framework (use `nox.http.serve`, `nyx`, or `aether`).
- A fork of the Nox compiler or runtime.
- A TLS implementation (TLS is delegated to the verified Nox runtime).

---

## Installation

Add Nova to your `nox.json`:

```json
{
  "name": "my_project",
  "version": "0.1.0",
  "entry": "main.nox",
  "requires": [
    { "alias": "nova", "repo": "github.com/mburakmmm/nova", "ref": "v0.1.0" }
  ]
}
```

Then fetch the dependency:

```sh
noxc fetch
```

---

## Quick Start

### Simple GET Request

```nox
import nova
from nova import Response

resp: Response = nova.get("https://httpbin.org/get")

print("Status:", resp.status_code)
print("Is Success:", resp.is_success())
print("Elapsed (ms):", resp.elapsed_ms)
```

### Simple POST with JSON

```nox
import nova
from nova import Response

resp: Response = nova.post_json("https://httpbin.org/post", "{\"user\":\"nox_dev\"}")
print("Status:", resp.status_code)
```

---

## Key Features

### JSON Requests and Responses

Responses provide native JSON parsing integrated with the standard library `nox.json`:

```nox
import nova
from nova import Response
import nox.json
from nox.json import JsonValue

resp: Response = nova.get("https://httpbin.org/json")
if resp.is_success():
    data: JsonValue = resp.json()
    print("Parsed JSON keys:", nox.json.object_len(data))
```

### SSRF: strict mode and DNS validation

```nox
import nova
from nova import Client, SSRFPolicy, StaticResolver

pol: SSRFPolicy = SSRFPolicy()
pol.set_strict_hostnames(True)       # strongest: only IP literals + allow-listed hosts
pol.allow_host("api.partner.com")

# Or validate resolved IPs with your own HostResolver subclass (fail-closed):
# pol.set_resolver(MyResolver())
cli: Client = Client()
cli.set_ssrf_policy(pol)
```

> Nox has no DNS API / connect-to-validated-IP yet, so a DNS-rebinding window remains when using a resolver. See `docs/security.md` and `NOX_LIMITATIONS.md` §14.

### Lazy Line Streaming

```nox
from nova import Client, StreamResponse, LineHandler

class Printer(LineHandler):
    def on_line(self: Printer, line: str) -> bool:
        print(line)
        return True

cli: Client = Client("https://httpbin.org")
with cli.stream("GET", "/stream/20") as st:
    st.for_each_line(Printer())      # bounded memory, unlike iter_lines()
```

### Streaming Response & Context Manager

Read response data incrementally in chunks or lines via native zero-copy socket streaming, or using the `with` statement context manager:

```nox
import nova
from nova import Client, StreamResponse

cli: Client = Client("https://httpbin.org")

# Context manager guarantees the underlying socket stream is cleanly closed
with cli.stream("GET", "/stream/20") as st:
    chunk: str = st.read_chunk(1024)
    print("Received first chunk:", len(chunk))

    lines: list[str] = st.iter_lines()
    for line in lines:
        print("Chunk line:", line)
```

### Large File Streaming Download & Upload

Directly stream files between the network and filesystem without holding multi-gigabyte files in RAM:

```nox
import nova
import nova.transfer
from nova import Client, Response
from nova.transfer import download_file, upload_file

cli: Client = Client("https://httpbin.org")

# Stream directly to disk:
bytes_written: int = download_file(cli, "/bytes/1048576", "large_payload.bin")

# Stream directly from disk:
resp: Response = upload_file(cli, "/post", "large_payload.bin", "POST")
```

### Connection Pooling & Keep-Alive Reuse

Enable connection reuse across consecutive requests to eliminate TCP handshakes and TLS negotiation overhead:

```nox
import nova
from nova import Client

cli: Client = Client("https://httpbin.org")
cli.set_connection_pool(max_idle=16, idle_timeout_ms=60000)

# Subsequent requests transparently reuse keep-alive connections
resp1 = cli.get("/get")
resp2 = cli.get("/get")
print("Active idle pool connections:", cli.get_idle_connections())
```

### SSRF Protection Shield

Prevent Server-Side Request Forgery by blocking requests to RFC 1918 private IPs, loopback, link-local, cloud metadata (`169.254.169.254`), and IPv4-mapped IPv6 evasion attempts on both initial requests and redirect hops:

```nox
import nova
from nova import Client, SSRFPolicy
from errors import SSRFSecurityError

cli: Client = Client()
cli.set_ssrf_policy(SSRFPolicy())

try:
    # Attempting to fetch cloud metadata is blocked immediately
    cli.get("http://169.254.169.254/latest/meta-data")
except SSRFSecurityError as err:
    print("Blocked malicious destination:", err)
```

### Form Submission

Submit URL-encoded forms effortlessly:

```nox
import nova
from nova import Response

form: dict[str, str] = {"grant_type": "password", "username": "ada"}
resp: Response = nova.post_form("https://httpbin.org/post", form)
```

### Multipart Form & File Upload

Upload files and form fields using RFC 7578 multipart/form-data encoding:

```nox
import nova
from nova import Client, Response
import multipart
from multipart import MultipartEncoder, MultipartFile, file_from_path

cli: Client = Client("https://httpbin.org")

enc: MultipartEncoder = MultipartEncoder()
enc.add_field("description", "Invoice upload")

# Attach file in memory or from disk
file_item: MultipartFile = MultipartFile("doc", "notes.txt", "Plain text notes", "text/plain")
enc.add_file(file_item)

# Or load from disk: enc.add_file(file_from_path("attachment", "report.pdf", "application/pdf"))

resp: Response = cli.post_multipart("/post", enc)
print("Uploaded successfully. Status:", resp.status_code)
```

### Binary Body & Buffer Access

For binary files, images, or payloads with embedded NUL (`\x00`) bytes, access raw byte buffers via `nox.bytes`:

```nox
import nova
from nova import Response
from nox.bytes import Buffer

resp: Response = nova.get("https://httpbin.org/bytes/1024")
buf: Buffer = resp.bytes()
print("Downloaded bytes length:", len(buf))
```

### Case-Insensitive Headers & CRLF Defense

Headers follow RFC 7230 case-insensitivity and strictly reject carriage return / line feed injection:

```nox
import nova
from nova import Client, Response

cli: Client = Client("https://httpbin.org")
cli.set_header("X-API-Version", "1.0")

# Header lookup is case-insensitive
resp: Response = cli.get("/get", None, {"x-api-version": "2.0"})
```

### Query Parameters & URL Joining

URLs are safely joined with `base_url`, query parameters are predictably encoded, and URL fragments (`#`) are stripped per RFC 7230 §5.1:

```nox
import nova
from nova import Client, Response

cli: Client = Client("https://httpbin.org")
resp: Response = cli.get("/get", {"query": "nox language", "page": "1"})
```

### Authentication & Redaction

Built-in `BasicAuth` and `BearerAuth` with automatic token redaction for logging safety:

```nox
import nova
from nova import Client, BasicAuth, BearerAuth

cli: Client = Client("https://httpbin.org")
cli.set_basic_auth("username", "secret_pass")
# Or: cli.set_bearer_auth("my_jwt_token")

# Password is safe from log leaks:
print(cli.basic_auth.redacted()) # Prints: Basic username:***
```

### Cookie Management

Each client session maintains an isolated `CookieJar`:

```nox
import nova
from nova import Client, Response

cli: Client = Client("https://httpbin.org")
cli.enable_cookies()

# Cookies received via Set-Cookie are captured and sent on subsequent requests
resp: Response = cli.get("/cookies/set?session=xyz")
```

### Retry Policy & Exponential Backoff

Configurable retry policy with bounded exponential backoff and idempotency protection (POST is not retried without explicit opt-in):

```nox
import nova
from nova import Client, RetryPolicy

cli: Client = Client("https://httpbin.org")
# Retry up to 3 times, starting at 100ms backoff, capped at 5000ms
cli.set_retry_policy(RetryPolicy(3, 100, 5000))
```

### Async Concurrency with Nox Tasks

Nox provides a fiber-based task scheduler with work-stealing threads (`spawn` and `Task[T]`). You can run multiple requests concurrently without blocking the main fiber:

```nox
import nova
from nova import Response

async def fetch_api(endpoint: str) -> Response:
    return nova.get("https://httpbin.org" + endpoint)

t1: Task[Response] = spawn fetch_api("/get")
t2: Task[Response] = spawn fetch_api("/status/200")

resp1: Response = await t1
resp2: Response = await t2
print("Concurrent requests completed:", resp1.status_code, resp2.status_code)
```

### Error Hierarchy

Nova provides an explicit exception taxonomy rooted at `NovaError`:

```nox
import nova
from nova import Client, Response
import errors
from errors import HttpStatusError, TransportError, NovaError

cli: Client = Client("https://httpbin.org")

try:
    resp: Response = cli.get("/status/500")
    resp.raise_for_status()
except HttpStatusError as he:
    print("HTTP Error:", he.status_code, "for URL:", he.url)
except TransportError as te:
    print("Network/Transport Error:", te)
except NovaError as ne:
    print("General Nova Error:", ne)
```

---

## Feature Matrix

| Feature | Status | Notes |
|---|---|---|
| GET / POST | ✅ Supported | Verified over HTTP & HTTPS |
| JSON Parse / Encode | ✅ Supported | Integrated with `nox.json` |
| URL-encoded Forms | ✅ Supported | Automatic `application/x-www-form-urlencoded` |
| Multipart Form & Upload | ✅ Supported | RFC 7578 multipart encoder and disk file loader |
| Case-Insensitive Headers | ✅ Supported | CRLF injection screened |
| URL Join & Query Encoding | ✅ Supported | Strips fragments, validates schemes |
| Basic & Bearer Auth | ✅ Supported | Redacted representations |
| Per-Client CookieJar | ✅ Supported | Domain isolation, Set-Cookie parsing |
| Exponential Backoff | ✅ Supported | Idempotency guarded, Retry-After respected |
| PUT / PATCH / DELETE / HEAD / OPTIONS | ✅ Supported | Native stdlib `nox.http.request` transport, HEAD keep-alive fix |
| Request Timeout | ✅ Supported | True socket timeout (`timeout_ms`) & `TimeoutError` |
| Binary Body Access | ✅ Supported | Native `Response.bytes() -> Buffer` via `nox.bytes` |
| Streaming Response Reader | ✅ Supported | Native zero-copy socket streaming, `read_chunk()`, `with` manager |
| Large File Disk Transfer | ✅ Supported | Direct disk streaming via `nova.transfer` (`download_file` / `upload_file`) |
| Connection Pooling | ✅ Supported | Reusable TCP/TLS pool via `client.set_connection_pool()` (**process-wide** scope) |
| HTTP / HTTPS Proxy | ✅ Supported | Transparent `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY` with `CONNECT` tunnel |
| SSRF Protection Shield | ⚠️ Partial | Real IPv4/IPv6 parser, resolver validation, strict-hostname mode. DNS-rebinding TOCTOU needs Nox runtime support — use `set_strict_hostnames(True)` for untrusted URLs |
| Cookie Expiry / Public Suffix | ✅ Supported | `Expires`/`Max-Age`, curated PSL subset (not the full list) |
| Multiple `Set-Cookie` | ⚠️ Partial | Nova supports it; current Nox runtime keeps only the last header |
| Lazy Streaming | ✅ Supported | `read_line`, `for_each_line`, `for_each_chunk` (`iter_*` buffer) |
| Retry jitter / HTTP-date `Retry-After` | ✅ Supported | Opt-in jitter |
| Transport Injection | ✅ Supported | `Client.set_transport()`, `MockTransport` |
| Async Concurrency | ✅ Supported | Fiber tasks via Nox runtime (`spawn` / `Task[T]`) |

---

## Running Tests

Run the full automated test suite with `noxc test`:

```sh
noxc test
```

Output:
```text
31 passed, 0 failed (31 total)
```

Run demonstration:

```sh
noxc run main.nox
```

---

## License & Changelog

- **License**: [MIT](LICENSE)
- **Changelog**: See [CHANGELOG.md](CHANGELOG.md) for version history.
