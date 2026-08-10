---
type: Guide
title: "Dayanıklılık (Resilience) Müfredatı — Temelden İleri Seviyeye"
description: "Dağıtık sistemlerde dayanıklılık kalıplarını temelden ileri seviyeye kadar kapsayan Türkçe öğrenme programı."
timestamp: 2026-08-10T00:00:00Z
---

# Dayanıklılık (Resilience) Müfredatı

> **Taxonomy Reference**: §7.1 Reliability & Resilience  
> **Sözlük**: [Resilience](../../reference-dictionary/resilience.md)  
> **Kaynak Dosyalar**: [resilience-patterns.md](resilience-patterns.md), [circuit-breaker-honesty.md](circuit-breaker-honesty.md), [defensive-coding.md](defensive-coding.md), [distributed-resilience-patterns.md](distributed-resilience-patterns.md), [uber-load-shedding.md](uber-load-shedding.md), [famous-outages.md](famous-outages.md)

---

## Konu Listesi (Seviyelere Göre)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🟢 TEMEL (1-2 hafta)                                            │
│                                                                 │
│  §1  Idempotency ⭐           #1 öncelik: tekrarın güvenliği     │
│  §2  Neden Dayanıklılık?      Başarısızlık zihniyeti, hata tür. │
│  §3  Timeout                  Zaman aşımı hiyerarşisi, deadline │
│  §4  Retry                    Tekrar deneme, retry storm        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 🟡 ORTA (2-4 hafta)                                             │
│                                                                 │
│  §5  Exponential Backoff      Üstel geri çekilme, jitter        │
│  §6  Circuit Breaker          Devre kesici, half-open, slow-call│
│  §7  Bulkhead                 Kaynak izolasyonu, blast radius   │
│  §8  Fallback                 Yedek davranış, graceful degrad.  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 🔴 İLERİ (1-2 ay)                                              │
│                                                                 │
│  §9  Resilience Stack         Aspect order, katman kompozisyonu │
│  §10 Load Shedding            Yük atma: CoDel, PID, scorecard   │
│  §11 Backpressure             Geri basınç, bounded queue        │
│  §12 Chaos Engineering        Kaos mühendisliği, hata enjeksiy. │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ ⚫ UZMAN (sürekli pratik)                                       │
│                                                                 │
│  §13 Ünlü Kesintiler          5 büyük kesinti ve çıkarılan ders │
│  §14 Defensive Coding         Savunmacı programlama, assertion  │
│  §15 Tasarım Seviyesi         Blast radius, fail-safe, defense  │
│                                in depth                         │
└─────────────────────────────────────────────────────────────────┘
```

## İçindekiler (Detaylı)

| Seviye | Bölüm | Konular |
|:---|:---|:---|
| 🟢 Temel | [1. Idempotency — Tekrar Güvenliği ⭐](#1-idempotency--tekrar-güvenliği) | #1 öncelik: Idempotency anahtarı, Safe retry, Çift yazma önleme |
| 🟢 Temel | [2. Neden Dayanıklılık?](#2-neden-dayanıklılık) | Başarısızlık kaçınılmazdır, Hata türleri, Dayanıklılık zihniyeti |
| 🟢 Temel | [3. Timeout — Zaman Aşımı](#3-timeout--zaman-aşımı) | Connect/Socket/Total deadline, Timeout hiyerarşisi, Deadline propagation |
| 🟢 Temel | [4. Retry — Tekrar Deneme](#4-retry--tekrar-deneme) | Ne zaman tekrar denenir, Idempotency ilişkisi, Retry storm tehlikesi |
| 🟡 Orta | [5. Exponential Backoff & Jitter](#5-exponential-backoff--jitter) | Üstel geri çekilme, Jitter neden şart, Thundering herd |
| 🟡 Orta | [6. Circuit Breaker — Devre Kesici](#6-circuit-breaker--devre-kesici) | Closed/Open/Half-Open, Parametre seçimi, Slow-call vs failure rate |
| 🟡 Orta | [7. Bulkhead — Bölme Duvarı](#7-bulkhead--bölme-duvarı) | Thread pool vs semaphore, Kaynak izolasyonu, Blast radius |
| 🟡 Orta | [8. Fallback — Yedek Davranış](#8-fallback--yedek-davranış) | Fallback merdiveni, Graceful degradation, Partial response |
| 🔴 İleri | [9. Resilience Stack — Katmanlı Savunma](#9-resilience-stack--katmanlı-savunma) | Aspect order (doğru sıralama), Dekoratör kompozisyonu |
| 🔴 İleri | [10. Load Shedding — Yük Atma](#10-load-shedding--yük-atma) | CoDel, Adaptive LIFO, PID-based shedding, Scorecard engine |
| 🔴 İleri | [11. Backpressure — Geri Basınç](#11-backpressure--geri-basınç) | Bounded queue, TCP flow control, gRPC akış kontrolü |
| 🔴 İleri | [12. Chaos Engineering — Kaos Mühendisliği](#12-chaos-engineering--kaos-mühendisliği) | Hata enjeksiyonu, Game day, Hipotez odaklı test |
| ⚫ Uzman | [13. Ünlü Kesintilerden Dersler](#13-ünlü-kesintilerden-dersler) | Roblox, Cloudflare, Datadog, Meta, Atlassian vaka analizleri |
| ⚫ Uzman | [14. Defensive Coding — Savunmacı Programlama](#14-defensive-coding--savunmacı-programlama) | Girdi doğrulama, Assertion, Fail-safe batch, Bağımlılık yönetimi |
| ⚫ Uzman | [15. Tasarım Seviyesi Dayanıklılık](#15-tasarım-seviyesi-dayanıklılık) | Blast radius, Correlated failure domain, Fail-safe vs fail-secure, Defense in depth |

---

## 1. Idempotency — Tekrar Güvenliği ⭐

> **#1 Öncelik**: Idempotency olmadan hiçbir retry güvenli değildir. Dayanıklılık zincirinin **ilk ve en kritik halkasıdır**.

### 1.1 Idempotency Nedir?

Bir işlemin **birden fazla kez çalıştırılsa bile aynı sonucu üretmesi** özelliğidir. Retry yaptığın her yerde idempotency olmak zorundadır.

```
Idempotent:    f(x) = f(f(x))     → aynı isteği 1 kez de 10 kez de atsan sonuç aynı
Non-idempotent: f(x) ≠ f(f(x))    → her çağrıda yan etki birikir
```

### 1.2 Neden #1 Öncelik?

```
Retry yapıyorsun ama idempotent değilsin:
  POST /odeme → başarısız → retry → başarısız → retry → başarılı!
  Sonuç: Kullanıcının kartından 3 kez para çekildi 💸

