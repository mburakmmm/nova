# NOX_LIMITATIONS.md — Nox Dili ve Standart Kütüphanesi Limitasyon & Çözüm Kaydı

Bu belge, **Nova HTTP Client** geliştirme sürecinde tespit edilen ve Nox çalışma zamanı (`runtime/stdlib_shims/http_client.zig`), standart kütüphanesi (`stdlib/nox/http.nox`, `stdlib/nox/bytes.nox`, `stdlib/nox/url.nox`, `stdlib/nox/transfer.nox`) ve derleyicisi (`noxc`) seviyesinde çözülen ve kalan mimari başlıkları listeler.

---

## 1. Genel HTTP Metod Desteği (PUT, PATCH, DELETE, HEAD, OPTIONS)
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.31 — Commit `491f1e08`)**
- **Uygulama:**
  - Zig çalışma zamanında `nox_http_request_raw(method, url, body, has_body, headers, timeout_ms)` dışa aktarıldı.
  - `stdlib/nox/http.nox` modülüne `request()`, `put()`, `patch()`, `delete()`, `head()`, `options()` fonksiyonları eklendi.
  - Desteklenmeyen veya geçersiz metodlar açıkça `HttpError` fırlatmaktadır.
- **Nova Entegrasyonu:** Nova v0.3.0 ile `TransportAdapter.execute()` içinde tüm metodlar doğrudan bağlandı; `UnsupportedFeatureError` kısıtlaması kaldırıldı.

---

## 2. Gerçek İstek ve Soket Zaman Aşımı (True Request Timeout)
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.31 — Commit `491f1e08`)**
- **Uygulama:**
  - `nox_http_request_raw` çağrısına `timeout_ms: int` parametresi eklendi.
  - Süre dolduğunda işletim sistemi soketi seviyesinde bağlantı iptal edilmekte ve `HttpTimeoutError` (`HttpError` alt sınıfı) fırlatılmaktadır.
  - Arka planda başıboş (dangling) iş parçacığı veya I/O bırakılmaz (`AGENTS.md §12` tam uyumlu).
- **Nova Entegrasyonu:** Nova v0.3.0 ile `Client(timeout_ms=...)` ve istek seviyesi `timeout_ms` desteği Nova `TimeoutError` ile eşleştirildi.

---

## 3. İkili / Bayt Tabanlı Gövde Desteği (Binary Body & Buffer)
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.31 — Commit `491f1e08`)**
- **Uygulama:**
  - `HttpResponse.body: str` artık gömülü `\x00` (NUL) ve geçersiz UTF-8 baytlarını uzunluk bilgisiyle bellekte aynen korumaktadır.
  - `stdlib/nox/bytes.nox` modülü ve `nox.bytes.from_str(s: str) -> Buffer` fonksiyonu eklendi.
- **Nova Entegrasyonu:** Nova v0.3.0 ile `Response.bytes() -> Buffer` metodu eklenerek ikili içerikler doğrudan `Buffer` olarak okunabilir hale getirildi.

---

## 4. Büyük Dosyalar İçin Yerel Akış ve Disk Transferi (Transfer & Chunked I/O)
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.69)**
- **Uygulama:**
  - `stdlib/nox/transfer.nox` ve çalışma zamanı şimi `download_to_file(url, path, headers, timeout_ms)` ile `upload_file(method, url, path, headers, timeout_ms)` eklendi.
  - Dosyalar tüm gövde belleğe alınmadan doğrudan soketten diske / diskten sokete akıtılmaktadır.
- **Nova Entegrasyonu:** Nova v0.5.0 ile `nova.transfer` (`download_file`, `upload_file`, `download`, `upload`) modülü eklendi.

---

## 5. Yönlendirme (Redirect) Politikası Kontrolü
- **Durum:** ✅ **ÇÖZÜLDÜ (Nova v0.2.1 / v0.2.2)**
- **Açıklama:** Nox çalışma zamanı `redirect_behavior = .unhandled` ayarladığı için 3xx yanıtları istemciye doğrudan döner. Nova katmanında döngü tespiti (`max_redirects = 5`) ve çapraz-orijin `Authorization` temizliği istemci seviyesinde tam kontrolle çözülmüştür.

---

## 6. Derleyici & Tip Sistemi İyileştirmeleri
- **A. `and` / `or` ile Flow-Sensitive Optional Daraltması:**
  - **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.30 — Commit `29a0b7af`)**
  - `if x is not None and x.foo():` sözdizimi derleyicide geçerlidir.
