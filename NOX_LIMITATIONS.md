# NOX_LIMITATIONS.md — Nox Dili ve Standart Kütüphanesi İçin Gereksinimler & Yol Haritası

Bu belge, **Nova HTTP Client** geliştirme sürecinde tespit edilen, Nox çalışma zamanı (`runtime/stdlib_shims/http_client.zig`), standart kütüphanesi (`stdlib/nox/http.nox`) ve derleyicisi (`noxc`) tarafında yapılması önerilen mimari geliştirmeleri ve değişiklik noktalarını listeler.

---

## 1. Genel HTTP Metod Desteği (PUT, PATCH, DELETE, HEAD, OPTIONS)

### Mevcut Durum & Problem:
* **Dosya:** `runtime/stdlib_shims/http_client.zig` (satır ~483 ve ~560)
* Zig tarafındaki `doRequest(rt, method: std.http.Method, url, body, headers_dict)` fonksiyonu dahili olarak Zig'in tüm HTTP metodlarını (`.GET`, `.POST`, `.PUT`, `.PATCH`, `.DELETE`, `.HEAD`, `.OPTIONS` vb.) çalıştırabilecek yapıdadır.
* Ancak `noxrt.o` çalışma zamanı dosyasından yalnızca iki fonksiyon export edilmiştir:
  ```zig
  export fn nox_http_get_raw(rt: ?*anyopaque, url: ?[*:0]const u8, headers: ?*anyopaque) callconv(.c) ?*anyopaque {
      return doRequest(rt, .GET, url, null, headers);
  }
  export fn nox_http_post_raw(rt: ?*anyopaque, url: ?[*:0]const u8, body: ?[*:0]const u8, headers: ?*anyopaque) callconv(.c) ?*anyopaque {
      return doRequest(rt, .POST, url, body, headers);
  }
  ```
* **Etki:** Nova'da `PUT`, `PATCH`, `DELETE` gibi temel REST API metodları şu an `UnsupportedFeatureError` fırlatmak zorundadır (`AGENTS.md` gereğince GET/POST ile taklit edilmesi yasaktır).

### Önerilen Çözüm:
1. `runtime/stdlib_shims/http_client.zig` dosyasına genel bir istek fonksiyonu eklenmesi:
   ```zig
   export fn nox_http_request_raw(
       rt: ?*anyopaque,
       method_str: ?[*:0]const u8,
       url: ?[*:0]const u8,
       body: ?[*:0]const u8,
       headers: ?*anyopaque,
   ) callconv(.c) ?*anyopaque {
       const m_slice = if (method_str) |m| str_mod.nox_str_slice(m) else "GET";
       const method: std.http.Method = if (std.mem.eql(u8, m_slice, "POST"))
           .POST
       else if (std.mem.eql(u8, m_slice, "PUT"))
           .PUT
       else if (std.mem.eql(u8, m_slice, "PATCH"))
           .PATCH
       else if (std.mem.eql(u8, m_slice, "DELETE"))
           .DELETE
       else if (std.mem.eql(u8, m_slice, "HEAD"))
           .HEAD
       else if (std.mem.eql(u8, m_slice, "OPTIONS"))
           .OPTIONS
       else
           .GET;

       return doRequest(rt, method, url, body, headers);
   }
   ```
2. `stdlib/nox/http.nox` modülüne bağlanması:
   ```nox
   extern def nox_http_request_raw(method: str, url: str, body: str, headers: dict[str, str]) -> ptr from "zig-out/lib/noxrt.o" with_rt

   def request(method: str, url: str, body: str, headers: dict[str, str]) -> HttpResponse:
       h: ptr = nox_http_request_raw(method, url, body, headers)
       if nox_http_response_ok(h) == 0:
           nox_http_response_free(h)
           raise HttpError("request failed: " + url)
       status: int = nox_http_response_status(h)
       resp_body: str = nox_http_response_body(h)
       resp: HttpResponse = HttpResponse(status, resp_body, nox_http_response_headers(h))
       nox_http_response_free(h)
       return resp
   ```

---

## 2. Gerçek İstek ve Soket Zaman Aşımı (True Request Timeout)