Retry yapıyorsun VE idempotentsin:
  PUT /odeme/{idempotency-key} → başarısız → retry → başarısız → retry → başarılı!
  Sonuç: Kullanıcının kartından 1 kez para çekildi ✅
```

### 1.3 Idempotency Anahtarı (Idempotency Key)

İstemci her istek için **benzersiz bir anahtar** üretir. Sunucu aynı anahtarı ikinci kez görürse işlemi tekrarlamaz, ilk sonucu döndürür.

```
İstemci:  POST /payments  +  Header: Idempotency-Key: abc-123
Sunucu:   abc-123'ü daha önce gördün mü?
          → Hayır: işlemi yap, sonucu sakla (key → response)
          → Evet:  kayıtlı sonucu döndür, işlemi TEKRARLAMA
```

| Adım | Açıklama |
|:---|:---|
| **Anahtar üretimi** | UUID v7 (zamana dayalı) veya iş mantığından türetilmiş benzersiz değer |
| **Anahtar gönderimi** | HTTP Header (`Idempotency-Key`) veya istek gövdesinde |
| **Sunucu tarafı** | Anahtarı atomik olarak kontrol et + işle (`INSERT ... ON CONFLICT` veya Redis `SETNX`) |
| **Saklama süresi** | En az `max_retry_window + reconciliation_lag` (genelde 24 saat) |

### 1.4 Doğal Idempotent İşlemler

| İşlem | Idempotent mi? | Açıklama |
|:---|:---|:---|
| `GET /kullanici/42` | ✅ Evet | Okuma işlemleri doğası gereği idempotent |
| `PUT /kullanici/42` | ✅ Evet | Tam kaynak güncelleme — aynı body ile tekrar aynı sonuç |
| `DELETE /kullanici/42` | ✅ Evet | İlk seferde siler, sonrakiler 404 döner ama sonuç aynı |
| `PATCH /kullanici/42` | ⚠️ Değişir | `{ "yas": "$inc" }` idempotent değil; `{ "yas": 25 }` idempotent |
| `POST /kullanici` | ❌ Hayır | Her çağrı yeni kaynak yaratır — mutlaka idempotency key gerekir |
| `POST /odeme` | ❌ Hayır | **En tehlikeli** — mutlaka idempotency key zorunlu |

### 1.5 İki Katmanlı Idempotency

```
Katman 1 — İletişim (Network):   Aynı istek tekrar gelirse → aynı yanıtı döndür
Katman 2 — İş (Business):         Aynı iş mantıksal işlem tekrar gelirse → yan etkiyi tekrar uygulama

Örnek (Ödeme):
  Transport idempotency: Aynı HTTP isteği iki kez geldi → tek işlem
  Business idempotency:  Aynı sipariş için iki ödeme isteği → ikinciyi reddet
```

### 1.6 Veritabanında Idempotency

```sql
-- PostgreSQL: Idempotency anahtarını atomik olarak kontrol et + işle
INSERT INTO idempotency_keys (key, response, created_at)
VALUES ('abc-123', '{"status": "ok"}', NOW())
ON CONFLICT (key) DO NOTHING;

