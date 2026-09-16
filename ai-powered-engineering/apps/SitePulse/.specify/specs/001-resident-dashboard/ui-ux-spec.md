# UI/UX Specification: Resident Mobile Dashboard (M3)

> **Feature ID:** SPEC-001  
> **Platform:** Android (Jetpack Compose)  
> **Theme:** Material Design 3  

---

## 1. Screen Architecture & Ergonomics
- **Target Device Resolution:** 412 x 915 dp (Google Pixel standard)
- **Ergonomic Zone:** Crucial interactive elements (Pay button, Quick Action items) are placed within the thumb-reach zone (lower 60% of viewport).

---

## 2. Component Layout Hierarchy

```
┌────────────────────────────────────────────────────────┐
│ [TopBar]  🏢 Begonya Sitesi - A Blok D:14      🔔 (2)  │
├────────────────────────────────────────────────────────┤
│ [Hero Balance Card]                                    │
│   Toplam Güncel Borç                                   │
│   ₺ 1.423,33                                           │
│   Son Ödeme: 15 Eylül 2026 (10 Gün Gecikmede)          │
│   [ 💳 Hemen Öde (Primary Filled Button) ]             │
├────────────────────────────────────────────────────────┤
│ [Hızlı İşlemler - 4 Grid Cards]                        │
│   [ 🔧 Arıza Bildir ]      [ ⚡ Sayaç Endeks ]          │
│   [ 🎾 Rezervasyon  ]      [ 📢 Duyurular    ]          │
├────────────────────────────────────────────────────────┤
│ [Son Duyuru Banner]                                    │
│   ⚠️ 18 Eylül Çarşamba Su Kesintisi Hakkında           │
│   "Belediye ana boru hattı yenileme çalışması..."      │
├────────────────────────────────────────────────────────┤
│ [Bottom Navigation Bar]                                │
│   [🏠 Ana Sayfa]  [📋 Aidatlar]  [🛠 Talepler]  [👤 Profil]│
└────────────────────────────────────────────────────────┘
```

---

## 3. UI State Definitions
1. **Loading State:** Shimmering placeholder boxes for Hero Card and Quick Action circles.
2. **Success State (Active Debt):** Gradient card with terracotta accent badge for overdue interest, active primary "Hemen Öde" button.
3. **Success State (Zero Debt):** Soft teal/green surface card with checkmark badge and "Borcunuz Bulunmamaktadır".
4. **Offline / Cache State:** Small amber chip in the TopBar: *"Çevrimdışı (Son senkr: 10:45)"*.
