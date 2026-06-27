---
type: Article
title: "Hap Bilgi 15: AI Agent Mimarisi — Bir Yapay Zekâ Ajanı Nasıl Çalışır?"
description: "Son dönemde teknoloji dünyasının en popüler kavramlarından biri **AI Agent**."
timestamp: 2026-06-14T00:00:00Z
---

# Hap Bilgi 15: AI Agent Mimarisi — Bir Yapay Zekâ Ajanı Nasıl Çalışır?

> **Seri**: Developer Hap Bilgi — Bölüm 15  
> **Yayın Tarihi**: Jun 10, 2026 · 5 dakika

![AI Agent Mimarisi — Altı temel bileşen](images/llm-agents-ai-agent-architecture.png)

---

Son dönemde teknoloji dünyasının en popüler kavramlarından biri **AI Agent**.

Peki aslında bir agent nedir?

En basit tanımıyla bir AI Agent, bir hedefe ulaşana kadar **düşünen, plan yapan, araç kullanan ve elde ettiği sonuçlara göre tekrar karar veren** otonom bir sistemdir.

Klasik chatbotlar yalnızca metin üretirken, AI Agent'lar gerektiğinde web araması yapabilir, kod çalıştırabilir, API çağırabilir veya dosya okuyabilir. Üstelik bunların hepsini belirli bir plan doğrultusunda gerçekleştirebilir.

Modern bir AI Agent mimarisi temel olarak **altı ana bileşenden** oluşur.

---

## 1. Brain (Beyin)

Her agent'ın merkezinde bir **Large Language Model (LLM)** bulunur.

Bu katman:

- Kullanıcının isteğini analiz eder.
- Mevcut durumu değerlendirir.
- Sonraki adımın ne olacağına karar verir.
- Gerekirse yeni bir plan oluşturur.

Buradaki en önemli fark şudur:

> **Chatbot metin üretir. AI Agent ise karar üretir.**

Model artık sadece cevap yazan bir sistem değildir; hangi işlemin yapılacağına karar veren bir **orkestratöre** dönüşür.

```
Kullanıcı
    ↓
İsteği Analiz Et
    ↓
Karar Ver
    ↓
Plan Oluştur
```

---

## 2. Planning (Planlama)

Gerçek hayattaki problemler çoğunlukla tek adımda çözülemez.

Bu nedenle agent önce hedefi daha küçük görevlere ayırır.

**Örneğin:**

```
"Hava durumunu öğren"
    ↓
Konumu belirle
    ↓
API çağır
    ↓
Sonucu işle
    ↓
Cevabı oluştur
```

Bu süreçte kullanılan popüler planlama teknikleri şunlardır:

- **Chain of Thought** (CoT)
- **Tree of Thoughts** (ToT)
- **ReAct** (Reasoning + Acting)
- **Reflexion**

Başarılı bir planlama mekanizması, agent'ın doğruluğunu ve başarısını doğrudan artırır.

---

## 3. Tools (Araçlar)

Bir LLM tek başına dış dünya ile iletişim kuramaz:

- İnternete erişemez.
- Kod çalıştıramaz.
- Veritabanına bağlanamaz.
- Dosya sistemi üzerinde işlem yapamaz.

Bu işlemler **Tool Calling** sayesinde gerçekleştirilir.

```
LLM
    ↓
Tool Call
    ↓
API / Browser / Python / SQL
    ↓
Sonuç
    ↓
LLM
```

Sık kullanılan araçlar:

- Web Search
- REST API
- Python
- File System
- SQL Database
- Browser Automation
- Function Calling
- MCP Server

> Aslında modern AI Agent'ların en büyük gücü yalnızca kullandıkları model değil, sahip oldukları **araç ekosistemidir**.

---

## 4. Memory (Hafıza)

Bir agent'ın her konuşmaya sıfırdan başlaması verimsizdir.

Bu nedenle iki farklı hafıza mekanizması kullanılır.

### Short-Term Memory (Kısa Süreli Hafıza)

Context Window içerisinde bulunan aktif konuşmadır.