-- Eğer INSERT başarılıysa → işlemi yap
-- Eğer INSERT başarısızsa → anahtar zaten var, kayıtlı yanıtı döndür
```

```python
# Redis ile atomik idempotency kontrolü
def process_payment(idempotency_key: str, amount: float) -> Response:
    # SETNX: sadece key yoksa yazar, atomik
    if redis.setnx(f"idem:{idempotency_key}", "processing", ex=86400):
        try:
            result = do_payment(amount)
            redis.set(f"idem:{idempotency_key}", result.json(), ex=86400)
            return result
        except Exception:
            redis.delete(f"idem:{idempotency_key}")  # temizle ki retry yapabilsin
            raise
    else:
        # Anahtar zaten var → önceki sonucu döndür
        return Response.from_json(redis.get(f"idem:{idempotency_key}"))
```

### 1.7 Sık Yapılan Hatalar

| Hata | Sonuç | Doğrusu |
|:---|:---|:---|
| Idempotency key olmadan retry | Çift ödeme, çift kayıt, çift bildirim | Her mutasyon isteğinde idempotency key zorunlu |
| Çok kısa TTL | Retry penceresi içinde anahtar silinir → çift işlem | TTL > max retry penceresi |
| Farklı body, aynı key | İlk istek başarılı, ikinci farklı içerikle gelir → sessizce yanlış sonuç | Key ile body'i birlikte hash'le veya body değişirse yeni key üret |
| İşlem başarısızken key saklamak | Retry yapılamaz hale gelir | Sadece başarılı işlemlerin key'ini sakla |

> **Sözlük**: [Idempotency](../../reference-dictionary/fintech.md#retry-identity) · [Retry Identity](../../reference-dictionary/fintech.md#retry-identity)

**Pratik**: Mevcut projendeki tüm POST/PATCH/PUT endpoint'lerini listele. Hangilerinde idempotency key var? Hangileri riskli? En riskli olana bugün idempotency key ekle.

---

## 2. Neden Dayanıklılık?

### 2.1 Başarısızlık Kaçınılmazdır

Dağıtık sistemlerde **her şey bozulabilir**: ağ kesintileri, disk arızaları, bellek taşmaları, üçüncü taraf servis kesintileri, yanlış konfigürasyon değişiklikleri. "Başarısızlık olacak mı?" değil, **"Başarısızlık olduğunda ne yapacağız?"** sorusu sorulur.

```
Monolit → Tek bir noktada hata → sistem çöker
Dağıtık → Her bağlantı hata kaynağı → plansız sistem çöker
Dayanıklı Dağıtık → Her bağlantı hata kaynağı → sistem ayakta kalır
```

### 2.2 Hata Türleri

| Tür | Örnek | Strateji |
|:---|:---|:---|
| **Geçici (Transient)** | Ağ zaman aşımı, kısa süreli DB kilitlenmesi | Retry + Backoff |
| **Kalıcı (Permanent)** | Yanlış API anahtarı, kayıt bulunamadı | Fallback, hata döndür |
| **Kademeli (Gradual)** | DB bağlantı havuzu tükenmesi | Bulkhead, Circuit Breaker |
| **Ani (Sudden)** | Sunucu çökmesi, DNS kesintisi | Failover, Redundancy |

### 2.3 Dayanıklılık Zihniyeti

- **Her dış çağrı başarısız olabilir** — timeout mutlaka tanımla
- **Her başarılı yanıt garanti değildir** — yanıtı doğrula
- **Her bağımlılık seni yarı yolda bırakabilir** — fallback planla
- **"Best effort" yetmez** — kasıtlı olarak dayanıklı tasarla

> **Anahtar fikir**: Dayanıklılık sonradan eklenen bir özellik değil, **sıfırıncı günden itibaren** tasarımın parçasıdır.

**Pratik**: En son kullandığın REST API çağrısını düşün. Timeout tanımladın mı? Retry ekledin mi? Ya servis 10 saniye yanıt vermezse ne olur?

---

## 3. Timeout — Zaman Aşımı

### 3.1 Neden En Temel Kalıp?

Timeout olmadan **tek bir yavaş bağlantı tüm thread havuzunu tüketebilir**.

```
İstek → Servis A (yanıt yok, thread bekliyor...)
İstek → Servis A (yanıt yok, thread bekliyor...)
İstek → Servis A (yanıt yok, thread bekliyor...)
... tüm thread'ler tükendi → sistem çöktü
```

### 3.2 Timeout Hiyerarşisi

```
connect_timeout < socket_timeout < total_deadline
```

| Seviye | Anlamı | Önerilen Değer |
|:---|:---|:---|
| `connect_timeout` | TCP bağlantısı kurma süresi | 500ms – 2s |
| `socket_timeout` | Bağlantı sonrası yanıt bekleme | 2s – 10s |
| `total_deadline` | Tüm retry'ler dahil toplam süre | 30s – 60s |

### 3.3 Deadline Propagation (Zaman Sınırı Yayılımı)

Bir istek zincirinde (`A → B → C`), A'nın timeout'u B ve C'ye iletilmelidir. Aksi halde C, A çoktan vazgeçmiş olsa bile çalışmaya devam eder → **boşa kaynak tüketimi**.

```
Doğru:   A (deadline: 5s) → B (deadline: 4s) → C (deadline: 3s)
Yanlış:  A (deadline: 5s) → B (timeout yok) → C (timeout yok)
```

> **Sözlük**: [Timeout](../../reference-dictionary/resilience.md#timeout)

**Pratik**: HTTP istemcinde `connectTimeout`, `socketTimeout` ve `requestTimeout` ayarlarını incele. Hepsi tanımlı mı?

---

## 4. Retry — Tekrar Deneme

### 4.1 Ne Zaman Tekrar Denenir?

| Denenebilir | Denenmemeli |
|:---|:---|
| 503 Service Unavailable | 400 Bad Request |
| 429 Too Many Requests (Retry-After ile) | 401 Unauthorized |
| Ağ zaman aşımı (geçici) | 404 Not Found |
| Geçici DB kilitlenmesi | 422 Unprocessable Entity |

### 4.2 Idempotency (Tekrar Güvenliği)

> **Kural**: Retry yapıyorsan, işlem **idempotent** olmak zorundadır.

```
Tehlikeli:  POST /payments  → retry → çift ödeme!
Güvenli:   PUT /payments/{idempotency-key} → retry → aynı ödeme
```

**Idempotency anahtarı**: Her istek için benzersiz bir anahtar üret. Sunucu aynı anahtarı tekrar görürse, işlemi tekrarlamaz.

### 4.3 Retry Storm (Tekrar Deneme Fırtınası)

> **En tehlikeli anti-pattern**: Başarısız olan bir sisteme tekrar tekrar istek göndermek.

```
Normal yük: 1000 istek/sn
Sistem yavaşladı → her istek 3 kez retry → 3000 istek/sn
Sistem daha da yavaşladı → 9000 istek/sn → tamamen çöktü
```

**Çözüm**: Circuit Breaker + Exponential Backoff + Maksimum retry limiti.

> **Sözlük**: [Retry Amplification](../../reference-dictionary/resilience.md#retry-amplification)

**Pratik**: Bir ödeme API'si için retry stratejisi tasarla. Hangi hatalarda retry yaparsın? Kaç kez? Idempotency anahtarını nerede tutarsın?

---

## 5. Exponential Backoff & Jitter

### 5.1 Üstel Geri Çekilme

Her başarısız denemeden sonra bekleme süresi **katlanarak artar**:

```
Deneme 1 → başarısız → 100ms bekle
Deneme 2 → başarısız → 200ms bekle
Deneme 3 → başarısız → 400ms bekle
Deneme 4 → başarısız → 800ms bekle
Deneme 5 → başarısız → 1600ms bekle (maksimum sınıra kadar)
```

**Neden?** Sisteme nefes alma şansı verir. Anlık bir ağ kesintisiyse, sistem kendini toparlayana kadar beklemiş olursun.

### 5.2 Jitter — Rastgele Gecikme

Jitter olmadan, aynı backoff algoritmasını kullanan **tüm istemciler aynı anda tekrar dener** → Thundering Herd (Gök Gürültülü Sürü).

```
Jitter'sız:  100ms, 200ms, 400ms, 800ms  → tüm istemciler aynı anda
Jitter'lı:   87ms, 215ms, 378ms, 832ms   → istemciler dağınık
```

| Jitter Türü | Formül | Kullanım |
|:---|:---|:---|
| **Full Jitter** | `random(0, backoff)` | En iyi dağılım |
| **Equal Jitter** | `backoff/2 + random(0, backoff/2)` | Dengeli |
| **Decorr Jitter** | `max(base, random(prev * 3, prev * 3))` | AWS tarafından kullanılır |

> **Sözlük**: [Exponential Backoff](../../reference-dictionary/resilience.md#exponential-backoff), [Jitter](../../reference-dictionary/resilience.md#jitter), [Thundering Herd](../../reference-dictionary/resilience.md#thundering-herd)

**Pratik**: 5 istemcinin aynı anda bir servise retry yaptığını simüle et (kağıt üzerinde). Jitter'lı ve Jitter'sız durumda istek dağılımını karşılaştır.

---

## 6. Circuit Breaker — Devre Kesici

### 6.1 Üç Durum

```
       ┌──────────┐
       │  CLOSED  │ ← Normal çalışma, tüm çağrılar geçer
       └────┬─────┘
            │ hata eşiği aşıldı
            ▼
       ┌──────────┐
       │   OPEN   │ ← Tüm çağrılar anında reddedilir
       └────┬─────┘
            │ waitDurationInOpenState süresi doldu
            ▼
       ┌──────────┐
       │HALF-OPEN │ ← Sınırlı sayıda probe çağrısı
       └────┬─────┘
            │ probe başarılı → CLOSED
            │ probe başarısız → OPEN