### Mevcut Durum & Problem:
* **Dosya:** `runtime/stdlib_shims/http_client.zig` (`RequestCtx` yapısı)
* Şu anda `RequestCtx` yapısında `timeout_ms` alanı bulunmamaktadır. İstek arka plan OS iş parçacığında bloklayan `std.http.Client` ile çalışır.
* Sunucu bağlantıyı kapatmaz veya paket düşürürse, istek süresiz olarak askıda (hang) kalabilir.
* `AGENTS.md §12` uyarınca: İstek döndükten sonra geçen süreyi kontrol eden "post-hoc fake timeout" çözümü kesinlikle yasaklanmıştır.

### Önerilen Çözüm:
1. `RequestCtx` içine `timeout_ms: i64 = 0` alanı eklenmesi.
2. Zig `std.http.Client` istek başlatılırken soket seviyesinde `SO_RCVTIMEO` / `SO_SNDTIMEO` ayarlanması veya `std.posix.poll` ile self-pipe bekleyişine zaman aşımı eklenmesi.
3. Zaman aşımı durumunda `failed = true` ve hata kodunun `HttpTimeout` olarak işaretlenmesi.

---

## 3. İkili / Bayt Tabanlı Gövde Desteği (Binary Body & Buffer)

### Mevcut Durum & Problem:
* **Dosya:** `runtime/stdlib_shims/http_client.zig:581` (`nox_http_response_body`) ve `runtime/str.zig`
* `HttpResponse.body: str` alanı NUL-sonlandırmalı (null-terminated) bir C string'i (`[*:0]u8`) olarak tahsis edilmektedir.
* Gövde içerisinde `\0` baytı barındıran ikili (binary) yanıtlar (ör. resimler, PDF'ler, gzip sıkıştırmalı ham veriler, protobuf) `strlen()` tabanlı bellek yöneticisinde (`nox_str_free_now`) boyut uyuşmazlığına (`Invalid free`) veya gövdenin ilk `\0` baytında kesilmesine yol açmaktadır (bkz. `http_client.zig:29-35`).
* **Etki:** Nova şu anda yalnızca metin tabanlı (UTF-8) içerikleri garanti edebilir. Dosya indirme (download) veya ikili veri akışı yapılamaz.

### Önerilen Çözüm:
1. Yanıt gövdesini `str` yerine `nox.buffer.Buffer` veya ham bayt dizisi (`list[int]` / `ptr + len`) olarak dönebilen ikinci bir erişimci eklenmesi:
   ```zig
   export fn nox_http_response_body_bytes(rt: ?*anyopaque, h: ?*anyopaque) ?*anyopaque
   ```
2. `HttpResponse` sınıfına `body_bytes: Buffer` veya `bytes: list[int]` opsiyonunun kazandırılması.

---

## 4. Büyük Dosyalar İçin Akış (Streaming Download & Upload)

### Mevcut Durum & Problem:
* **Dosya:** `runtime/stdlib_shims/http_client.zig` (`workerThreadFn`)
* Yanıt okunurken tüm gövde `Response.readerDecompressing` ile tek seferde belleğe alınmaktadır (`std.ArrayList(u8)`).
* 500 MB veya birkaç GB büyüklüğündeki dosya transferlerinde tüm içerik RAM'e dolmakta ve bellek tükenmesine (OOM) yol açabilmektedir.

### Önerilen Çözüm:
* İsteğe bağlı bir chunked stream okuyucu API'si:
  `nox_http_stream_read(h: ptr, chunk_size: int) -> str`

---

## 5. Yönlendirme (Redirect) Politikası Kontrolü

### Mevcut Durum & Problem:
* `http_client.zig` dosyasında yönlendirmeler `redirect_behavior = .unhandled` olarak bırakılmıştır; ancak yüksek seviye `fetch` veya üst protokol kullanıldığında yönlendirmeler istemcinin kontrolü dışında gerçekleşebilmektedir.
* **Güvenlik Riski:** Bir istek `https://example.com`dan `https://hacker.com`a yönlendirildiğinde, `Authorization` veya `Cookie` başlıklarının çalışma zamanı seviyesinde otomatik temizlenmesi (strip) gerekmektedir (`AGENTS.md §11`).

### Önerilen Çözüm:
* İstemciye `max_redirects: int` (ör. varsayılan 5, 0 = yönlendirme kapalı) parametresi verilmesi.
* Yönlendirme hedefi farklı bir origin/host ise hassas başlıkların (`Authorization`, `Proxy-Authorization`) çalışma zamanında silinmesi.

---

## 6. Derleyici & Tip Sistemi Gözlemleri (Noxc / Checker)

Nova geliştirilirken Nox derleyicisinde (`noxc`) tespit edilen ve geliştiricilerin dikkat etmesi gereken kurallar:

### A. Bileşik Koşullarda Optional Daraltması (`and` ile Type Narrowing):
* **Gözlem:**
  ```nox
  # Derleme Hatası Verir (OptionalNotNarrowed):
  if pol is not None and pol.should_retry_status(...):
      ...
  ```
* **Neden:** `and` operatörünün sağ tarafındaki ifade değerlendirilirken, sol taraftaki `is not None` daraltması aynı satırda henüz aktifleşmemektedir.
* **Mevcut Çözüm:** İç içe `if` kullanmak:
  ```nox
  if pol is not None:
      if pol.should_retry_status(...):
          ...
  ```
* **Öneri:** Checker'ın `and` zincirinde sol taraftaki daraltmayı sağ tarafa akıtması (`flow-sensitive typing`).

### B. `int()` Fonksiyonunda Boşluk (Whitespace) Hassasiyeti:
* **Gözlem:** `int(" 5 ")` veya `int("5\n")` ifadesi `ValueError: int(): invalid number format` hatası fırlatmaktadır.
* **Mevcut Çözüm:** String'i önce `nox.strings.trim(s)` ile temizlemek gerekmektedir.
* **Öneri:** `int()` fonksiyonunun C `strtol` veya Python `int()` gibi baştaki ve sondaki ASCII boşluklarını (`\s`, `\t`, `\r`, `\n`) otomatik yok sayması kullanıcı deneyimini artıracaktır.

### C. Fonksiyon Parametrelerinde Sabit Varsayılan Değer Zorunluluğu:
* **Gözlem:** `def req(headers: dict[str, str] = {})` veya `def fn(items: list[str] = [])` derleme hatası vermektedir (`the default value can only be a constant literal`).
* **Neden:** Bellek güvenliği ve nesne referansı paylaşımını önlemek için bilinçli bir kuraldır.
* **Mevcut Çözüm:** `headers: dict[str, str] | None = None` kullanılıp fonksiyon gövdesinde `if headers is None: headers = {}` denilmektedir. Bu yapı güvenlidir ve korunmalıdır.

---

## 7. `nox.url` Standart Kütüphanesinde IPv6 Literal Hatası

### Mevcut Durum & Problem:
* **Dosya:** `stdlib/nox/url.nox` (satır ~110)
* URL parse edilirken `host_port` ayrımı ilk `:` karakterine göre yapılmaktadır (`split_once(":")` benzeri mantık).
* Örnek URL: `http://[::1]:8080/api`
* `host_port` alanı `[::1]:8080` olduğunda ilk `:` ilk IPv6 heksadesimal basamağında eşleşmekte, port olarak `:1]:8080` alınmakta ve `UrlError("invalid port")` fırlatılmaktadır.
* **Nova'daki Geçici Çözüm:** Nova `url.nox` içerisinde `[` ile başlayan IPv6 adreslerini `nox.url.parse`a girmeden önce ayırmakta ve köşeli parantezleri koruyarak URL oluşturmaktadır.

### Önerilen Çözüm:
* `stdlib/nox/url.nox` içinde port araması yapılırken, eğer host `[` ile başlıyorsa, eşleşen `]` karakterinden *sonraki* `:` aranmalıdır.

---

## Özet Yol Haritası Eşleşmesi

| Özellik | İlgili Dosya | Nova'da Açacağı Kapı |
|---|---|---|
| `nox_http_request_raw` | `runtime/stdlib_shims/http_client.zig` | PUT, PATCH, DELETE, HEAD metodları |
| `timeout_ms` parametresi | `runtime/stdlib_shims/http_client.zig` | Gerçek soket zaman aşımı koruması |
| `body_bytes` desteği | `runtime/stdlib_shims/http_client.zig` | İkili veri indirme, resim/dosya akışı |
| Akışlı okuma (Streaming) | `runtime/stdlib_shims/http_client.zig` | OOM olmadan büyük dosya indirme |
| IPv6 port ayrımı | `stdlib/nox/url.nox` | Yerel `nox.url.parse` ile doğrudan IPv6 desteği |
