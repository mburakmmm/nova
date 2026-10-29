# NOX_LIMITATIONS.md — Nox Dili ve Standart Kütüphanesi Limitasyon & Çözüm Kaydı

Bu belge, **Nova HTTP Client** geliştirme sürecinde tespit edilen ve Nox çalışma zamanı (`runtime/stdlib_shims/http_client.zig`), standart kütüphanesi (`stdlib/nox/http.nox`, `stdlib/nox/bytes.nox`, `stdlib/nox/url.nox`) ve derleyicisi (`noxc`) seviyesinde çözülen/kalan mimari başlıkları listeler.

---

## 1. Genel HTTP Metod Desteği (PUT, PATCH, DELETE, HEAD, OPTIONS)
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.31 — Commit `491f1e08`)**
- **Uygulama:**
  - Zig çalışma zamanında `nox_http_request_raw(method, url, body, has_body, headers, timeout_ms)` dışa aktarıldı.
  - `stdlib/nox/http.nox` modülüne `request()`, `put()`, `patch()`, `delete()`, `head()`, `options()` fonksiyonları eklendi.
  - Desteklenmeyen veya geçersiz metodlar açıkça `HttpError` fırlatmaktadır.
- **Nova v0.3.0 Entegrasyonu:** `TransportAdapter.execute()` içinde tüm metodlar doğrudan bağlanacak; `UnsupportedFeatureError` kısıtlaması kaldırılacaktır.

---

## 2. Gerçek İstek ve Soket Zaman Aşımı (True Request Timeout)
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.31 — Commit `491f1e08`)**
- **Uygulama:**
  - `nox_http_request_raw` çağrısına `timeout_ms: int` parametresi eklendi.
  - Süre dolduğunda işletim sistemi soketi seviyesinde bağlantı iptal edilmekte ve `HttpTimeoutError` (`HttpError` alt sınıfı) fırlatılmaktadır.
  - Arka planda başıboş (dangling) iş parçacığı veya I/O bırakılmaz (`AGENTS.md §12` tam uyumlu).
- **Nova v0.3.0 Entegrasyonu:** `Client(timeout_ms=...)` ve istek seviyesi `timeout_ms` desteği Nova `TimeoutError` ile eşleştirilecektir.

---

## 3. İkili / Bayt Tabanlı Gövde Desteği (Binary Body & Buffer)
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.31 — Commit `491f1e08`)**
- **Uygulama:**
  - `HttpResponse.body: str` artık gömülü `\x00` (NUL) ve geçersiz UTF-8 baytlarını uzunluk bilgisiyle bellekte aynen korumaktadır.
  - `stdlib/nox/bytes.nox` modülü ve `nox.bytes.from_str(s: str) -> Buffer` fonksiyonu eklendi.
- **Nova v0.3.0 Entegrasyonu:** `Response.bytes() -> Buffer` metodu eklenerek ikili içerikler doğrudan `Buffer` olarak okunabilecektir.

---

## 4. Büyük Dosyalar İçin Akış (Streaming Download & Upload)
- **Durum:** ⏳ **PLANLANDI (Phase 4 — Gelecek Aşama)**
- **Açıklama:** Yanıtlar şu an tek parça halinde belleğe alınmaktadır. Gigabayt ölçeğinde streaming desteği ilerleyen sürümlerde chunked okuyucu API'si ile değerlendirilecektir.

---

## 5. Yönlendirme (Redirect) Politikası Kontrolü
- **Durum:** ✅ **ÇÖZÜLDÜ (Nova v0.2.1 / v0.2.2)**
- **Açıklama:** Nox çalışma zamanı `redirect_behavior = .unhandled` ayarladığı için 3xx yanıtları istemciye doğrudan döner. Nova katmanında döngü tespiti (`max_redirects = 5`) ve çapraz-orijin `Authorization` temizliği istemci seviyesinde tam kontrolle çözülmüştür.

---

## 6. Derleyici & Tip Sistemi İyileştirmeleri
- **A. `and` / `or` ile Flow-Sensitive Optional Daraltması:**
  - **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.30 — Commit `29a0b7af`)**
  - `if x is not None and x.foo():` sözdizimi artık derleyicide geçerlidir.
- **B. `int()` ve `float()` Fonksiyonlarında Boşluk Toleransı:**
  - **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.30 — Commit `29a0b7af`)**
  - `int("  42  ")` baştaki ve sondaki boşlukları otomatik temizlemektedir.
- **C. String Literallerinde Onaltılık Kaçış Dizisi (`\xHH`):**
  - **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.30 — Commit `29a0b7af`)**
  - `"\x00"` ve `"\x01"` gibi onaltılık kaçışlar string literallerinde desteklenmektedir.
- **D. Fonksiyon Parametrelerinde Sabit Varsayılan Değer:**
  - Bellek güvenliği kuralı olarak korunmaktadır (`headers: dict[str, str] | None = None`).

---

## 7. `nox.url` Standart Kütüphanesinde IPv6 Literal Desteği
- **Durum:** ✅ **ÇÖZÜLDÜ (Nox v2.0.30 — Commit `29a0b7af`)**
- **Açıklama:** `[::1]:8080` gibi IPv6 literal adresler `stdlib/nox/url.nox` içinde köşeli parantez korumasıyla hatasız ayrıştırılmaktadır.

---

## 📊 Çözüm Matrisi Özeti

| Kısıtlama | İlgili Nox Sürümü | Durum | Nova'daki Karşılığı |
|---|---|---|---|
| PUT, PATCH, DELETE, HEAD, OPTIONS | `v2.0.31` | ✅ ÇÖZÜLDÜ | `client.put()`, `patch()`, `delete()`, `head()` |
| Gerçek İstek Zaman Aşımı | `v2.0.31` | ✅ ÇÖZÜLDÜ | `Client(timeout_ms=...)` & `TimeoutError` |
| İkili Gövde (`nox.bytes`) | `v2.0.31` | ✅ ÇÖZÜLDÜ | `response.bytes() -> Buffer` |
| IPv6 URL Çözümleme | `v2.0.30` | ✅ ÇÖZÜLDÜ | Yerel `nox.url.parse` tam uyumu |
| `and` Optional Daraltma | `v2.0.30` | ✅ ÇÖZÜLDÜ | Akıcı tip kontrolleri |
| String `\xHH` Kaçışları | `v2.0.30` | ✅ ÇÖZÜLDÜ | İkili testler ve protokol filtreleri |
| Akışlı Okuma (Streaming) | — | ⏳ PLANLANDI | Phase 4 |