```

### 6.2 Kritik Parametreler

| Parametre | Anlamı | Önerilen |
|:---|:---|:---|
| `failureRateThreshold` | Hata oranı eşiği | %50 |
| `slowCallRateThreshold` | Yavaş çağrı oranı eşiği | %50 |
| `slowCallDurationThreshold` | "Yavaş" sayılan süre | 2s |
| `minimumNumberOfCalls` | Değerlendirme için min. çağrı | 10 |
| `slidingWindowSize` | Pencere boyutu | 100 |
| `waitDurationInOpenState` | OPEN → Half-Open süresi | 30s |

### 6.3 Slow-Call Rate Neden Önemli?

> **Anahtar içgörü**: Sadece hata oranına değil, **yavaş çağrı oranına da bak**. 6 saniyede gelen "başarılı" yanıt, kullanıcı için başarısızlıktır.

### 6.4 Fallback Olmadan Circuit Breaker Eksiktir

OPEN durumda fallback yoksa → sadece daha hızlı bir hatadır, koruma değil.

> **Kaynak**: [circuit-breaker-honesty.md](circuit-breaker-honesty.md), [resilience-patterns.md §resilience-02](resilience-patterns.md#resilience-02-circuit-breaker--stop-calling-dead-services)

**Pratik**: Bir Circuit Breaker kütüphanesini (Resilience4j, Polly, Hystrix) incele. Kendi projende en az bir dış servis çağrısına ekle.

---

## 7. Bulkhead — Bölme Duvarı

### 7.1 Gemi Metaforu

Bir gemide bölmeler (bulkhead) vardır. Bir bölme su alsa bile gemi batmaz — su diğer bölmelere yayılmaz.

```
Bulkhead'siz:  Tüm çağrılar tek thread havuzu → 1 bağımlılık tüm sistemi çökertir

                ┌─────────────────────────────┐
                │    Ortak Thread Havuzu       │
                │  DB çağrısı │ API çağrısı   │ ← DB yavaşlayınca API de kitlenir
                └─────────────────────────────┘

