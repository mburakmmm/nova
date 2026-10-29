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

## 8. HEAD İsteklerinde Keep-Alive Gövde Okuma Kilitlenmesi (RFC 7230 §3.3.3)
- **Durum:** ⚠️ **AÇIK / ÖNERİLEN DÜZELTME**
- **Konum:** `runtime/stdlib_shims/http_client.zig` (satır ~514)
- **Detay:**
  - Sunucular `HEAD` yanıtlarında kaynağın boyutunu `Content-Length: <n>` olarak bildirir ancak gövde göndermez (0 bayt).
  - Zig çalışma zamanındaki `reader.streamRemaining` fonksiyonu `Content-Length` kadar bayt okumaya çalışır. Keep-alive bağlantılarda soket kapanmadığı için çalışma zamanı hiç gelmeyecek baytları bekleyerek kilitlenir (hang).
- **Önerilen Çözüm:** `http_client.zig` içinde istek metodu `HEAD` ise (`ctx.method == .HEAD`) gövde okuma adımı doğrudan atlanmalı ve boş string (`""`) dönmelidir.

---

## 9. `spawn` İfadesinin Metot ve Modüller Arası Çağrı Kısıtlamaları
- **Durum:** ⚠️ **AÇIK DERLEYİCİ LİMİTASYONU**
- **Konum:** `compiler/typecheck/checker.zig` (satır ~6639-6646)
- **Detay:**
  1. **Metot Çağrısı:** `spawn client.get(...)` yazıldığında derleyici `callee` tipinin doğrudan tanımlayıcı (`identifier`) olmasını şart koştuğu için reddeder:
     `type error (NotCallable): 'spawn' can only wrap a direct function call (method/constructor calls are not supported yet)`
  2. **Modüller Arası İçe Aktarma (`import`):** Başka bir modülden `from module import async_fn` yapıldığında veya `spawn module.async_fn()` çağrıldığında, `checker.zig:6643` içindeki `self.async_functions.contains(fn_name)` kontrolü başarısız olur çünkü `self.async_functions` sadece o an derlenen dosya içindeki yerel fonksiyonları kaydeder:
     `type error (TypeMismatch): 'spawn' can only start 'async def' functions: 'async_fn' is not async`
- **Önerilen Çözüm:**
  - `checker.zig` içinde `self.async_functions` kontrolünün içe aktarılan fonksiyonların `is_async` meta-bilgisini de sorgulayacak şekilde genişletilmesi.
  - `spawn` ifadesinin metot çağrılarını (`.member_access`) desteklemesi veya bir closure oluşturması.
- **Geçici Çözüm (Nova Kullanıcıları İçin):** Kullanıcı kendi dosyasında yerel bir `async def run_fetch(): return nova.get(...)` fonksiyonu tanımlayıp `spawn run_fetch()` olarak çağırabilmektedir. Bu yöntemle eşzamanlı istekler Nox'un iş parçacığı havuzunda başarıyla koşmaktadır.

---

## 10. Düşük Seviye Soket Akışı (True Chunked Streaming Transport)
- **Durum:** ⏳ **ÖNERİLEN GELİŞTİRME**
- **Detay:**
  - Mevcut `nox_http_request_raw` tüm gövdeyi tek seferde `str` olarak bellek tamponuna alır.
  - Gigabaytlarca büyük dosyalar için soketten parça parça (`Buffer` veya chunked reader) okuma sağlayan bir `nox_http_stream_raw` C-ABI köprüsü eklendiğinde Nova'nın `StreamResponse` katmanı doğrudan sıfır-tamponlama ile çalışabilecektir.

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
| HEAD Keep-Alive Kilitlenmesi | — | ⚠️ AÇIK | `http_client.zig` içinde HEAD gövde atlama |
| `spawn` Metot Desteği | — | ⚠️ BİLGİ | Bağımsız sarmalayıcı fonksiyonlar |
| Soket Düzeyi Akış (Streaming) | — | ⏳ ÖNERİLDİ | `StreamResponse` (Nova içi simüle chunking) |
