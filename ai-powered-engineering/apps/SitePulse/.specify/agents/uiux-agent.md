# UI/UX Architect Agent Specification

> **Agent Name:** Mobile Design & Ergonomics Specialist  
> **Target Surface:** Android (Jetpack Compose, Material 3)  
> **Output Artifacts:** `ui-ux-spec.md`, Interactive HTML Previews (`prototype.html`), Design Tokens  

---

## 1. Role & Objectives
The UI/UX Agent translates functional requirements into responsive, accessible, and delightful Android mobile experiences. It enforces Material 3 guidelines and produces living visual previews before Kotlin code is written.

## 2. Design System Tokens (SitePulse Theme)

### Color Palette (Material 3 Dynamic Theming)
- **Primary:** `#00629E` (Deep Aegean Blue - Trust & Authority)
- **OnPrimary:** `#FFFFFF`
- **PrimaryContainer:** `#CFE5FF`
- **Secondary:** `#006874` (Teal Slate - Financial Balance)
- **Tertiary:** `#9C4146` (Terracotta Alert - Overdue notices)
- **Background:** `#F8F9FA` (Soft Light Gray)
- **Surface:** `#FFFFFF`
- **SurfaceVariant:** `#E1E2EC`

### Typography (Inter / Roboto)
- **Display Large:** 32sp / 40sp line height (Total balance amount)
- **Headline Medium:** 20sp / 26sp line height (Section titles)
- **Body Medium:** 14sp / 20sp line height (Descriptions, receipts)
- **Label Large:** 14sp / 20sp (Button text, badge indicators)

## 3. Required Outputs per Screen
1. **Layout Hierarchy (Composables tree):**
   - TopAppBar (Site/Daire Switcher + Notifications)
   - Hero Card (Outstanding dues + quick pay CTA)
   - Quick Action Grid (Arıza Bildir, Sayaç Gir, Rezervasyon, İletişim)
   - Recent Feed (Duyurular & Belgeler)
   - BottomNavigationBar (Ana Sayfa, Aidat, Talepler, Profil)
2. **Interactive HTML Prototype:**
   - Every feature spec must be accompanied by an interactive `prototype.html` rendered inside a 412x915dp mobile frame for browser-based visual inspection.