Bulkhead'li:   Her bağımlılık için ayrı havuz

                ┌──────────┐  ┌──────────┐
                │ DB Havuz │  │API Havuz │ ← DB yavaşlasa bile API çalışır
                └──────────┘  └──────────┘
```

### 7.2 İki Tür Bulkhead

| Tür | Mekanizma | Avantaj | Dezavantaj |
|:---|:---|:---|:---|
| **Thread Pool** | Her bağımlılık için ayrı thread havuzu | Tam izolasyon, sıra bekleme yok | Daha fazla thread, context switching |
| **Semaphore** | Eşzamanlı çağrı limiti | Hafif, az kaynak | Sıra bekleme var, timeout riski |

### 7.3 Circuit Breaker vs Bulkhead

| | Circuit Breaker | Bulkhead |
|:---|:---|:---|
| **Karar** | Çağrı yapılmalı mı? | Kaç çağrı aynı anda yapılabilir? |
| **Koruduğu** | Bağımlılığı (daha fazla zarar verme) | Kendini (kaynaklarını tüketme) |
| **Birlikte** | CB OPEN → hiç çağrı yok, Bulkhead boşta | Bulkhead dolu → CB'ye sıra gelmez |

> **Sözlük**: [Bulkhead](../../reference-dictionary/resilience.md#bulkhead), [Blast Radius](../../reference-dictionary/resilience.md#blast-radius)

**Pratik**: Sistemindeki tüm dış bağımlılıkları listele. Hangileri aynı thread havuzunu paylaşıyor? Hangilerinin ayrılması gerekir?

---

## 8. Fallback — Yedek Davranış

### 8.1 Fallback Merdiveni

En iyiden en kötüye:

```
1. Stale Cache   → "5 dakika önceki sonuç buydu, işte o"
2. Static Default → "Varsayılan öneriler listesi"
3. Degraded UX   → "Öneriler şu anda gösterilemiyor" (ama sayfa çalışıyor)
4. Meaningful Err → "Lütfen daha sonra tekrar deneyin" (açıklayıcı hata)
```

### 8.2 Graceful Degradation (Kontrollü Bozulma)

Tamamen çökmek yerine **azaltılmış işlevsellikle** çalışmaya devam et.

```
Tam çöküş:  500 Internal Server Error → kullanıcı hiçbir şey göremez
Kontrollü:  200 OK ama "Son aktiviteler" bölümü yok → kullanıcı profili görür
```

### 8.3 Partial Response (Kısmi Yanıt)

Bir sayfa birden fazla servisten veri alıyorsa, **bozuk bölümü atla, sağlamları göster**:

```json
{
  "user": {"name": "Ali", "email": "ali@ornek.com"},
  "recommendations": null,        // ← öneri servisi kapalı
  "recentActivity": [...],         // ← aktivite servisi çalışıyor
  "_warnings": ["recommendations: servis geçici olarak kullanılamıyor"]
}
```

> **Sözlük**: [Fallback](../../reference-dictionary/resilience.md#fallback), [Graceful Degradation](../../reference-dictionary/resilience.md#graceful-degradation), [Partial Response](../../reference-dictionary/resilience.md#partial-response)

**Pratik**: Kendi uygulamanın ana sayfasını düşün. Hangi veriler kritik (olmazsa sayfa çalışmaz)? Hangileri isteğe bağlı (olmazsa da olur)?

---

## 9. Resilience Stack — Katmanlı Savunma

### 9.1 Doğru Sıralama (Aspect Order)

```java
// ✅ DOĞRU sıralama
@TimeLimiter(timeout = 5s)       // 1. Önce zaman sınırı
@CircuitBreaker(...)             // 2. Devre kesici
@Bulkhead(maxConcurrent = 10)    // 3. Kaynak izolasyonu
@Retry(maxAttempts = 3)          // 4. Tekrar deneme
@Fallback(method = "fallback")   // 5. Yedek davranış
public Result callService() { ... }

