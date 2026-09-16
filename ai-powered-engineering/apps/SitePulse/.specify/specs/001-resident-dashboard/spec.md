# Feature Spec: Resident Mobile Dashboard (Ana Sayfa)

> **Feature ID:** SPEC-001  
> **Module:** Sakin Mobil Arayüzü  
> **Status:** APPROVED  

---

## 1. Summary
The Resident Mobile Dashboard is the initial landing screen when a resident (kat maliki or kiracı) opens the SitePulse Android app. It provides an immediate overview of current financial liability (aidat balance), upcoming payment deadlines, emergency announcements, and high-frequency quick actions (reporting a maintenance fault or submitting sub-meter readings).

## 2. Personas & Scenarios
- **Primary Persona:** Zeynep (Kiracı, A Blok Daire 14)
- **Goal:** Quickly verify if her monthly dues are paid, pay via credit card if outstanding, and check if the complex water cut announcement is active.

## 3. Detailed Requirements (Acceptance Criteria)

### Scenario 1: Displaying Outstanding Dues with Delay Penalty
- **Given** Zeynep has an unpaid aidat of ₺1.400,00 that is 10 days past the due date (15th of the month),
- **When** the dashboard loads,
- **Then** calculate the statutory KMK delay penalty ($\text{Delay} = 1.400 \times 0.05 \times \frac{10}{30} = ₺23,33$),
- **And** display the total payable balance as **₺1.423,33**,
- **And** render a prominent **"Hemen Öde"** call-to-action button.

### Scenario 2: Zero Debt / All Paid State
- **Given** the resident has paid all past and current dues,
- **When** the dashboard loads,
- **Then** the hero card displays a green success state with **"Borcunuz Bulunmamaktadır (₺0,00)"**,
- **And** displays the upcoming accrual date (e.g., *"Sonraki Aidat: 1 Ekim 2026"*).

### Scenario 3: Quick Action Navigation
- **Given** the resident is on the dashboard,
- **When** they tap:
  - **"Arıza Bildir"**: Open camera/ticket screen.
  - **"Sayaç Gir"**: Open pay ölçer input sheet.
  - **"Rezervasyon"**: Open facility calendar (tennis/pool).
  - **"Duyurular"**: Open management news feed.

## 4. Non-Goals
- Full accounting reconciliation and bank transfer matching (handled in Admin Web).
- Editing building/complex structural information (read-only for residents).
