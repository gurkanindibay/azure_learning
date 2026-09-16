# SitePulse Engineering Constitution (Spec Kit)

> **Version:** 1.0.0  
> **Domain:** Residential Site & Community Management (Apsiyon Model)  
> **Primary Interface:** Android (Kotlin / Jetpack Compose)  
> **Platform Governance:** Kat Mülkiyeti Kanunu (KMK - 634 Sayılı Kanun)  

---

## 1. Core Architectural Principles

### 1.1 Kat Mülkiyeti Kanunu (KMK) Compliance
1. **Financial Integrity & Calculation Rules:**
   - Currency must NEVER use floating-point types (`float`, `double`). All financial balances, dues, and interest calculations must use `BigDecimal` (JVM) or `decimal`.
   - Statutory Delay Penalty (**Gecikme Tazminatı**): Per KMK Article 20, unpaid dues incur a maximum of 5% monthly delay compensation, pro-rated on a daily basis ($\text{Delay} = \text{Principal} \times 0.05 \times \frac{\text{DaysOverdue}}{30}$).
   - **Arsa Payı Distribution:** When expenses are shared based on land-share ratios, rounding remainders must be reconciled down to the single kuruş (₺0.01) so that $\sum \text{DairePayi} = \text{ToplamGider}$.

2. **Role & Tenancy Segregation:**
   - Every unit (**Bağımsız Bölüm**) has an immutable relationship with its **Kat Maliki** (Property Owner).
   - A unit may have an optional active **Kiracı** (Tenant).
   - Core dues (operating expenses: kapıcı, temizlik, güvenlik) can be billed to Kiracı or Maliki; capital expenses (demirbaş, çatı onarımı, asansör yenileme) are legally attributable solely to the **Kat Maliki**.

---

## 2. Backend & Database Conventions (Java 21 + PostgreSQL)

1. **Stack & Versioning:**
   - **Language:** Java 21 (LTS)
   - **Framework:** Spring Boot 3.x (Web, Data JPA, Validation)
   - **Database:** PostgreSQL 16+
   - **Migration Tool:** Flyway (versioned immutable SQL scripts in `src/main/resources/db/migration/`)

2. **Database Schema & Financial Rigor:**
   - **Monetary Columns:** Must strictly use `NUMERIC(15, 2)` in PostgreSQL and `BigDecimal` in Java entities. `FLOAT` or `DOUBLE PRECISION` is strictly forbidden.
   - **Auditability:** All financial transactions (tahakkuk, tahsilat, gecikme zammı) must be stored in immutable ledger tables (`tahsilat_hareketleri`) with timestamp, operator ID, and balance snapshot.
   - **Concurrency Control:** Use optimistic locking (`@Version` integer column) on unit balance records to prevent double-spending or race conditions during payment gateway webhooks.
   - **Referential Integrity:** Enforce foreign keys between `siteler` -> `bloklar` -> `bagimsiz_bolumler` -> `kat_malikleri` and `aidat_tahakkuklari`.

---

## 3. Android Development Conventions

1. **Stack & Versioning:**
   - **Language:** Kotlin 2.x
   - **UI Framework:** Jetpack Compose with **Material 3 (M3)**
   - **Architecture:** MVI / MVVM with Unidirectional Data Flow (UDF)
   - **Asynchronous:** Kotlin Coroutines & `StateFlow`

2. **UI & Usability Mandates (UI/UX Guardrails):**
   - **Touch Targets:** Minimum 48dp on all clickable elements.
   - **Design Tokens:** All colors and typography must use Material 3 Theme tokens; no hardcoded hex values in composables.
   - **State Handling:** Every screen must explicitly define four states: `Loading`, `Empty`, `Error`, and `Success`.
   - **Accessibility:** Content descriptions on all icons, WCAG 2.1 AA contrast ratios on text and buttons.

3. **Offline-First & State Synchronization:**
   - All resident information and recent balance statements must be cached locally (Room DB).
   - Network errors must gracefully degrade to offline-cached data with a clear "Çevrimdışı Mod" indicator.

---

## 4. The Harness Loop & Graph Constraints

1. **Topological Task Scheduling:**
   - Code must only be written for tasks whose prerequisites in `task-dag.json` are in the `VERIFIED` state.
   - Core Domain entities must be established and tested before UI ViewModels or API integrations are attempted.

2. **Verification Gates:**
   - **Build Gate:** Code must compile with zero errors and zero warnings.
   - **Financial Precision Gate:** Unit tests must assert exact decimal balances without rounding leaks.
   - **Lint Gate:** Android layout and naming conventions must adhere to Kotlin best practices.
   - **Budget Limit:** A task loop terminates and escalates if verification gates fail after 3 successive iterations.