// ❌ YANLIŞ sıralama
@Retry(maxAttempts = 3)          // Retry dışarıda → CB hataları görmez!
@Bulkhead(maxConcurrent = 10)
@CircuitBreaker(...)
@TimeLimiter(timeout = 5s)
@Fallback(method = "fallback")
```

### 9.2 Her Katmanın Görevi

| Katman | Ne Yapar? | Neden Bu Sırada? |
|:---|:---|:---|
| **TimeLimiter** | Çalışma süresini sınırlar | Kaynak israfını en baştan engelle |
| **CircuitBreaker** | Bozuk bağımlılığı atlar | Retry'leri sayarak hata oranını doğru hesapla |
| **Bulkhead** | Eşzamanlı çağrı limiti | Çalışan bağımlılıkları koru |
| **Retry** | Geçici hataları tekrar dene | Bulkhead içinde, CB'den sonra |
| **Fallback** | Hepsi başarısız olursa yedek yanıt | Son çare, her zaman en dışta |

> **Kaynak**: [resilience-patterns.md §resilience-06](resilience-patterns.md#resilience-06-the-resilience-stack), [circuit-breaker-honesty.md §cb-06](circuit-breaker-honesty.md#cb-06-the-honest-resilience-stack)

**Pratik**: Bir servis çağrısı için yukarıdaki 5 katmanı sırasıyla uygula. Hata durumunda hangi katmanın devreye girdiğini log'la.

---

## 10. Load Shedding — Yük Atma

### 10.1 Problem: Trafik Aniden Patladı

```
Normal: 1000 istek/sn → sistem rahat
Kampanya başladı: 5000 istek/sn → kuyruklar doluyor
Kullanıcılar retry yapıyor: 15000 istek/sn → sistem çöktü
```

Load shedding: "Hepsini işlemeye çalışıp çökmektense, **bazılarını bilinçli olarak reddet**."

### 10.2 Stratejiler (Basitten Karmaşığa)

| Strateji | Nasıl Çalışır? | Avantaj | Dezavantaj |
|:---|:---|:---|:---|
| **Statik Rate Limiting** | İstemci başına sabit limit | Basit | Adaletsiz, esnek değil |
| **CoDel** | Kuyrukta bekleme süresine göre atma | Bufferbloat'ı önler | Sadece gecikme sinyaline bakar |
| **Adaptive LIFO** | Yük altında en yeni isteği önce işle | Eski istekler zaten timeout olur | Tüm istekler eşit önemliyse uymaz |
| **PID-Based Shedding** | PID kontrolcü ile hedef gecikmeye ayarla | Dinamik, kendini ayarlar | Ayarlanması gereken parametreler var |
| **Scorecard Engine** | CPU + Gecikme + Hata + Kuyruk → bileşik skor | Çok boyutlu karar | Karmaşık |

### 10.3 CoDel (Controlled Delay) Derinlemesine

CoDel, kuyruktaki paketlerin **minimum** gecikmesine bakar, ortalamaya değil:

```
Hedef gecikme: 5ms
Aralık: 100ms

