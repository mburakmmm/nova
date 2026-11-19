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
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.1.195 + v2.2.4 / Nova v0.8.0)** *(tamponlu HTTP/HTTPS istekleri için; akışlı `stream()`/`stream_upload()` hâlâ açık)*
- **Uygulama (`v2.1.195+`):**
  - `nox.dns.resolve(host, timeout_ms, doh_url)` ve `nox.ip` (`is_valid`, `parse`) standart kütüphaneye eklendi (WASM'da açık `doh_url` desteğiyle).
  - `nox.http.request(..., connect_ip=..., ca_file=...)` bağlanma hedefini doğrulanmış IP'ye sabitlerken TLS SNI ve sertifika/hostname doğrulamasını **orijinal ana makine adı** üzerinden yapar.
- **Nova Entegrasyonu (v0.8.0):**
  - `NoxDnsResolver(timeout_ms, doh_url)` (`nox.dns.resolve` tabanlı `HostResolver`).
  - `SSRFPolicy.set_pin_resolved_ip(True)` ve `SSRFPolicy.validate_and_pin()`: hem ilk istek hem de her yönlendirme (redirect) adımında IP kanonikleştirme + doğrulama + `Request.connect_ip` sabitlemesi.
  - `create_safe_client()` / `nova.safe_client()` varsayılan olarak `NoxDnsResolver` + `pin_resolved_ip=True` + `allow_https_downgrade=False` ile başlar.
  - **Açık kalan sınır:** `nox.http.stream()` ve `nox.http.stream_upload()` `connect_ip` almadığından Nova bu iki çağrıda `pin_resolved_ip` etkinken sessizce düşmek yerine açıkça `UnsupportedFeatureError("connect_ip", ...)` fırlatır.

---

## 15. Tembel (Lazy) İteratör / Generator Desteği
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.2.x `Iterator[T]` + `yield` / Nova v0.8.0)**
- **Uygulama:** Derleyici `def ... -> Iterator[str]: ... yield ...` generator fonksiyonlarını/metotlarını Masaüstü ve `wasm32-*` hedeflerinde tam desteklemektedir.
- **Nova Entegrasyonu (v0.8.0):** `StreamResponse.lines() -> Iterator[str]` ve `StreamResponse.chunks(chunk_size=4096) -> Iterator[str]` eklendi; böylece `for line in stream.lines():` doğrudan tembel ve sınırlı bellekli tüketim sunar (`read_line` / `LineHandler` / `ChunkHandler` geriye dönük uyumlu korunur).

---

## 16. Yinelenen Yanıt Başlıkları (Birden Çok `Set-Cookie`)
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.1.195 / Nova v0.8.0)**
- **Uygulama:** `nox.http` istemcisi yinelenen yanıt başlıklarını (`Set-Cookie` dahil) sunucudaki `nox.http.multi` ile simetrik biçimde `\n` ayırıcısıyla birleştirerek `HttpResponse.headers` içinde döndürür.
- **Nova Entegrasyonu (v0.8.0):** `Headers.get_all()`, `response_headers_from_dict()` ve `CookieJar.extract_from_response()` uçtan uca yerel sunucu testiyle (`tests/integration/multi_set_cookie_test.nox`) doğrulandı.

---

## 17. Client'a Özel (Per-Client) Bağlantı Havuzu
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.2.1 `nox.http.Pool` / Nova v0.8.0)**
- **Uygulama:** `nox.http.new_pool(max_idle, idle_timeout_ms)` ile `Pool.request()`, `Pool.idle_connections()`, `Pool.close()` standart kütüphaneye eklendi (`connect_ip`/`ca_file` verilen istekler güvenlik gereği havuzu atlar).
- **Nova Entegrasyonu (v0.8.0):** `Client.enable_private_pool(max_idle, idle_timeout_ms)` (`connection_pool_scope() == "client"`), `Client.close()`, ve `with Client(...) as cli:` context manager yaşam döngüsü (`tests/integration/private_pool_test.nox`) eklendi. `set_connection_pool()` geriye dönük uyumluluk için `"process"` kapsamını korur.

---

## 18. Modül Düzeyinde Değiştirilebilir Durum ve `while True` Dönüş Analizi
- **Durum:** ℹ️ **BİLGİ**
- `global` ile modül değişkeni atanamadığından çalışma-zamanı genişletmeleri nesne alanlarında tutulur (`CookieJar.add_public_suffix`).
- `while True:` içinde `return` olsa bile fonksiyon sonuna `return` gerekir (`MissingReturn`).

---

## 19. Nox Karakter Sayısı (`len`) ve Bayt Uzunluğu (`nox.strings.byte_len`) Semantiği
- **Durum:** ℹ️ **BİLGİ / KÜTÜPHANE UYUMU (Nova v0.6.2)**
- **Detay:** Nox dilinde yerleşik `len(s: str)` fonksiyonu Unicode kod noktası (karakter sayısı) döndürmektedir (`len("ğ") == 1`, `len("😀") == 1`). Ancak ağ ve akış protokollerinde (HTTP satır sınırları, `max_line_bytes`, Content-Length) ham bayt sayısı (`byte_len`) esastır (`byte_len("ğ") == 2`, `byte_len("😀") == 4`).
- **Nova'daki karşılığı (v0.6.2):** `StreamResponse.read_line()` içinde bellek sınırları `len(s)` yerine doğrudan `nox.strings.byte_len(s)` ile ölçülür; böylece çok baytlı UTF-8 karakterlerinde `max_line_bytes` güvencesi tam olarak sağlanır.

---