- **B. `int()` ve `float()` Fonksiyonlarında Boşluk Toleransı:**
  - **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.30 — Commit `29a0b7af`)**
  - `int("  42  ")` baştaki ve sondaki boşlukları otomatik temizlemektedir.
- **C. String Literallerinde Onaltılık Kaçış Dizisi (`\xHH`):**
  - **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.30 — Commit `29a0b7af`)**
  - `"\x00"` ve `"\x01"` gibi onaltılık kaçışlar desteklenmektedir.
- **D. Fonksiyon Parametrelerinde Sabit Varsayılan Değer:**
  - Bellek güvenliği kuralı olarak korunmaktadır (`headers: dict[str, str] | None = None`).

---

## 7. `nox.url` Standart Kütüphanesinde IPv6 Literal Desteği
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.30 — Commit `29a0b7af`)**
- **Açıklama:** `[::1]:8080` gibi IPv6 literal adresler `stdlib/nox/url.nox` içinde köşeli parantez korumasıyla hatasız ayrıştırılmaktadır.

---

## 8. HEAD İsteklerinde Keep-Alive Gövde Okuma Kilitlenmesi (RFC 7230 §3.3.3)
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.1.2 — `http_client.zig:909`)**
- **Uygulama:**
  - `runtime/stdlib_shims/http_client.zig` içinde `HEAD` isteklerinde veya `204 No Content`, `304 Not Modified`, `< 200 Informational` durum kodlarında gövde okuma adımı soketi tüketmeden doğrudan `ctx.response_body = &.{}` olarak sonlandırılmaktadır.
  - Keep-alive bağlantılarda soket kilitlenmesi tamamen ortadan kalktı.
- **Nova Entegrasyonu:** Nova v0.5.0 `tests/integration/methods_integration_test.nox` içerisinde canlı `HEAD 200` isteği ile doğrulandı.

---

## 9. `spawn` İfadesinin Metot ve Modüller Arası Çağrı Desteği
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.1.5 — `checker.zig:2912`)**
- **Uygulama:**
  - `spawn obj.method(...)` yazıldığında derleyici nesne ve metot için otomatik `__spawn_<Class>_<method>` thunk fonksiyonu sentezler.
  - Paketlenebilir tipler (`int`, `float`, `bool`, `str`, `None`, `Task[T]`, `Channel[T]`) güvenle iş parçacığı havuzuna aktarılır.
  - İçe aktarılan (`import`) `async def` fonksiyonları da `spawn` tarafından tanınmaktadır.
- **Nova Entegrasyonu:** Nova v0.4.0 ve v0.5.0 testlerinde eşzamanlı istekler doğrudan `spawn` ile test edilmektedir.

---

## 10. Düşük Seviye Soket Akışı (Native Low-Level Chunked Streaming)
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.69)**
- **Uygulama:**
  - `nox.http.stream(method, url, headers, body, timeout_ms) -> HttpStream` ve `HttpStream.read_chunk(n)` eklendi.
  - Soketten parça parça okuma, sınırlandırılmış bellek kullanımı ve soket kapatma (`close()`) sağlandı.
- **Nova Entegrasyonu:** Nova v0.5.0 ile `StreamResponse` sınıfına `HttpStream` entegrasyonu, `with client.stream(...) as s:` context manager (`__enter__`/`__exit__`) ve sıfır-tamponlama akışı eklendi.

---

## 11. HTTP Bağlantı Havuzu (Connection Pooling & Keep-Alive Reuse)
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.126 & v2.0.128)**
- **Uygulama:**
  - `nox.http.client_pool(max_idle: int, idle_timeout_ms: int)` ve `nox.http.client_idle_connections() -> int` standart kütüphaneye eklendi.
  - Çoklu isteklerde TCP/TLS el sıkışması maliyeti önlenerek açık bağlantılar güvenle yeniden kullanılmaktadır.
- **Nova Entegrasyonu:** Nova v0.5.0 ile `client.set_connection_pool(max_idle, idle_timeout_ms)` ve `client.get_idle_connections()` metotları eklendi.

---

## 12. Kurumsal Proxy Desteği (HTTP / HTTPS / NO_PROXY)
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.129)**
- **Uygulama:**
  - Standart HTTP istemcisi ortam değişkenlerini (`HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`) otomatik olarak değerlendirir.
  - HTTPS istekleri için güvenli `CONNECT host:443` tünellemesi kullanılır.