Eğer son 100ms'deki minimum gecikme > 5ms → paket at
Eğer minimum gecikme < 5ms → interval sıfırla
```

> **Sözlük**: [Load Shedding](../../reference-dictionary/resilience.md#load-shedding), [CoDel](../../reference-dictionary/resilience.md#codel-controlled-delay), [Adaptive LIFO](../../reference-dictionary/resilience.md#adaptive-lifo)

> **Kaynak**: [uber-load-shedding.md](uber-load-shedding.md)

**Pratik**: Sisteminde hangi endpoint'ler kritik (asla atılmamalı)? Hangileri düşük öncelikli (yük altında atılabilir)? Bir öncelik matrisi oluştur.

---

## 11. Backpressure — Geri Basınç

### 11.1 Problem: Hızlı Üretici, Yavaş Tüketici

```
Üretici: 1000 mesaj/sn üretiyor
Tüketici: 100 mesaj/sn işliyor
Aradaki fark: 900 mesaj/sn → kuyruk sonsuza kadar büyür → OOM (Out of Memory)
```

### 11.2 Çözüm Katmanları

| Katman | Mekanizma | Örnek |
|:---|:---|:---|
| **Bounded Queue** | Kuyruk boyutu sınırlı | `new ArrayBlockingQueue(1000)` |
| **TCP Flow Control** | Alıcı penceresi daralır, gönderici yavaşlar | TCP receive window |
| **gRPC Flow Control** | Per-stream buffer limiti | `maxInboundMessageSize` |
| **Reactive Streams** | `request(n)` ile talep sinyali | `backpressure` sinyali upstream'e yayılır |

### 11.3 Kuyruk Dolduğunda Ne Yapmalı?

| Politika | Davranış | Ne Zaman? |
|:---|:---|:---|
| **Block** | Üreticiyi bekle | Dayanıklılık > Gecikme |
| **Drop (Head)** | En eskiyi at | En yeni veri önemli (canlı yayın) |
| **Drop (Tail)** | En yeniyi at | Sıralama önemli (işlem kaydı) |
| **CallerRuns** | Üretici thread'de çalıştır | Doğal backpressure (Java ThreadPoolExecutor) |

> **Sözlük**: [Backpressure](../../reference-dictionary/resilience.md#backpressure)

**Pratik**: Projendeki bir kuyruk yapısını incele. Sınırsız mı? Sınırlıysa, dolduğunda ne oluyor?

---

## 12. Chaos Engineering — Kaos Mühendisliği

### 12.1 Felsefe

> "Sisteminin nasıl bozulacağını, bozulmadan önce öğren."

### 12.2 Adım Adım Chaos Engineering

```
1. Kararlı Durum Tanımla → "Normalde p99 gecikme 200ms"
2. Hipotez Kur        → "Redis'i durdurursak Fallback devreye girer"
3. Deney Tasarla      → "Traffiğin %1'ine Redis kesintisi uygula"
4. Patlatma Yarıçapını Sınırla → "Sadece staging'de, sadece Canary'de"
5. Gözlemle           → "p99 200ms → 450ms oldu, Fallback cevap verdi ✓"
6. Düzelt/Ayarla      → "Fallback süresi 2s → 500ms'e indi, iyileştir"
```

### 12.3 Ne Zaman Yapılmaz?

- İzleme ve rollback yeteneği yoksa
- Üretim trafiğinin tamamında (önce canary)
- Bir kerelik gösteri olarak (sürekli pratik gerekir)

> **Sözlük**: [Chaos Engineering](../../reference-dictionary/resilience.md#chaos-engineering)

**Pratik**: En basit Chaos deneyini tasarla: bir servisin 2 saniye gecikmeli yanıt verdiğini simüle et. Circuit Breaker'ın açıldığını gözlemle.

---

## 13. Ünlü Kesintilerden Dersler

> **Kaynak**: [famous-outages.md](famous-outages.md)

| Şirket | Yıl | Kök Neden | Alınacak Ders |
|:---|:---|:---|:---|
| **Roblox** | 2021 | Konsol arka plan görevi yanlışlıkla Consul cluster'ını durdurdu → gözlemlenebilirlik çöktü → sorun tespit edilemedi | Gözlemlenebilirlik, izlediğin sistemden **bağımsız** olmalı |
| **Cloudflare** | 2019 | 1 regex kuralı CPU'yu %100'e çıkardı, 30 dakika kesinti | Girdi doğrulama her katmanda şart; regex timeout'u olmalı |
| **Datadog** | 2023 | 5 "bağımsız" bölge aynı OS güncellemesini aynı anda aldı → hepsi çöktü | Correlated failure domain: bağımsız görünen sistemler aynı gizli bağımlılığı paylaşabilir |
| **Meta** | 2021 | DNS sunucuları sağlık kontrolü başarısız olunca BGP route'larını geri çekti → tüm sunucular aynı anda kendini ağdan sildi | Fail-safe mekanizmaların "tümü aynı anda tetiklenirse" senaryosunu modelle |
| **Atlassian** | 2022 | Otomasyon betiği yanlış tenant ID ile çalıştı → 775 müşteri hesabı silindi | İnsan onayı olmadan kritik operasyon çalıştırma; betiklerde dry-run zorunlu olsun |

**Pratik**: Kendi sisteminde bir "bağımlılık haritası" çıkar. Hangi bileşenler aynı anda güncelleniyor? Aynı DNS çözümleyiciyi mi kullanıyorlar? Aynı paket kayıt defterinden mi çekiyorlar?

---

## 14. Defensive Coding — Savunmacı Programlama

### 14.1 Temel İlkeler

| İlke | Anlamı | Örnek |
|:---|:---|:---|
| **Her girdi şüpheli** | Dışarıdan gelen her şeyi doğrula | `if (input == null \|\| input.isEmpty())` |
| **Her hata ele alınır** | Unhandled exception = tasarım hatası | Try-catch her dış çağrıda |
| **Invariant'lar assertion'dır** | "Bu noktada X her zaman doğru olmalı" | `assert balance >= 0 : "Negatif bakiye!"` |
| **Bağımlılıklar denetlenir** | 3. parti kütüphaneler CVE taramasından geçer | `npm audit`, `pip audit` |

### 14.2 Fail-Safe Batch İşleme

```python
# ❌ YANLIŞ: tek bir hatalı kayıt tüm batch'i durdurur
for record in batch:
    process(record)  # 500. kayıtta hata → 1-499 boşa gitti

# ✅ DOĞRU: hatalı kaydı atla, devam et
for record in batch:
    try:
        process(record)
    except Exception as e:
        dead_letter_queue.send(record, error=e)
        metrics.increment("batch.errors")
        continue  # sonraki kayda geç