## 20. C-Tabanlı `noxclibs.a` Modülleri ve WASM / Mobil Hedef Sınırı (`nox.brotli`, `nox.yyjson`)
- **Durum:** ✅ **KORUMALI MİMARİ İLE AYRILDI (Nox v2.1.173–2.1.186 / Nova v0.7.0)**
- **Detay:** Nox `v2.1.173+` masaüstü hedeflerde (macOS/Linux/Windows) `nox.brotli` ve `nox.yyjson` modüllerini `noxclibs.a` ile sunar; ancak derleyici `ios-*`/`android-*` hedeflerinde bu modüllerin `import` edilmesini tip kontrolünde reddeder ve `wasm32-*` hedeflerinde bağlama hatası verir. Ayrıca `http_client.zig` yanıtları yalnızca `gzip`/`deflate` olarak otomatik açar (`br` desteklemez).
- **Nova'daki karşılığı (v0.7.0):** Çekirdek `nova.nox` ve `Client`, saf Nox (`nox.json` / `FallbackContentDecoder` / `NoxJsonReader`) ile %100 WASM + mobil uyumlu kalır. Brotli (`brotli_codec.nox`) ve yyjson (`yyjson_adapter.nox`) yalnızca masaüstü uygulamaların isteğe bağlı import edebileceği eklenti modülleri olarak ayrılmıştır.

---

## 21. Akışlı Yükleme (`stream_upload`) ve HTTP/3 (`set_http3`) Desteği
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.1.116 & v2.0.152 / Nova v0.7.0)** / ⚠️ **Gerçek QUIC Doğrulama Notu (§22)**
- **Detay:** `nox.http.stream_upload()` chunked ve sabit boyutlu artımlı yükleme sağlar; `nox.http.set_http3(true)` ise `Alt-Svc: h3` keşfiyle süreç-geneli HTTP/3 desteği açar (UDP/OpenSSL 3.5 yoksa şeffaf TCP geri dönüşü).
- **Nova'daki karşılığı (v0.7.0 / v0.7.1):** `Client.stream_upload()`, `UploadStream` (CookieJar/ContentDecoder senkronizasyonu ve deterministik cleanup ile), `Client.set_http3()` ve `nova.set_http3()` entegre edildi.

---

## 22. İstemci Tarafında Özel CA / Sertifika Güvenliği ve Yerel HTTP/3 QUIC Sınırı
- **Durum:** ✅ **TCP TLS (`ca_file`) ÇÖZÜLDÜ (Nox v2.1.195 / Nova v0.8.0)** / ⚠️ **HTTP/3 QUIC özel CA desteği bekliyor**
- **Uygulama:** `nox.http.request(..., ca_file=...)` sistem deposu yerine belirtilen PEM CA dosyasına sıkı sertifika + hostname doğrulaması yapar (`verify=False` asla sunulmaz). Nova `Client.set_ca_file(path)` ile yerel `serve_tls` sunucusuna karşı doğrulamalı HTTPS GET/POST ve `connect_ip` SNI sabitlemesi `tests/integration/tls_custom_ca_connect_ip_test.nox` içinde doğrulanmıştır.
- **Kalan sınır:** `nox.http` HTTP/3 QUIC yolu (`ca_file.len == 0` koşulu) ve `stream()`/`stream_upload()` henüz `ca_file` parametresi almadığından özel CA ile HTTP/3 QUIC loopback el sıkışması ve akışlı özel-CA istekleri gelecek çalışma zamanı genişlemesine bırakılmıştır (`UnsupportedFeatureError` ile açıkça reddedilir).

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
| Akışlı Yükleme (`stream_upload`) | `v2.0.152` | ✅ ÇÖZÜLDÜ | `UploadStream` + `client.stream_upload()` |
| HTTP/3 (`Alt-Svc` + TCP fallback) | `v2.1.116` | ✅ ÇÖZÜLDÜ | `client.set_http3()` / `nova.set_http3()` |
| Bağlantı Havuzu (Process Pool) | `v2.0.126` | ✅ ÇÖZÜLDÜ | `client.set_connection_pool()` |
| Client'a Özel Havuz (`nox.http.Pool`) | `v2.2.1` | ✅ ÇÖZÜLDÜ | `client.enable_private_pool()`, `with Client()` |
| Proxy Tünelleme | `v2.0.129` | ✅ ÇÖZÜLDÜ | `HTTP_PROXY`, `HTTPS_PROXY` şeffaf tünelleme |
| Büyük Dosya Transferi | `v2.0.69` | ✅ ÇÖZÜLDÜ | `nova.transfer` (`download_file`/`upload_file`) |
| `noxclibs` (Brotli / yyjson) WASM+Mobil Sınırı | `v2.1.175` | ✅ KORUMALI | Çekirdek saf Nox fallback + masaüstü opt-in modülleri |
| FFI Argümanında Heap Geçicisi | — | ⚠️ AÇIK (Workaround var) | Yerel değişkene atama kuralı |
| DNS çözümleme + IP (`connect_ip` + `nox.dns`) | `v2.1.195` | ✅ ÇÖZÜLDÜ (tamponlu) | `NoxDnsResolver`, `pin_resolved_ip`, `connect_ip` (`stream` hariç) |
| Tembel iteratör (`Iterator[str]`) | `v2.2.x` | ✅ ÇÖZÜLDÜ | `StreamResponse.lines()` / `chunks()` (`yield`) |
| Yinelenen yanıt başlıkları | `v2.1.195` | ✅ ÇÖZÜLDÜ | `\n` birleşimli çoklu `Set-Cookie` canlı/yerel doğrulandı |
| Özel PEM CA (`ca_file`) | `v2.1.195` | ✅ ÇÖZÜLDÜ (TCP TLS) | `Client.set_ca_file()` (akışlı ve QUIC HTTP/3 hariç) |