- **Nova Entegrasyonu:** Nova v0.5.0, altta yatan güvenli proxy tünellemesini doğrudan şeffaf bir şekilde kullanmaktadır.

---

## 13. Derleyici Limitasyonu: FFI Fonksiyon Parametresinde Geçici Heap İfadesi
- **Durum:** ⚠️ **AÇIK DERLEYİCİ LİMİTASYONU / WORKAROUND BELGELENDİ**
- **Konum:** `noxc` ARC Analizcisi / LLVM Codegen
- **Detay:**
  - Bir nesne metot çağrısından dönen heap nesnesi (örneğin `req_headers.to_dict()`) doğrudan bir C/Zig stdlib FFI fonksiyonunun argüman listesi içinde çağrıldığında:
    `download_to_file(url, path, req_headers.to_dict(), timeout)`
    derleyici kod üretimi sırasında SIGSEGV (139) verebilmektedir.
- **Çözüm (Nova'da uygulanan):**
  - İfadeyi bir yerel değişkene atamak sorunu tamamen ortadan kaldırır:
    ```nox
    h: dict[str, str] = req_headers.to_dict()
    return download_to_file(url, path, h, timeout)
    ```

---

## 14. DNS Çözümleme API'si ve Doğrulanmış IP'ye Bağlanma (SSRF / DNS Rebinding)
- **Durum:** ⚠️ **AÇIK — Nox çalışma zamanı özelliği gerekli (P0 güvenlik)**
- **Detay:** Nox stdlib'de bir DNS çözümleme fonksiyonu (`nox.net.resolve` benzeri) yoktur ve `nox.http` bağlanırken hostname'i kendisi tekrar çözer. Bu yüzden Nova, çözümlenmiş IP'yi doğrulasa bile bağlantı **o IP'ye** yapılmaz → DNS rebinding (TOCTOU) penceresi açık kalır.
- **Önerilen Nox değişikliği:**
  1. `nox.net.resolve(host: str) -> list[str]` (A/AAAA).
  2. `nox.http` isteklerine `connect_ip: str` (veya bir `pre_connect` doğrulama kancası): doğrulanmış IP'ye bağlan, TLS SNI + sertifika/hostname doğrulamasını **orijinal hostname** üzerinden yap.
  3. Ortak `nox.net.ip` (IPv4/IPv6 ayrıştırma + sınıflandırma): Nova'nın `ssrf.nox` parser'ı bunun için referans olabilir; Cipher / Sentinel gibi kütüphaneler tekrar yazmak zorunda kalmaz.
- **Nova'daki karşılığı (v0.6.0):** `HostResolver` arayüzü + `SSRFPolicy.set_resolver()` (tüm IP'ler doğrulanır, fail-closed) ve `set_strict_hostnames(True)` (en güçlü mevcut mod).

---

## 15. Tembel (Lazy) İteratör / Generator Desteği
- **Durum:** ⚠️ **AÇIK — dil özelliği**
- **Detay:** Nox'ta `for x in obj.iter_lines():` ile tüketilebilen tembel iteratör/generator protokolü yoktur; metotlar `list[...]` döndürmek zorundadır (tüm veri belleğe alınır).
- **Önerilen Nox değişikliği:** `__iter__`/`__next__` protokolü veya `yield`.
- **Nova'daki karşılığı (v0.6.0):** `StreamResponse.read_line()` (pull) ve callback sınıfları `LineHandler` / `ChunkHandler` ile `for_each_line` / `for_each_chunk` (sınırlı bellek).

---

## 16. Yinelenen Yanıt Başlıkları (Birden Çok `Set-Cookie`)
- **Durum:** ⚠️ **AÇIK — runtime hatası/eksiği**
- **Detay:** Canlı doğrulandı: `httpbin.org/cookies/set?a=1&b=2` iki `Set-Cookie` döndürür, ancak `nox.http` istemcisinin `HttpResponse.headers: dict[str, str]` alanında yalnızca **sonuncusu** (`b=2`) kalır; `a=1` kaybolur. (Sunucu tarafı için `nox.http.multi` `\n` ile birleştirir; istemci tarafı simetrik değildir.)
- **Önerilen Nox değişikliği:** İstemci yanıtında yinelenen başlıkları `nox.http.multi` ile aynı `\n` kuralıyla birleştirmek (veya `HttpResponse.header_list: list[tuple[str,str]]`).
- **Nova'daki karşılığı (v0.6.0):** `Headers.set_multi/get_all`, `response_headers_from_dict` ve `CookieJar` çoklu `Set-Cookie` değerlerini `\n` ile destekler; runtime düzelince ek değişiklik gerekmez.