```
User
    ↓
Conversation Context
    ↓
LLM
```

Konuşma uzadığında eski içerikler özetlenerek bağlam korunmaya çalışılır.

### Long-Term Memory (Uzun Süreli Hafıza)

Kalıcı bilgiler burada saklanır:

- Kullanıcı tercihleri
- Dokümanlar
- Knowledge Base
- Vector Database
- RAG sistemi
- Kurumsal veri kaynakları

Agent ihtiyaç duyduğunda bu bilgileri tekrar çağırabilir ve önceki deneyimlerinden faydalanabilir.

---

## 5. Agent Loop (Karar Döngüsü)

AI Agent'ı klasik chatbotlardan ayıran **en önemli özellik** budur.

Agent tek seferlik cevap üretmez. Hedef tamamlanıncaya kadar sürekli karar verir.

```
Durumu Algıla
    ↓
Düşün
    ↓
Planla
    ↓
Araç Kullan
    ↓
Sonucu Değerlendir
    ↓
Görev tamamlandı mı?
    ├── Hayır → Döngüye devam et
    └── Evet  → Final cevabı üret
```

> Bu nedenle bir AI Agent'ı aslında **akıllı bir `while` döngüsü** olarak düşünebiliriz.

---

## 6. Guardrails (Kontrol ve Güvenlik Katmanı)

Bir agent'a ne kadar fazla yetki verirseniz, kontrol mekanizmaları da o kadar önemli hale gelir.

Production sistemlerde her aksiyon belirli güvenlik katmanlarından geçer.

Başlıca guardrail örnekleri:

- Yetki kontrolü
- Scope doğrulaması
- İnsan onayı (Human in the Loop)
- Çıktı doğrulama
- Token limiti
- Maliyet limiti
- Sandbox ortamı
- Hassas veri filtreleme

Yanlış yapılandırılmış bir agent gereksiz maliyet oluşturabilir, hatalı API çağrıları yapabilir veya kritik sistemlerde beklenmeyen işlemler gerçekleştirebilir.

> Bu nedenle kurumsal AI sistemlerinde guardrail katmanı çoğu zaman **model kadar önemlidir**.

---

## Özet

Başarılı bir AI Agent yalnızca güçlü bir LLM'den oluşmaz.

Gerçek güç; planlama, araç kullanımı, hafıza yönetimi ve güvenlik mekanizmalarının birlikte çalışmasından gelir.

| Bileşen | Görevi |
|:---|:---|
| **Brain** | Karar verir |
| **Planning** | Problemi adımlara böler |
| **Tools** | Dış dünya ile etkileşim kurar |
| **Memory** | Bilgiyi saklar ve geri çağırır |
| **Agent Loop** | Görev tamamlanana kadar çalışır |
| **Guardrails** | Güvenliği ve kontrolü sağlar |

Modern bir AI Agent'ı özetleyen formül:

```
AI Agent = LLM + Planning + Tools + Memory + Loop + Guardrails
```

Gelecekte fark yaratacak sistemler yalnızca daha büyük modeller kullananlar değil; bu bileşenleri doğru şekilde bir araya getirip yöneten mimariler olacaktır.

---

> **Hap Bilgi**  
> *"Chatbot size cevap verir. AI Agent ise hedefe ulaşmak için karar alır, araç kullanır, sonucu değerlendirir ve gerekirse tekrar dener."*
>
> İşte yapay zekâ dünyasındaki en büyük paradigma değişimi tam olarak budur.

---

## Kaynaklar

- [LLM Powered Autonomous Agents — Lilian Weng](https://lilianweng.github.io/posts/2023-06-23-agent/)
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
- [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)
- [Model Context Protocol (MCP) — Resmi Dokümantasyon](https://modelcontextprotocol.io/introduction)
- [Microsoft AutoGen Framework](https://microsoft.github.io/autogen/)
- [ByteByteGo — The Anatomy of an AI Agent](https://blog.bytebytego.com/p/ep215-the-anatomy-of-an-ai-agent)