```

### 14.3 Assertion Kullanımı

```java
// Geliştirme/test ortamında aktif, production'da pasif
assert connection != null : "Bağlantı havuzu boş dönmemeli";
assert amount > 0 : "Ödeme miktarı pozitif olmalı, gelen: " + amount;
```

> **Kaynak**: [defensive-coding.md](defensive-coding.md)

**Pratik**: Kod tabanında `catch (Exception e) { }` (boş catch) ara. Her birini ya log'la ya da uygun şekilde işle.

---

## 15. Tasarım Seviyesi Dayanıklılık

### 15.1 Blast Radius (Patlatma Yarıçapı)

Bir hatanın etkilediği kullanıcı/servis/veri kapsamı.

```
Büyük Blast Radius:  Global konfigürasyon değişikliği → tüm kullanıcılar etkilenir
Küçük Blast Radius:  Canary deployment → kullanıcıların %1'i etkilenir
```

**Azaltma stratejileri**: Sharding, bölgesel bağımsızlık, canary deployment, ring-based rollout.

### 15.2 Correlated Failure Domain (İlişkili Hata Alanı)

Bağımsız görünen ama **aynı gizli bağımlılığı paylaştığı için birlikte çöken** bileşenler.

```
Görünürde:   EU-West, US-East, APAC → 3 bağımsız bölge
Gerçekte:    Hepsi aynı OS imajını, aynı anda günceller → tek hata alanı
```

### 15.3 Fail-Safe vs Fail-Secure

| | Fail-Safe (Açık) | Fail-Secure (Kapalı) |
|:---|:---|:---|
| **Öncelik** | Erişilebilirlik | Güvenlik/Doğruluk |
| **Hata davranışı** | Çalışmaya devam et (bozulmuş da olsa) | Durdur (yanlış çalışmaktansa) |
| **Örnek** | Asansör freni (elektrik kesilince kilitlenir, düşmez) | Kapı kilidi (elektrik kesilince kilitli kalır) |
| **Yazılım** | Önbellekten servis et (güncel değil ama var) | Ödeme başarısız (eksik ödeme yapmaktansa) |

### 15.4 Defense in Depth (Katmanlı Savunma)

Tek bir güvenlik veya dayanıklılık mekanizmasına güvenme. Her katman bağımsız olmalı:

```
İstek → Rate Limiter → Input Validation → Auth → CircuitBreaker → Bulkhead → Retry → Business Logic
        ↑               ↑                  ↑      ↑               ↑         ↑        ↑
        Her katman farklı bir hata sınıfına karşı koruma sağlar
```

> **Sözlük**: [Blast Radius](../../reference-dictionary/resilience.md#blast-radius), [Correlated Failure Domain](../../reference-dictionary/resilience.md#correlated-failure-domain), [Fail-safe vs Fail-secure](../../reference-dictionary/resilience.md#fail-safe-vs-fail-secure), [Defense in Depth](../../reference-dictionary/resilience.md#defense-in-depth)

---

## Öğrenme Yolu Özeti

```
🟢 Temel (1-2 hafta)
   ├── ⭐ Idempotency: TÜM mutasyon işlemlerine idempotency key ekle
   ├── Timeout her çağrıya ekle
   ├── Retry + Idempotency ilişkisini anla
   └── Basit bir fallback uygula

🟡 Orta (2-4 hafta)
   ├── Circuit Breaker + Bulkhead ekle
   ├── Exponential Backoff + Jitter uygula
   └── Resilience Stack'i doğru sırayla birleştir

🔴 İleri (1-2 ay)
   ├── Load Shedding stratejisi seç ve uygula
   ├── Backpressure mekanizması kur
   └── İlk Chaos deneyini üretimde (canary) çalıştır

⚫ Uzman (sürekli)
   ├── Ünlü kesintileri analiz et, kendi sistemine uygula
   ├── Defensive coding'i kod inceleme kültürüne yerleştir
   └── Mimari seviyede blast radius ve failure domain analizi yap
```

---

## Referanslar

| Kaynak | Bağlantı |
|:---|:---|
| Resilience Sözlüğü | [reference-dictionary/resilience.md](../../reference-dictionary/resilience.md) (31 terim) |
| Resilience Pattern'ları | [resilience-patterns.md](resilience-patterns.md) (`resilience-01` – `resilience-06`) |
| Circuit Breaker Derinlemesine | [circuit-breaker-honesty.md](circuit-breaker-honesty.md) (`cb-01` – `cb-07`) |
| Ünlü Kesintiler | [famous-outages.md](famous-outages.md) (`resilience-07` – `resilience-11`) |
| Defensive Coding | [defensive-coding.md](defensive-coding.md) (`arch-12` – `arch-15`) |
| Distributed Resilience | [distributed-resilience-patterns.md](distributed-resilience-patterns.md) (`resilience-12` – `resilience-16`) |
| Uber Load Shedding | [uber-load-shedding.md](uber-load-shedding.md) (`resilience-17` – `resilience-21`) |
| Azure Dayanıklılık | [architecture-azure/observability/](../../architecture-azure/observability/) |
| Taksonomi | §7.1 Reliability & Resilience |

---

> **Son söz**: Dayanıklılık bir varış noktası değil, **sürekli bir pratiktir**. Bugün timeout ekle, yarın circuit breaker, sonraki hafta chaos experiment. Her adım sistemi biraz daha sağlamlaştırır.
