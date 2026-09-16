# SitePulse: AI-Manufactured Residential Site Management Platform

> **Domain:** Apsiyon-style Apartman & Site Yönetim Platformu (KMK Compliance, Financial Integrity)  
> **Interface:** Android Native (Kotlin 2.x + Jetpack Compose Material 3)  
> **Methodology:** Spec-Driven Development (Spec Kit) + Closed-Loop Harness (Loops & Graphs)  

---

## 1. Multi-Agent Team & System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    1. Discovery & Design Layer (Spec Kit)                       │
│                                                                                 │
│   .specify/constitution.md         <── Platform Rules (KMK, BigDecimal)         │
│   .specify/agents/pm-agent.md      <── PM Agent: User Stories & Acceptance Tests│
│   .specify/agents/uiux-agent.md    <── UI/UX Agent: M3 Tokens & HTML Prototypes │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    2. Architectural Planning & Graph Layer                      │
│                                                                                 │
│   .specify/agents/architect-agent.md <── Architect Agent: Clean Arch & Contracts│
│   .specify/tasks/task-dag.json       <── Topological Task Dependency Graph      │
│   harness/graph/task_dag.py          <── Graph Engine & Task Scheduler          │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │ Schedules Next Task Node
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    3. Closed-Loop Execution Harness (Maker-Checker)             │
│                                                                                 │
│   .specify/agents/developer-agent.md <── Developer Agent (Maker: Kotlin/Compose)│
│   .specify/agents/tester-agent.md    <── Tester Agent (Checker: xUnit/JUnit)    │
│   harness/loop/verification_gates    <── Syntax, Financial & Test Gates         │
│   harness/loop/loop_runner.py        <── 3-Iteration Closed Feedback Loop       │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │ Passes Gate
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    4. Verified Full-Stack Deliverables                          │
│                                                                                 │
│   A. Android Native Client (Kotlin / Jetpack Compose / M3)                      │
│      - android/app/.../domain/     (Daire, AidatBorcu, CalculateDuesUseCase)    │
│      - android/app/.../ui/         (DashboardScreen, ViewModel, M3 Theme)       │
│                                                                                 │
│   B. Backend Application (Java 21 / Spring Boot 3.3.4 / REST)                   │
│      - backend/src/.../domain/     (JPA Entities with @Version optimistic lock) │
│      - backend/src/.../service/    (AidatCalculationService - KMK Art. 20)      │
│      - backend/src/.../controller/ (ResidentDashboardController REST API)       │
│                                                                                 │
│   C. Database (PostgreSQL 16+ / Flyway Migrations)                              │
│      - backend/src/.../migration/  (V1__init_schema.sql with NUMERIC(15,2))     │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Running the Harness

### View Task DAG & Progress
```bash
python3 harness/harness_cli.py status
```

### Find Next Runnable Tasks
```bash
python3 harness/harness_cli.py next
```

### Verify a Task in the Closed Loop
```bash
python3 harness/harness_cli.py verify --task task-01
```

### Run Harness Self-Tests
```bash
python3 -m unittest discover -s harness/tests
```

---

## 3. Backend & Database Development Environment (Docker)

To run the PostgreSQL 16 database and Adminer web GUI locally:

```bash
# Start PostgreSQL & Adminer with pre-seeded test data
./scripts/dev-db-up.sh

# Or directly via Docker Compose in backend/
cd backend && docker compose up -d postgres adminer
```

| Service | Host / Port | Credentials / Purpose |
| :--- | :--- | :--- |
| **PostgreSQL 16** | `localhost:5432` | DB: `sitepulse`, User: `sitepulse_user`, Pass: `sitepulse_secret` |
| **Adminer Web GUI** | `http://localhost:8081` | Web database management client |
| **Spring Boot App** | `localhost:8080` | `GET /api/v1/residents/d-14/dashboard` |

To tear down the containers:
```bash
./scripts/dev-db-down.sh
```

---

## 4. Interactive UI/UX Visual Prototype
To preview the Android mobile interface in your browser before running on a device:
- Open [prototype.html](.specify/specs/001-resident-dashboard/assets/prototype.html) in any web browser.
- Supports interactive state toggling between **Borçlu (Gecikmeli)** and **Borçsuz (Ödenmiş)** states.
