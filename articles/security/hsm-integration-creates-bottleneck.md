---
type: Article
title: "HSM Integration Creates Architectural Bottlenecks — and the Design Cost of Cryptographic Operations"
description: "HSM, modern ödeme mimarisinin en büyük çelişkisidir. Sistemin güvenliğini fiilen garanti eden tek bileşendir; ve tam olarak bu yüzden sistemi en fazla kısıtlayan bileşen de odur. Diğer her bileşeni..."
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# HSM Integration Creates Architectural Bottlenecks — and the Design Cost of Cryptographic Operations

> **Author**: Umut Akbulut · **Published**: Mar 16, 2026 · **7 min read**
> **Original**: [Medium Article](https://medium.com/@umutt.akbulut/hsm-entegrasyonu-neden-mimari-darbo%C4%9Faz-yarat%C4%B1r-ve-kriptografik-operasyonlar%C4%B1n-tasar%C4%B1m-bedeli-6bd6d9e07764)

---

![HSM Bottleneck Overview](images/hsm-integration-bottleneck-overview.png)

---

HSM, modern ödeme mimarisinin en büyük çelişkisidir. Sistemin güvenliğini fiilen garanti eden tek bileşendir; ve tam olarak bu yüzden sistemi en fazla kısıtlayan bileşen de odur. Diğer her bileşeni yatayda büyütebilirsin — uygulama sunucusunu, veritabanını, mesaj kuyruğunu, event stream'i. HSM'i büyütmek başka bir prosedür gerektirir. Ve bu asimetri, yüksek hacimli ödeme sistemlerinde en çok görmezden gelinen mimari gerçeklerden biridir.

`Hardware Security Module`, adından da anlaşıldığı üzere donanımdır. Yazılım gibi container'a koyamazsın, Kubernetes üzerinde replika sayısını artıramazsın, cloud autoscaling politikası yazamazsın. Kapasitesini artırmak istediğinde yeni bir cihaz satın alıyorsun, rack'e takıyorsun, `key ceremony` yapıyorsun, sisteme tanıtıyorsun. Bu süreç haftalar alıyor. Yazılımda hiçbir bileşen böyle çalışmıyor. Bu gerçekliğin mimari tasarım üzerindeki baskısı, ödeme sistemleri kurulurken gerektiği kadar içselleştirilmiyor.

---

## What HSM Actually Does

Bunun nedenini anlamak için HSM'in tam olarak ne iş yaptığını görmek gerekiyor. Bir kart işleminde kriptografik operasyon sayısı şaşırtıcı derecede yüksek. ATM'den PIN giren bir müşteri düşün: terminal, PIN'i şifreli bir blok olarak gönderiyor. Bu blok terminal'in anahtarıyla şifrelenmiş. Banka tarafı bu `PIN block`'u kendi anahtarına çevirmek zorunda — buna `PIN block translation` deniyor, Thales payShield terminolojisinde `CC` komutu. Sonra doğrulamanın kendisi geliyor; `EA` ya da `EB` komutu, işlem başına 1–3 milisaniye. Bu iki operasyon birbirini izlediğinde tek bir ATM işleminde HSM, kritik yolun içinde en az iki kez yer alıyor. Bu rakam senaryo karmaşıklaştıkça artıyor.

Chip kartlarda tablo daha da derin. EMV kriptogramı — müşteri terminaline kartını taktığında kart içinde üretilen `ARQC` ya da `TC` — issuer tarafında doğrulanmak zorunda. Bu doğrulama `KQ` komutuyla yapılıyor ve hesap yoğunluğu diğer komutlardan belirgin biçimde yüksek. RSA ya da ECC tabanlı kriptografiye giren senaryolarda 5–15 milisaniye sürebiliyor; yük altında bu değer daha da yukarı çekiyor. Türkiye'de chip kart penetrasyonu son yıllarda %95 bandına yerleştiğine göre, her authorization akışında `KQ` komutunun havuz tüketimindeki payı küçümsenemez. Kart-yoksuz işlemlerde ise `CVV2` doğrulaması `CY` komutuyla geliyor; görece hafif ama her e-ticaret işleminde geçiyor. Tokenizasyon doğrulaması `Token Vault`'a gidip HSM'e dokunuyor. `3D Secure` akışındaki kriptografik işlemler yine HSM altyapısından besleniyor. Sistemde HSM'i bypass eden kriptografik bir kritik yol yok.

---

## Capacity: Simple Math, Brutal Reality

Bu tablo kapasiteyi basit bir matematik sorusuna dönüştürüyor. Bir Thales `payShield 9000` tipik yapılandırmada **100 eş zamanlı bağlantıyı** destekliyor. `payShield 10K` ile bu **1.000'e** çıkabiliyor ama bu model henüz her kurumda yaygınlaşmış değil. Günde bir milyon işlem yapan bir sistem, saatte yaklaşık 42.000 işlem demek. Trafik gün içinde hiç homojen dağılmıyor — öğleden sonra 2–4 ve akşam 7–9 arası yoğunluk zirvelerinde bu rakam iki-üç katına çıkabiliyor. Saniyede 300–500 işleme geliyor; her işlemde HSM iki-üç kez çağrılıyor. Her çağrı ortalama 2–10 milisaniye, yük altında 50 milisaniyeye kadar gidiyor. 100 bağlantıyla bu denklemi yönetmek, bağlantı havuzu yönetiminin yanlış tasarlandığı sistemlerde mümkün değil.

---

## Connection Pool Exhaustion

Bağlantı havuzu dolduğunda zincirleme bir süreç başlıyor. Yeni gelen istekler kuyrukta bekliyor, kuyruk büyüdükçe `latency` artıyor, authorization süresi 200–300 milisaniyeyi aştığında kart ağı `timeout` üretiyor ve işlem `system error` ile reddedilebiliyor. Müşteri perspektifinden kart çalışmıyor. Sistem loglarında ise herhangi bir uygulama hatası görünmüyor — çünkü sorun uygulama katmanında değil. `HSM connection pool exhaustion`, monitoring altyapısı bu boyutu izlemiyorsa teşhis edilmesi saatler alan bir arıza türü.

---

## Design Principle: Isolate by Operation Type

Buradan çıkan tasarım ilkesi net: HSM'e yapılan çağrıları operasyon tipine göre izole etmek zorunlu. `PIN verification`, `CVV` doğrulama, `EMV` kriptogram doğrulama gibi gerçek zamanlı authorization operasyonları, kart saklama sırasındaki `PAN` şifreleme ya da batch anahtar güncelleme operasyonlarıyla aynı bağlantı havuzunu paylaşmamalı. Batch bir iş gecenin sessiz saatinde toplu PAN şifrelemesi yapıyorsa ve havuzu tüketiyorsa, aynı anda gelen sabah yoğunluğunun authorization istekleri timeout alır. Ayrı havuzlar, ayrı HSM partition ya da ayrı fiziksel cihaz — seçenek kurumun altyapısına göre değişir, ama izolasyon şarttır.

Bu izolasyonun yanına bir şey daha eklenmeli: HSM'in kendisini kara kutu olarak bırakmamak. Bağlantı havuzu doluluğu, komut başına ortalama ve **99. percentile latency**, cihaz CPU kullanımı — bunların gerçek zamanlı izlenmesi olmadan bir anomali yaşandığında "HSM mi yavaş, network mi, uygulama mı?" sorusu dakikalar değil saatler alır.

---

## The Synchronous Call Trap

Yazılım katmanındaki bu zorunlulukların ötesinde, HSM'i asıl mimari baskı altına sokan şey senkron çağrıların kritik yoldan çıkarılamamasıdır. Yazılım sistemlerinde asenkronizasyon tasarımın temel aracı; kritik yolu kısa tut, ağır işi arka plana at. Ödeme akışında bunu tam anlamıyla yapamazsın. Müşteri PIN girmiş, terminal bekliyor, kart ağı bekliyor, yanıt gelmesi gerekiyor. Kriptogram doğrulanmadan authorization kararı verilemez. Senkron çağrı bu akışta zorunlu.

Bu zorunluluk, uygulama katmanını ne kadar iyi asenkron tasarlasan da HSM latency'sinin authorization toplam süresine direkt eklendiği anlamına geliyor. Yük altında HSM süresi 50 milisaniyeye çıktığında, authorization hedefi olan 200 milisaniyenin dörtte birini tek başına tüketiyor. Diğer bileşenleri optimize ederek bu katkıyı seyreltilebilirsin ama sıfıra indiremezsin.

---

## Caching vs. PCI-DSS

Bazı mimarlar bu sorunu önbellekle çözmeye çalışıyor. Anahtarları ya da bazı hesaplamaları bellekte tutarsan HSM'e gitme sıklığı azalır. Bu yaklaşım cazip görünüyor ama `PCI-DSS` Gereksinim 3.5 ve 3.6 ile doğrudan çatışıyor. Aktif çalışma anahtarlarının şifresiz biçimde bellekte tutulması standart dışı kabul ediliyor. Önbellekleme yapılacaksa çok dar bir pencerede, şifreli biçimde, kısa `TTL` ile yapılabilir. Ama bu da sorunun gerçek çözümü değil, görünürlüğünü azaltmak. Ve denetim anında bu önbelleğin varlığı soruları beraberinde getiriyor.

---

## Key Hierarchy

Anahtar hiyerarşisi meselesi HSM'in mimariye neden bu kadar derinden işlediğini açıklıyor. Ödeme sistemlerinde kriptografik anahtar tek katmanlı değil:

| Layer | Key | Purpose |
|-------|-----|---------|
| 1 (Top) | `LMK` (Local Master Key) | HSM'in fabrika anahtarı, cihazın içinde yaşıyor, dışarı hiçbir zaman çıkmıyor |
| 2 | `ZMK` (Zone Master Key) | İki kurum arasında güvenli anahtar değişimi |
| 3 | `ZPK` (Zone PIN Key) | PIN block şifreleme |
| 3 | `CVK` (Card Verification Key) | Kart doğrulama |
| 3 | `PVK` (PIN Verification Key) | PIN doğrulama |
| 3 | `EMV` Key Set | EMV kriptogram işlemleri |

Her kriptografik operasyon bu hiyerarşinin belirli bir katmanını kullanıyor ve her katman HSM'in farklı bir bölümünde yaşıyor. Yeni bir kart ağıyla entegrasyon kurulduğunda o ağla `ZMK` değişimi yapılması gerekiyor. Bu değişim fiziksel ya da elektronik protokolle gerçekleşiyor. Anahtarlar yüklenirken HSM'de slot açılıyor. Slot sayısı sınırlı. On yıl önce tasarlanan bir cihazda bugün altı farklı ağla entegrasyon varsa, o cihazın kapasitesi zorlama noktasına yaklaşmış olabilir.

---

## LMK Ceremony: Not a Software Deployment

`LMK` değişimi ise bambaşka bir operasyonel gerçeklik. HSM cihazı yaşlandığında ya da güvenlik politikası gereği döngüsel anahtar yenileme yapılması gerektiğinde `LMK ceremony` başlıyor. Bu prosedür birden fazla anahtar sahibinin fiziksel varlığını gerektiriyor — akıllı kart ya da anahtar parçaları birleştiriliyor, denetim kaydı tutuluyor, prosedür belgeleniyor. Bir yazılım deployment değil bu; organizasyonel bir güvenlik ritüeli. Ve bu prosedür sırasında HSM ya tamamen kapalı ya da kısıtlı modda çalışıyor. Aktif bir ödeme sisteminde `LMK ceremony`'sini ne zaman yapacaksın? Gecenin ölü saatlerinde, haftasonu sabahı, kısa bir bakım penceresinde. Ve her şey planlandığı gibi gitmeyebilir. Bu gerçeklik, HSM yüksek erişilebilirliğinin yazılımdaki `HA` anlayışından çok farklı düşünülmesi gerektiğini gösteriyor.

---

## Active-Passive vs. Active-Active HSM

`Active-passive` HSM mimarisi yaygın: bir birincil, bir yedek. Birincil arızalandığında yedek devreye giriyor. Ama bu geçişin saniyeler içinde otomatik gerçekleşmesi için iki cihazın da aynı `LMK`'ya sahip olması gerekiyor; senkronizasyon fiziksel token transfer ya da elektronik key sync protokolüyle sağlanıyor.

`Active-active` konfigürasyon mümkün ama karmaşık. Her iki HSM da aktif işliyor, yük paylaşılıyor, `LMK` tutarlılığı sürekli doğrulanıyor. Bir HSM güncelleme alırken ya da kısa bakıma girerken diğeri tüm yükü taşıyabiliyor olmalı.

`Network partition` bu tabloya eklenince başka bir soru geliyor: uygulama katmanı ikiye ayrıldığında hangi taraf hangi HSM'i kullanacak? `PIN block translation` bir HSM'den gelen anahtarla başladıysa aynı HSM'de bitmeli — başka bir cihaza geçilirse işlem baştan yapılmalı. Bu durumu yöneten bir routing mantığı gerekiyor ve bu mantığın `failover` senaryolarında da tutarlı çalışması şart.

---

## Cloud HSM: Latency vs. Operational Simplicity

Bulut ortamlarında tablo farklı bir yere oturuyor. `AWS CloudHSM`, `Azure Dedicated HSM` gibi hizmetler fiziksel HSM'i yönetilen formda sunuyor. Kapasite artırmak daha az prosedürel sürtünme içeriyor, `key ceremony`'nin bir kısmı servis sağlayıcının sorumluluğuna giriyor. Ama latency değişiyor: veri merkezindeki yerel HSM'e yüz mikrosaniye seviyesinde erişim sağlanabilirken, cloud HSM'e erişim milisaniye mertebesine taşıyor. Bu fark, saniyede yüzlerce authorization işleyen sistemlerde yük altında toplamda hissedilen bir değer. Yönetimsel kolaylık ile latency optimizasyonu arasındaki bu denge, kurumun işlem hacmine ve latency hedeflerine göre net biçimde modellenmeden karar verilemez.

---

## Mobile Wallet & Tokenization: The Hidden Traffic

Mobile wallet ve tokenizasyon entegrasyonunun HSM üzerindeki etkisi çoğu kapasite planlamasında gözden kaçıyor. `Apple Pay` ve `Google Pay`'de kullanılan `Device Account Token` (`DPAN`) — kart ağı tarafından üretilip cihaza provision ediliyor. Issuer'ın bu token'ı kabul etmesi, kendi sisteminde doğrulaması ve token ile gerçek `PAN` arasındaki eşleştirmeyi güvenli tutması gerekiyor. Bu eşleştirme veri tabanında düz metin duramaz. `Token Vault` HSM anahtarlarıyla korunuyor ve her token doğrulaması Token Vault üzerinden HSM'e dokunuyor. Contactless ödeme ve mobile wallet kullanımı artıkça bu dokunma sayısı artıyor. Kapasite planlaması bugünkü hacim üzerine değil, üç yıl sonraki wallet penetrasyonu baz alınarak yapılmalı. Bu öngörüyü yapmak, yeni bir HSM cihazının temin ve entegrasyon süresinin yazılım deployment'tan çok daha uzun olduğunu bilerek yapmak demek.

---

## Software HSM: Scaling Solution or Compliance Gap?

Software HSM'i bu tablonun alternatifi olarak değerlendirenlere şu söylenebilir: ölçekleme problemi gerçekten ortadan kalkıyor — container çoğaltılabiliyor. Ama `PCI-DSS` açısından software HSM, hardware HSM ile eşdeğer kabul edilmiyor. Fiziksel güvenlik katmanı yok: `side-channel` saldırıları, bellek dökümü, hypervisor erişimi gibi vektörler risk taşıyor. Bu yüzden software HSM test ortamlarında ve PCI kapsamı dışındaki kriptografik operasyonlarda kullanılıyor; production PIN işlemlerinde sektör standardı hâlâ fiziksel donanım.

`P2PE` (Point-to-Point Encryption) farklı bir açıdan yaklaşıyor: terminal kart verisini kendi içinde şifreliyor, `PAN` hiçbir zaman şifresiz tüccar ağına girmiyor. PCI scope'unu daraltıyor. Ama şifre çözme işlemi yine HSM'de yapılıyor; bu sefer tüccar tarafında değil, acquirer ya da payment gateway tarafında. Yük HSM'den kalkmıyor, yer değiştiriyor.

---

## Post-Quantum Cryptography: The Looming Tension

Post-quantum kriptografi yakın vadede bu mimari üzerine başka bir gerilim katıyor. `Shor` algoritması, yeterli kapasitede bir kuantum bilgisayarla mevcut RSA ve ECC altyapısını kırabilir. `NIST` 2024'te post-quantum standartlarını yayımladı; `CRYSTALS-Kyber` anahtar kapsülleme için, `CRYSTALS-Dilithium` dijital imza için öne çıkan algoritmalar. Mevcut HSM cihazları bu algoritmalar için henüz geniş çaplı destek sunmuyor. Ama geçiş planlaması bugün yapılmalı çünkü kriptografik algoritma seçimi sistemin her katmanında — protokol tanımlarında, kart kişiselleştirme altyapısında, anahtar hiyerarşisinin tasarımında — iz bırakıyor. Bu izleri değiştirmek yıllarca süren bir süreç.

---

## Summary for Architects

Tüm bu tablonun mimarlar için özeti şu: HSM darboğazını tamamen ortadan kaldırmak mümkün değil. Mümkün olan onu erken görmek, kapasite planlamasına dahil etmek, operasyon tiplerini izole etmek, sistemin HSM arızası ya da bakımı sırasında öngörülebilir biçimde davranmasını tasarlamak ve kriptografik operasyonların tam olarak hangi yoldan geçtiğini mimari modelin içinde tutmak.

Çoğu ödeme sistemi mimarisi uygulama katmanını detaylıca tasarlıyor, HSM katmanını güvenlik ekibinin meselesi olarak bırakıyor. Bu iki dünyanın kesiştiği yerde — authorization `SLA`'sı, bağlantı havuzu kapasitesi, `key ceremony` zamanlaması, tokenizasyon büyümesi — production'daki en ağır darboğazlar sessizce birikip gün yüzüne çıkıyor.

---

## Key Takeaways

1. **HSM ölçeklenemez** — yatay büyüme yok, kapasite artışı haftalar sürer.
2. **Senkron çağrılar kritik yola doğrudan eklenir** — HSM latency'si authorization SLA'sını tüketir.
3. **Operasyon tiplerini izole et** — real-time ve batch işlemler aynı havuzu paylaşmamalı.
4. **PCI-DSS önbelleklemeyi kısıtlar** — anahtarlar şifresiz bellekte tutulamaz.
5. **LMK ceremony bir deployment değildir** — organizasyonel güvenlik ritüelidir, planlama ister.
6. **Cloud HSM latency trade-off** — yönetim kolaylığı milisaniye maliyetiyle gelir.
7. **Post-quantum geçişini bugün planla** — algoritma değişimi yıllar sürer.

---

> **Original**: [Medium Article](https://medium.com/@umutt.akbulut/hsm-entegrasyonu-neden-mimari-darbo%C4%9Faz-yarat%C4%B1r-ve-kriptografik-operasyonlar%C4%B1n-tasar%C4%B1m-bedeli-6bd6d9e07764)