---

## 17. Client'a Özel (Per-Client) Bağlantı Havuzu
- **Durum:** ⚠️ **AÇIK — runtime tasarımı**
- **Detay:** `nox.http.client_pool(max_idle, idle_timeout_ms)` **süreç geneli**dir. Bir `Client` üzerindeki `set_connection_pool()` bütün süreci etkiler (bağlantılar origin başına ayrı tutulur).
- **Önerilen Nox değişikliği:** `nox.http.Pool` nesnesi (`pool.request(...)` / `request(..., pool=p)`).
- **Nova'daki karşılığı (v0.6.0):** API dokümantasyonunda kapsam açıkça "process"; `Client.connection_pool_scope()`.

---

## 18. Modül Düzeyinde Değiştirilebilir Durum ve `while True` Dönüş Analizi
- **Durum:** ℹ️ **BİLGİ**
- `global` ile modül değişkeni atanamadığından (Public Suffix listesi gibi) çalışma-zamanı genişletmeleri nesne alanlarında tutulur (`CookieJar.add_public_suffix`).
- `while True:` içinde `return` olsa bile fonksiyon sonuna `return` gerekir (`MissingReturn`).

---

## 📊 Çözüm Matrisi Özeti

| Kısıtlama / Özellik | İlgili Nox Sürümü | Durum | Nova'daki Karşılığı |
|---|---|---|---|
| PUT, PATCH, DELETE, HEAD, OPTIONS | `v2.0.31` | ✅ ÇÖZÜLDÜ | `client.put()`, `patch()`, `delete()`, `head()` |
| Gerçek İstek Zaman Aşımı | `v2.0.31` | ✅ ÇÖZÜLDÜ | `Client(timeout_ms=...)` & `TimeoutError` |
| İkili Gövde (`nox.bytes`) | `v2.0.31` | ✅ ÇÖZÜLDÜ | `response.bytes() -> Buffer` |
| IPv6 URL Çözümleme | `v2.0.30` | ✅ ÇÖZÜLDÜ | Yerel `nox.url.parse` tam uyumu |
| `and` Optional Daraltma | `v2.0.30` | ✅ ÇÖZÜLDÜ | Akıcı tip kontrolleri |
| String `\xHH` Kaçışları | `v2.0.30` | ✅ ÇÖZÜLDÜ | İkili testler ve protokol filtreleri |
| HEAD Keep-Alive Kilitlenmesi | `v2.1.2` | ✅ ÇÖZÜLDÜ | Canlı `HEAD 200` doğrulaması |
| `spawn` Metot Desteği | `v2.1.5` | ✅ ÇÖZÜLDÜ | `spawn obj.method(...)` & `Task[T]` |
| Yerel Soket Akışı (Streaming) | `v2.0.69` | ✅ ÇÖZÜLDÜ | `StreamResponse` + `with client.stream()` |
| Bağlantı Havuzu (Connection Pool) | `v2.0.126` | ✅ ÇÖZÜLDÜ | `client.set_connection_pool()` |
| Proxy Tünelleme | `v2.0.129` | ✅ ÇÖZÜLDÜ | `HTTP_PROXY`, `HTTPS_PROXY` şeffaf tünelleme |
| Büyük Dosya Transferi | `v2.0.69` | ✅ ÇÖZÜLDÜ | `nova.transfer` (`download_file`/`upload_file`) |
| FFI Argümanında Heap Geçicisi | — | ⚠️ AÇIK (Workaround var) | Yerel değişkene atama kuralı |
| DNS çözümleme + IP'ye bağlanma | — | ⚠️ AÇIK (P0) | `HostResolver`, `strict_hostnames` |
| Tembel iteratör | — | ⚠️ AÇIK | `read_line`, `for_each_line` |
| Yinelenen yanıt başlıkları | — | ⚠️ AÇIK | `Headers.set_multi`, `\n` kuralı |
| Client'a özel havuz | — | ⚠️ AÇIK | Kapsam belgelendi (`process`) |
