# Nova Architecture

Nova is designed as a layered, modular HTTP client for the Nox programming language, inspired by Python Requests and HTTPX while adhering strictly to Nox's static typing and runtime capabilities.

## Layer Diagram

```text
User Application / Web Framework (Nyx, Aether, etc.)
                      │
              Nova Public API
        (nova.get, nova.post, etc.)
                      │
       Client Session & Request Pipeline
     (base_url, default headers, cookies)
                      │
  URL + Headers + Auth + CookieJar + Errors
                      │
              Transport Adapter
           (TransportAdapter in Nox)
                      │
       Verified Nox Standard Library
        (nox.http, nox.url, nox.json)
```

## Architectural Principles

1. **Explicit Transport Separation**:
   `transport.nox` is the sole module interacting with `nox.http`. All requests pass through `TransportAdapter.execute()`, ensuring higher layers do not depend directly on stdlib quirks or native runtime handles.

2. **No Faked Capabilities**:
   Features not supported by the underlying runtime transport (such as PUT/PATCH/DELETE methods, streaming, connection pooling) explicitly raise `UnsupportedFeatureError` rather than silently degrading or faking behavior.

3. **Immutable Configurations & Instance Isolation**:
   No global mutable state or shared cookie jars exist. Each `Client` instance maintains its own isolated headers, cookies, and retry policies.

4. **Security by Default**:
   Headers are screened for CRLF injection, URLs are validated against dangerous schemes, fragments are stripped before network transmission, and credentials in URLs or auth headers are redacted in string representations and logs.
