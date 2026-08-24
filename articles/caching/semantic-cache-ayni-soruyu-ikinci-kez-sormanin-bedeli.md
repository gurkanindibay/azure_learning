---
type: Article
title: "Semantic Cache: Aynı Soruyu İkinci Kez Sormanın Bedeli"
description: "LLM maliyet ve gecikmelerini azaltmak için semantic cache mimarisi: embedding modelleri, cosine similarity, ANN vektör arama, threshold seçimi ve production tuzakları."
source: "https://medium.com/@gokhandyncer/semantic-cache-ayn%C4%B1-soruyu-i%CC%87kinci-kez-sorman%C4%B1n-bedeli-99fc857bb56f"
author: "Gökhan Dinçer"
published: 2026-08-17
created: 2026-08-24
tags:
  - semantic-cache
  - caching
  - llm
  - embeddings
  - vector-search
  - redis
  - faiss
---

# Semantic Cache: Aynı Soruyu İkinci Kez Sormanın Bedeli

> **Source**: [Medium — Semantic Cache: Aynı Soruyu İkinci Kez Sormanın Bedeli](https://medium.com/@gokhandyncer/semantic-cache-ayn%C4%B1-soruyu-i%CC%87kinci-kez-sorman%C4%B1n-bedeli-99fc857bb56f) by Gökhan Dinçer (2026-08-17)  
> **Domain**: [Caching →](index.md)  
> **Related Takeaways**: [Semantic Caching for LLMs — Key Takeaways](../../system-design-architecture/caching/semantic-cache-llm-takeaways.md) · [Reference Dictionary (Caching)](../../reference-dictionary/caching.md#semantic-cache)

![Semantic Cache Banner](https://miro.medium.com/v2/resize:fit:1400/format:webp/0*SX94rYYhsiR7nBKN.jpg)

*LLM’ler pahalı. Kullanıcılar ise aynı şeyi farklı kelimelerle sormakta ısrarcı. Bu iki gerçeğin kesiştiği yerde semantic cache duruyor.*

---

## 1. Faturanın Hikâyesi

Bir e-ticaret destek chatbot’u yazdın. Canlıya aldın. İlk hafta güzel gidiyor, sonra faturaya bakıyorsun.

Logları açıp gelen soruları okuyorsun:

```text
"kargom nerede"
"siparişim ne zaman gelir"
"paketim hala gelmedi ne yapmalıyım"
"kargo takip nasıl yapılır"
"siparişimi nereden takip edebilirim"
"kargom nerde acaba"
"kargom nerede?"
```

Bunlar farklı sorular mı? Hayır. **Tek bir sorunun yedi farklı yazılışı.** Ama modelin umurunda değil — her biri için baştan düşünüyor, her biri için token yakıyor, her biri için 2–3 saniye bekletiyor.

Üstelik cevap her seferinde aynı: *“Siparişlerim sayfasından takip numaranızla sorgulayabilirsiniz.”*

Model, aynı cümleyi yedi kez, sıfırdan, para vererek üretti.

İşte semantic cache tam olarak bu israfı durdurmak için var.

---

## 2. İki Tip Çağrı Merkezi Temsilcisi

Bir çağrı merkezi düşün. İki temsilci çalışıyor.

**Ahmet — acemi temsilci.** Elinde bir defter var. Defterde daha önce cevapladığı sorular ve cevapları yazılı. Ama Ahmet çok katı çalışıyor: gelen soruyu defterdekiyle **harfi harfine** karşılaştırıyor.

> Müşteri: “Kargom nerede?” Ahmet: (defteri kontrol eder) Evet, bu var! İşte cevabınız.
> 
> Müşteri: “Kargom nerede acaba?” Ahmet: (defteri kontrol eder) Bu soru defterimde yok. Uzmana aktarıyorum…

Tek bir “acaba” kelimesi Ahmet’i devre dışı bıraktı. Ahmet, klasik cache’tir.

**Ayşe — deneyimli temsilci.** Ayşe’nin defteri de var ama Ayşe kelimelere değil **anlama** bakıyor.

> Müşteri: “Paketim hala gelmedi, ne yapmalıyım?” Ayşe: (düşünür) Bu aslında geçen hafta cevapladığım “kargom nerede” sorusuyla aynı şey. Defterden okuyorum.

Ayşe, semantic cache’tir.

Ama işin bir de karanlık tarafı var. Ayşe deneyimli olduğu için bazen **fazla özgüvenli** davranıyor:

> Müşteri: “İade süresi 14 gün değil mi?” Ayşe: (düşünür) “İade süresi 14 gün mü?” sorusuyla neredeyse aynı. Evet, 14 gündür!

İki soru kelime olarak neredeyse aynı ama biri onay istiyor, diğeri bilgi istiyor — ve eğer iade süresi 30 günse Ayşe müşteriye yanlış bilgi verdi.

Semantic cache’in bütün hikâyesi bu ikilemde: Ayşe’nin hızı da, hatası da aynı yetenekten geliyor. İlerleyen bölümlerde bu ikilemi ölçmeye ve yönetmeye çalışacağız.

---

## 3. Klasik Cache Neden Çöküyor?

Klasik yaklaşım basit:

```python
key = hashlib.sha256(prompt.encode()).hexdigest()
cached = redis.get(key)
if cached:
    return cached
```

Bu, veritabanı sorgularında harika çalışır. `SELECT * FROM users WHERE id=42` her zaman aynı stringtir.

Ama doğal dil böyle davranmaz. Hash fonksiyonunun doğası gereği **tek bir karakter değişirse anahtar tamamen değişir**:

```text
"kargom nerede"   → sha256: a3f9c2...
"kargom nerede?"  → sha256: 7b1e04...   ← tamamen farklı!
"Kargom nerede"   → sha256: e5d883...   ← yine farklı!
```

Gerçek trafikte exact-match cache’in hit oranı genelde %5'in altında kalır. Neredeyse hiç çalışmaz.

### Türkçe’de durum daha da beter

Türkçe eklemeli (agglutinative) bir dil. Aynı kökten devasa bir varyasyon uzayı doğuyor:

```text
kargo
kargom
kargomun
kargoma
kargomdan
kargolarım
kargolarımın
siparişim
siparişimin
siparişimdeki
```

İngilizce’de *“where is my package”* etrafında belki 3–5 doğal varyasyon vardır. Türkçe’de aynı niyeti ifade etmenin onlarca yolu var — üstelik ek yapısı yüzünden karakter düzeyinde birbirlerine hiç benzemiyorlar.

Yani exact-match cache Türkçe bir üründe İngilizce’dekinden **daha da** işe yaramaz. Semantic cache burada opsiyonel bir optimizasyon değil, neredeyse zorunluluk.

---

## 4. Semantic Cache Nedir? — Boru Hattı

Fikir şu: soruyu string olarak değil, **anlamının vektör temsili** olarak sakla.

![Semantic Cache Pipeline](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*8UhwcohTPo7SIz02Pd8aZA.png)

Kilit nokta: **hit yolu ile miss yolu arasında ~400 kat hız farkı var.**

![Hit vs Miss Comparison](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*QGKVHVwRj1DZEXLxnt1yDA.png)

---

## 5. Kalbindeki Matematik

### Cosine Similarity

İki vektörün ne kadar “aynı yöne baktığını” ölçüyoruz:

![Cosine Similarity Formula](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*MawUOn9_FuOFCV1CkpDwPg.png)

Uzunluk değil **yön** önemli, çünkü anlam yöne kodlanıyor. “kargom nerede” ile “paketim nerede” vektörleri yaklaşık aynı yöne bakar; “kargom nerede” ile “iade nasıl yapılır” bakmaz.

**Pratik hile:** Vektörleri baştan birim uzunluğa normalize edersen paydalar 1 olur ve cosine similarity basit bir nokta çarpımına iner:

![Normalized Cosine Similarity](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*vkxrfKEZixIru4zKFsghJw.png)

Bu sadece matematiksel bir zarafet değil — tüm cache’i tek bir matris çarpımına indirger.

### Karar Kuralı

![Decision Rule](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*pcDLR1EmANL-xak4pzRG5g.png)

Tüm sistemin kaderi tek bir sayıya, **$\tau$ (tau) eşiğine** bağlı. Bu sayıyı nasıl seçeceğimiz (ve neden seçemeyeceğimiz) yazının ilerleyen kısmının konusu.

### Neden Brute-Force Değil? — ANN

Cache’te 10 kayıt varken hepsiyle tek tek karşılaştırmak sorun değil. 10 milyon kayıtta felaket.

Çözüm: **Approximate Nearest Neighbor (ANN)** arama. En yaygını **HNSW** (Hierarchical Navigable Small World). Mantığı sezgisel olarak şu:

```text
Katman 2 (seyrek):   A ────────────── D          ← uzun atlamalar
                     │                │
Katman 1 (orta):     A ─── B ──────── D ─── F
                     │     │          │     │
Katman 0 (tam):      A──B──C──D──E──F──G──H──I   ← tüm noktalar
```

Üst katmandan başlayıp uzun atlamalarla hedefe kabaca yaklaşıyorsun, sonra aşağı inip ince ayar yapıyorsun. Şehirlerarası yolculukta önce otoyola çıkıp sonra sokak aramak gibi. Sonuç: doğrusal tarama yerine logaritmik yakınlıkta bir arama.

“Approximate” kelimesi önemli — %100 doğru komşuyu bulmayı garanti etmiyor. Ama cache için bu kabul edilebilir: en yakın komşuyu kaçırırsan olacak şey sadece bir cache miss, yani modele sorarsın. Felaket değil.

### Maliyet Modeli

Asıl soru: bu iş ne zaman kâra geçiyor?

Hit oranı **$h$** olsun. Her istek için beklenen maliyet:

![Cost Model Equation](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*APY588xeatrb9IhWeId-Gg.png)

Dikkat: $c_{\text{embed}}$ **her istekte** ödenir (hit için de arama yapman lazım), $c_{\text{LLM}}$ ise sadece miss’lerde.

Cache’siz maliyet $c_{\text{LLM}}$ olduğuna göre, kârlı olma koşulu:

![Profitability Condition](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*1npLFcF4nESeP88BX5D-3g.png)

Şimdi somut sayı koyalım. Lokal bir embedding modeli kullanıyorsan API maliyeti sıfıra yakın — diyelim bir LLM çağrısının binde biri. O zaman:

![Break-even Calculation](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*OBp1P8swE-NkI3fvQugWfA.png)

**Yani binde bir hit alsan bile kârdasın.** Gerçek chatbot trafiğinde hit oranları %30–60 bandına çıkabiliyor:

![Hit Rate Scenarios](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*xj387HfF5_FSIMYcMe_8mg.png)

Bu yüzden semantic cache, LLM uygulamalarındaki en yüksek getirili optimizasyonlardan biri.

Ama bu hesap sadece **paradan** bahsediyor. Yanlış cevabın maliyeti bu formülde yok — ve o maliyet çok daha yüksek olabilir.

---

## 6. Sıfırdan İmplementasyon

### Önce Embed Fonksiyonu

Aşağıdaki her şey bir `embed(text) -> vektör` fonksiyonuna dayanıyor:

```bash
pip install sentence-transformers
```

```python
from sentence_transformers import SentenceTransformer
 
model = SentenceTransformer("intfloat/multilingual-e5-small")

def embed(text: str):
    # E5 ailesi için 'query: ' öneki kaliteyi artırır
    return model.encode(f"query: {text}", normalize_embeddings=True)
```

Deneyelim:

```python
import numpy as np

v1 = embed("kargom nerede")
v2 = embed("paketim hala gelmedi")
v3 = embed("bugün hava çok güzel")

print("v1 vs v2 (aynı anlam):", np.dot(v1, v2))  # ~0.89
print("v1 vs v3 (alakasız):  ", np.dot(v1, v3))  # ~0.62
```

Cosine similarity, iki ilgili soruda **0.89**, alakasızda **0.62** verdi. Şimdi bunu bir cache sınıfına bağlayalım.

### Cache Sınıfı

```python
import time
import numpy as np

class SemanticCache:
    def __init__(self, embed_fn, threshold=0.85, max_size=10000):
        self.embed_fn  = embed_fn
        self.threshold = threshold
        self.max_size  = max_size
        self.vectors   = None   # np.ndarray, shape (N, dim)
        self.entries   = []     # [{"query": str, "answer": str, ...}]

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def lookup(self, query):
        """Cache'te ara. Hit varsa (cevap, benzerlik), yoksa (None, en_yüksek_benzerlik)."""
        if self.vectors is None or len(self.entries) == 0:
            return None, 0.0

        q = self._normalize(self.embed_fn(query))

        # Tek bir matris çarpımı: (N, dim) @ (dim,) -> (N,)
        similarities = self.vectors @ q

        best_idx = np.argmax(similarities)
        best_sim = similarities[best_idx]

        if best_sim >= self.threshold:
            self.entries[best_idx]["hits"] += 1
            self.entries[best_idx]["last_used"] = time.time()
            return self.entries[best_idx]["answer"], float(best_sim)

        return None, float(best_sim)

    def store(self, query, answer):
        """Yeni bir soru-cevap çiftini cache'e ekle."""
        q = self._normalize(self.embed_fn(query))

        if self.vectors is None:
            self.vectors = q.reshape(1, -1)
        else:
            self.vectors = np.vstack([self.vectors, q])

        self.entries.append({
            "query": query, "answer": answer,
            "hits": 0, "created": time.time(), "last_used": time.time(),
        })

        if len(self.entries) > self.max_size:
            self._evict()

    def _evict(self):
        """En az kullanılanı at (LFU)."""
        victim = min(range(len(self.entries)),
                     key=lambda i: self.entries[i]["hits"])
        self.vectors = np.delete(self.vectors, victim, axis=0)
        self.entries.pop(victim)
```

Kullanımı:

```python
cache = SemanticCache(embed_fn=embed, threshold=0.85)
 
def ask(query):
    answer, score = cache.lookup(query)
    if answer is not None:
        print(f"✅ HIT (benzerlik={score:.3f})")
        return answer
 
    print(f"❌ MISS (en yakın={score:.3f}) → LLM çağrılıyor")
    answer = call_llm(query)
    cache.store(query, answer)
    return answer
```

### FAISS ile Ölçeklendirme

Yukarıdaki `self.vectors @ q` satırı 10 bin kayda kadar gayet iyi. Ötesinde FAISS'e geçmek gerekiyor:

```python
import faiss
import numpy as np

class FaissSemanticCache:
    def __init__(self, embed_fn, dim, threshold=0.85):
        self.embed_fn  = embed_fn
        self.threshold = threshold
        # IndexFlatIP = Inner Product. Normalize vektörlerde = cosine.
        # Milyonlarca kayıtta IndexHNSWFlat'a geç.
        self.index   = faiss.IndexFlatIP(dim)
        self.entries = []
 
    def lookup(self, query):
        if self.index.ntotal == 0:
            return None, 0.0
        q = self.embed_fn(query).astype("float32").reshape(1, -1)
        faiss.normalize_L2(q)
        scores, ids = self.index.search(q, k=1)
        best, idx = float(scores[0][0]), int(ids[0][0])
        if best >= self.threshold:
            return self.entries[idx]["answer"], best
        return None, best
 
    def store(self, query, answer):
        q = self.embed_fn(query).astype("float32").reshape(1, -1)
        faiss.normalize_L2(q)
        self.index.add(q)
        self.entries.append({"query": query, "answer": answer})
```

`IndexFlatIP` → `IndexHNSWFlat` geçişi tek satır. Mimari aynı kalıyor, sadece arama motoru değişiyor.

---

## 7. Embedding Modeli Seçimi — Türkçe Tarafı 🇹🇷

Cache kalitesini belirleyen **tek en önemli karar** embedding modeli. Kötü bir model, anlamca farklı soruları vektör uzayında yan yana koyar → yanlış hit → kullanıcıya yanlış cevap.

### Cache’in Kriterleri RAG’inkinden Farklı

Bu en sık atlanan nokta. RAG kurarken en yüksek kaliteyi kovalarsın, çünkü embedding’i doküman başına bir kez üretirsin. Cache’te ise **embedding üretimi her istekte ödediğin bir vergi** — hit’lerde de, miss’lerde de.

Bu farkın üç sonucu var:

1. **Küçük model burada bir avantaj:** Sıralamanın tepesindeki modeller genelde 500M+ parametreli ve 1024 boyutlu. Birkaç puan altındaki küçük kardeşleri 4–5 kat hızlı olabiliyor. Cache’te bu takas çoğu zaman küçük modelden yana.
2. **Uzun context özelliğinin hiçbir değeri yok:** Bazı modeller 8192 token’a kadar destek verir; bu, uzun doküman gömme senaryoları için tasarlanmış bir özellik. Senin cache’lediğin şey 20 kelimelik bir kullanıcı sorusu. 512 token fazlasıyla yeter.
3. **Vektör boyutu bellek maliyetin:** 1024 boyutlu bir model, 384 boyutluya göre cache’in RAM kullanımını neredeyse 3 katına çıkarır. Milyonlarca girdide bu ciddi bir fark.

### Türkçe’de Neye Bakmalı

- **İngilizce sıralamalara güvenme:** Bir modelin İngilizce skoru Türkçe performansını garanti etmiyor. Türkçe’nin eklemeli yapısı, çok dilli modellerin tokenizer’larında sorun çıkarabiliyor — aynı kelimenin çekimli halleri anlamsız parçalara bölünebiliyor.
- **Türkçe benchmark’lara bak:** [TR-MTEB](https://huggingface.co/trmteb), Türkçe cümle temsilleri için 26 veri seti ve 6 görev kategorisi içeren kapsamlı bir benchmark. Genel çok dilli sıralamalar için [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) canlı olarak güncelleniyor.
- **Prefix kurallarını atlama:** Bazı model aileleri (E5 gibi) girdilerin başına belirli bir önek bekler. Bunu atlamak kaliteyi sessizce düşürür. Semantic cache’te hem sorgu hem depolanan öğe “soru” olduğu için ikisinde de aynı öneki kullan.

### Ve Nihayetinde

Hiçbir benchmark senin verini bilmiyor. Sıralamalar başlangıç noktası; karar mercii **kendi soru setinde ölçtüğün yanlış hit oranı**.

**Pratik akış:** Küçük bir çok dilli modelle başla → kendi verinde ölç → yanlış hit oranı kabul edilemezse büyüğe çık. Ters yönde başlarsan hem gecikmeyi hem maliyeti gereksiz taşımış olursun.

---

## 8. Eşik Seçimi: Precision/Recall Dansı

İşte yazının en kritik bölümü.

$\tau$ eşiği tek bir sayı ama iki rakip hedefi aynı anda kontrol ediyor:

```text
τ düşük (0.75)                    τ yüksek (0.95)
   ├─ Çok hit ✅                      ├─ Az hit ❌
   ├─ Büyük tasarruf ✅                ├─ Az tasarruf ❌
   └─ Çok yanlış cevap ❌              └─ Neredeyse hiç yanlış cevap ✅
```

Ve embedding modelleri belirli hata türlerinde sistematik olarak zayıf. Türkçe örneklerle:

### ❌ Tuzak 1: Olumsuzlama

```text
A: "İade süresi 14 gün mü?"
B: "İade süresi 14 gün değil mi?"
→ cosine similarity ≈ 0.96
```

Embedding uzayında neredeyse aynı noktadalar. Peki bu gerçekten tehlikeli mi? **Cevabın nasıl yazıldığına bağlı** — ve bu ayrım çok az konuşuluyor.

Cache’teki cevap **tam cümle** ise:

```text
Cache: "Hayır, iade süresi 14 gün değil — 30 gündür."
 
A'ya döner  → doğru ✅
B'ye döner  → doğru ✅
```

Sorun yok. İki soru da aynı bilgiyi istiyordu, aynı cevabı aldı.

Ama cache’teki cevap **eksiltili** ise:

```text
Cache: "Evet."
 
A'ya döner  → "14 gün mü?" → "Evet"  ✅
B'ye döner  → "14 gün değil mi?" → "Evet"  ❌ tam tersini onayladı!
```

İşte gerçek mekanizma bu: **olumsuzlama, cevap eksiltili olduğunda tehlikeye dönüşür.** “Evet”, “Hayır”, “Doğru”, “Mevcut” gibi tek kelimelik cevaplar sorunun yönüne bağımlıdır — soru tersine dönünce cevap da anlamını tersine çevirir.

> **Kural**: Cache’e asla eksiltili cevap yazma. Her cevap, sorusu olmadan da tek başına doğru okunabilmeli. “Evet” değil, “Evet, kapıda ödeme mevcuttur” yaz.

### ❌ Tuzak 2: Varlık Değişimi

```text
A: "İstanbul'dan Ankara'ya kargo kaç günde gider?"
B: "Ankara'dan İstanbul'a kargo kaç günde gider?"
→ cosine similarity ≈ 0.98
```

Aynı kelimeler, ters yön. Çoğu senaryoda cevap aynı olur — ama bir kargo firması için olmayabilir.

Daha net bir örnek:

```text
A: "5000 TL'lik siparişte kargo bedava mı?"
B: "500 TL'lik siparişte kargo bedava mı?"
→ cosine similarity ≈ 0.97
```

Bir sıfır. Embedding modelleri sayılara karşı **kör denecek kadar duyarsız**.

### ❌ Tuzak 3: Zamana Bağlı Sorular

```text
"Bugün kampanya var mı?"
```

Bu soru cache’lenmemeli. Hiçbir eşik değeri seni bundan korumaz, çünkü problem benzerlik değil **tazelik**. Çözüm eşikte değil, politikada: bu tür sorguları cache’e hiç sokma.

### Nasıl Karar Veriyoruz?

Doğru yöntem tahmin etmek değil, **ölçmek**:

1. Geçmiş loglardan 200–500 çift soru çıkar
2. Elle etiketle: `1` (aynı niyet) veya `0` (farklı niyet / tuzak)
3. Farklı $\tau$ değerlerinde precision ve recall eğrilerini çiz
4. Ürünün risk toleransına göre eşiği belirle:
   - Destek botu (hata tolere edilebilir): $\tau \approx 0.82 - 0.86$
   - Hukuk / Finans / Sağlık botu (sıfır hata): $\tau \ge 0.93$ veya semantic cache kullanma

---

## 9. Üretimde Neler Ters Gider?

### 🔴 Kullanıcı İzolasyonu — En Tehlikelisi

```python
# ❌ Bu kod veri sızdırıyor:
cache.store("Siparişim ne zaman gelir?",
            "12345 numaralı siparişiniz yarın Kadıköy'e teslim edilecek.")
```

Ahmet’in sorusuna üretilen kişiselleştirilmiş cevap cache’e girdi. Mehmet aynı soruyu sorduğunda **Ahmet’in sipariş numarasını ve adresini** alacak.

Bu teorik bir risk değil, semantic cache’in en sık yapılan üretim hatası. Çözüm: cache anahtarını kullanıcı/kiracı bazında izole et:

```python
# Kullanıcı bazlı namespace
cache.lookup(query, namespace=f"user:{user_id}")
 
# Ya da daha iyisi: kişiselleştirilmiş cevapları hiç cache'leme
if response_contains_pii(answer):
    return answer  # cache'e yazma
```

**Genel kural:** Sadece *herkes için aynı olan* cevapları paylaşımlı cache’e koy. Kişiye özel her şey ya izole edilir ya da cache dışı bırakılır.

### 🟠 Bayatlama ve Invalidation

Ürün fiyatı değişti. Cache hâlâ eski fiyatı söylüyor.

- **TTL**: Her girdiye son kullanma tarihi ver. Fiyat sorularına 1 saat, politika sorularına 30 gün.
- **Olay bazlı temizleme**: Katalog güncellenince ilgili girdileri sil.
- **Sürüm etiketi**: Sistem prompt’un veya bilgi tabanın değişince cache sürümünü artır, eski girdiler otomatik geçersiz olsun.

Sistem prompt değişikliğinde cache’i temizlemeyi unutmak sinsi bir hatadır: model artık farklı davranıyordur ama cache eski kişiliğin cevaplarını dağıtmaya devam eder.

### 🟡 Çok Turlu Sohbet Problemi

```text
Kullanıcı: "iPhone 17 fiyatı ne kadar?"
Bot:       "95.000 TL"
Kullanıcı: "peki ya diğeri?"   ← tek başına anlamsız
```

*“peki ya diğeri?”* cümlesini tek başına embed edersen, tamamen alakasız bir bağlamdaki aynı cümleyle eşleşir.

Çözüm: cache anahtarını sadece son mesajdan değil, konuşma bağlamından üret. Ya sorguyu bağımsız hale getir (query rewriting: *“peki ya diğeri?”* → *“iPhone 17 Pro fiyatı ne kadar?”*), ya da son N mesajı embedding’e dahil et.

### 🟡 Eviction Politikası

Cache sonsuz büyüyemez. Ama LRU (en son kullanılan kalsın) semantic cache için çoğu zaman kötü bir seçim — nadir ama pahalı sorguları atar. LFU (en sık kullanılan kalsın) veya “hit sayısı $\times$ üretim maliyeti” gibi hibrit skorlar genelde daha iyi çalışır.

### 🟡 Cache Poisoning

Kullanıcı girdisiyle beslenen bir cache, kötü niyetli girdilerle zehirlenebilir. Modelden alınan hatalı bir cevap cache’e yazıldıysa, artık o hata **kalıcı** ve **yüzlerce kullanıcıya** dağıtılıyor. Cache’e yazmadan önce basit sağlık kontrolleri (boş cevap mı, hata mesajı mı, aşırı kısa mı) koymak ucuz bir sigorta.

---

## 10. Üç Cache’i Karıştırmayalım

Bu üçü sürekli birbirine karıştırılıyor. Halbuki tamamen farklı katmanlarda, farklı şeyler için çalışıyorlar:

![Cache Comparison Matrix](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*7L5E5_mCosz5D65h5zE1CQ.png)

| Özellik | KV Cache | Prompt Cache | Semantic Cache |
|:---|:---|:---|:---|
| **Nerede Yaşar?** | Model içinde (GPU VRAM) | Model inference motoru | Dış katman (Redis / FAISS / DB) |
| **Eşleşme Tipi** | Attention state reuse | Exact prefix match | Semantic (vektör benzerliği) |
| **Model Çalışır mı?** | Evet (üretim hızlanır) | Evet (prefill hızlanır) | **Hayır (model hiç çağrılmaz)** |
| **Tasarruf Türü** | GPU compute / Latency | Token / Prefill cost | Tam API maliyeti + Sıfır inference |
| **Hata / Sapma Riski** | Sıfır (deterministik) | Sıfır (deterministik) | **Var ($\tau$ eşiğine bağlı)** |

Son satır kritik: tabloda yanlış cevap riski olan tek satır semantic cache. KV cache ve prompt cache matematiksel olarak aynı sonucu üretir. Semantic cache ise bir **tahminde bulunur** — ve tahminler yanılabilir.

Bu üçü birbirinin alternatifi değil, **birlikte** kullanılır:

```text
İstek gelir
   │
   ▼
[Semantic Cache]  ── hit ──▶ dön (LLM'e hiç gitmedik)
   │ miss
   ▼
[Prompt Cache]    ── prefix hit ──▶ prefill'i atla
   │
   ▼
[KV Cache]        ── üretim boyunca token token
   │
   ▼
Cevap
```

---

## 11. Ölçüm: Neye Bakmalı?

Semantic cache’i “kurdum, çalışıyor” diye bırakırsan sessizce yanlış cevap dağıtan bir sisteme dönüşebilir. İzlenmesi gereken metrikler:

![Metrics Overview](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*O1T6dPaVA2tEH9YBQXsEhw.png)

| Metrik | Açıklama | Hedef / Eşik |
|:---|:---|:---|
| **Hit Ratio ($h$)** | Toplam isteklerin ne kadarı cache'ten döndü | %30 – %60 |
| **False Hit Rate** | Cache'ten dönüp kullanıcıya yanlış bilgi veren oran | < %0.5 (ürüne göre) |
| **P99 Embedding Latency** | Arama öncesi embed süresi | < 15–20 ms |
| **Cost Savings Ratio** | Cache sonrası fatura düşüşü | %25 – %50 |
| **Similarity Histogram** | Skorların dağılımı (overlap analizi) | Çift tepe (bimodal) ayrışma |

Histogram analizi kritik: benzerlik skorlarının histogramını çizdiğinde:

![Similarity Histogram](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*9ICp3p4K1oCR0nIuyylQqQ.png)

Tuzaklar (kırmızı) parafrazların (mavi) tam içine karışmış durumda ise (0.78–0.98 arası çakışma), eşik ayarından önce embedding modeli veya cache tasarımı gözden geçirilmelidir.

**False hit rate nasıl ölçülür?** Hit’lerin küçük bir yüzdesini (%1–5) rastgele seçip yine de LLM’e sor, iki cevabı karşılaştır (**Shadow Testing**).

---

## 12. Sonuç ve 6 Uygulama Adımı

- Exact-match cache doğal dilde işe yaramaz; Türkçe’nin eklemeli yapısı bunu daha da zorlaştırır.
- Semantic cache, string yerine **anlamı** anahtar olarak kullanır.
- Maliyet açısından neredeyse her zaman kârlı — binde bir hit bile yeter.
- **Ama tek bir sayıya ($\tau$) bağlı bir tahmin sistemi**, ve tahminler yanılır.
- En tehlikeli hata mimaridir: kişiselleştirilmiş cevapları paylaşımlı cache’e koymak.
- KV cache, prompt cache ve semantic cache farklı katmanlarda, birlikte çalışır.

### Bu Hafta Uygulayabileceğin 6 Adım

1. **Ölç, sonra başla:** Son 1000 sorunun loglarını al. Kaçı parafraz? Hit potansiyelin yoksa cache’e hiç girme.
2. **Küçük bir çok dilli embedding modeliyle kur:** 384 boyut CPU’da rahat çalışır. Büyük modele ihtiyacın olduğunu *ölçtükten sonra* geç.
3. **Cevapları tam cümle yaz:** Sistem prompt’una ekle: *“Cevapların sorusuz da anlaşılır olsun, ‘Evet/Hayır’ ile başlama.”* Bu tek satır olumsuzlama tuzaklarının çoğunu çözer.
4. **Kişiselleştirilmiş cevapları cache’e hiç sokma:** Sipariş numarası, adres, bakiye içeren hiçbir cevap paylaşımlı cache’e girmesin.
5. **Sayı/varlık kontrolü ekle:** Eşiği geçen adayda iki sorunun sayıları ve özel isimleri eşleşmiyorsa hit’i reddet.
6. **İlk hafta %5 shadow test yap:** Hit’lerin %5'ini yine de LLM’e sor, iki cevabı karşılaştır.
