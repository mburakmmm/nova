# Nova — Modern HTTP Client for Nox

[![Nox Version](https://img.shields.io/badge/noxc-2.0.27-blue.svg)](https://github.com/mburakmmm/nox-lang)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-11%20passed-brightgreen.svg)]()

> A pleasant, safe, predictable, production-oriented HTTP client for the **Nox programming language**, inspired by Python Requests and HTTPX.

---

## Table of Contents

- [What Nova Is (and Is Not)](#what-nova-is-and-is-not)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Key Features](#key-features)
  - [JSON Requests and Responses](#json-requests-and-responses)
  - [Form Submission](#form-submission)
  - [Case-Insensitive Headers & CRLF Defense](#case-insensitive-headers--crlf-defense)
  - [Query Parameters & URL Joining](#query-parameters--url-joining)
  - [Authentication & Redaction](#authentication--redaction)
  - [Cookie Management](#cookie-management)
  - [Retry Policy & Exponential Backoff](#retry-policy--exponential-backoff)
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

### Form Submission

Submit URL-encoded forms effortlessly:

```nox
import nova
from nova import Response

form: dict[str, str] = {"grant_type": "password", "username": "ada"}
resp: Response = nova.post_form("https://httpbin.org/post", form)
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
| Case-Insensitive Headers | ✅ Supported | CRLF injection screened |
| URL Join & Query Encoding | ✅ Supported | Strips fragments, validates schemes |
| Basic & Bearer Auth | ✅ Supported | Redacted representations |
| Per-Client CookieJar | ✅ Supported | Domain isolation, Set-Cookie parsing |
| Exponential Backoff | ✅ Supported | Idempotency guarded |
| PUT / PATCH / DELETE | ⏳ Proposed | Gated by upstream `noxrt.o` export (raises `UnsupportedFeatureError`) |
| Request Timeout | ⏳ Planned | Awaiting runtime timeout hook |
| Streaming / Binary | ⏳ Planned | Awaiting byte-buffer transport support |

---

## Running Tests

Run the full automated test suite with `noxc test`:

```sh
noxc test
```

Output:
```text
11 passed, 0 failed (11 total)
```

Run demonstration:

```sh
noxc run main.nox
```

---

## License & Changelog

- **License**: [MIT](LICENSE)
- **Changelog**: See [CHANGELOG.md](CHANGELOG.md) for version history.
