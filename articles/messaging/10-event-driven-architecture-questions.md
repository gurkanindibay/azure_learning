---
type: Article
title: "10 Event-Driven Architecture Questions That Separate Architects from Framework Users"
source: "https://codefarm0.medium.com/10-event-driven-architecture-questions-that-separate-architects-from-framework-users-d673024c7557"
author:
  - "Arvind Kumar"
published: 2026-09-05
created: 2026-09-08
description: "10 critical questions and architectural decisions that separate event-driven framework users from architects: consistency, replays, schema evolution, outbox limits, and avoiding distributed monoliths."
tags:
  - "event-driven-architecture"
  - "kafka"
  - "system-design"
  - "messaging"
  - "microservices"
---

# 10 Event-Driven Architecture Questions That Separate Architects from Framework Users

Event-Driven Architecture (EDA) looks simple on slides: *publish events, consume events, scale infinitely*.  
Reality is messier. Most production failures in EDA don’t come from brokers — they come from **wrong assumptions**.

The questions below are the ones that **actually matter in interviews and real systems**.  
If you can reason through these, you’re not just “using Kafka” — you’re designing systems.

---

## 1. How do you guarantee business consistency when events are eventually consistent and may arrive out of order?

### What the interviewer is probing
- Whether you understand that *eventual consistency is a business problem*, not a technical one.

### Why this matters
- Out-of-order events can break invariants like balance, inventory, or entitlement.

### Indicative solution thinking
- Use versioned aggregates, event timestamps vs processing time, and idempotent state transitions.
- Accept that *some consistency must be enforced at the domain boundary*, not downstream.

---

## 2. How do you handle event loss, duplicate events, and reprocessing — and why are these three different problems?

### What the interviewer is probing
- Whether you treat “at least once delivery” as a feature or a footnote.

### Why this matters
- Production systems fail in silent ways when these are mixed up.

### Indicative solution thinking
- **Event loss** → producer guarantees + broker durability.
- **Duplicates** → idempotent consumers.
- **Reprocessing** → deterministic consumers with replay-safe logic.

---

## 3. When should you not use event-driven architecture even if scalability is required?

### What the interviewer is probing
- Your ability to say “no” to popular architecture.

### Why this matters
- EDA adds latency, debugging complexity, and cognitive load.

### Indicative solution thinking
- Avoid EDA for strict transactional workflows or low-latency request/response paths.
- Use it where *decoupling is more valuable than immediacy*.

---

## 4. How do you design consumers so replaying millions of old events does not corrupt current state?

### What the interviewer is probing
- Whether you’ve thought about replays beyond demos.

### Why this matters
- Reprocessing is inevitable after bugs, migrations, or schema fixes.

### Indicative solution thinking
- Separate derived state from source of truth.
- Make consumers deterministic and version-aware.
- Guard side effects (emails, payments) explicitly.

---

## 5. What does the Outbox Pattern solve — and what does it not solve?

### What the interviewer is probing
- Depth beyond pattern memorization.

### Why this matters
- Teams overtrust Outbox and under-design consumers.

### Indicative solution thinking
- Solves atomicity between DB write and event publish.
- Does *not* solve consumer idempotency, ordering, or downstream consistency.

---

## 6. How do you evolve event schemas when multiple consumer versions are already running?

### What the interviewer is probing
- Your understanding of backward vs forward compatibility.

### Why this matters
- Schema mistakes break consumers silently.

### Indicative solution thinking
- Treat events as contracts, not DTOs.
- Prefer additive changes, explicit versioning, and consumer-driven evolution.
- Never “fix” an old event shape in place.

---

## 7. What is the real difference between event-driven and message-driven systems?

### What the interviewer is probing
- Conceptual clarity, not tooling knowledge.

### Why this matters
- Message-driven systems tend to drift into orchestration.

### Indicative solution thinking
- Events describe *facts that happened*.
- Messages describe *commands expecting action*.
- Mixing the two leads to tight coupling and fragile flows.

---

## 8. How do you debug a production issue when a single business flow spans 10 event-driven services?

### What the interviewer is probing
- Operational maturity.

### Why this matters
- EDA without observability is a black box.

### Indicative solution thinking
- Use correlation IDs, distributed tracing, and event metadata.
- Debug via *event timelines*, not service logs alone.
- Design observability from day one.

---

## 9. Should events be immutable forever, or can they be corrected later?

### What the interviewer is probing
- Your stance on data truth and auditability.

### Why this matters
- Legal, financial, and compliance systems depend on this decision.

### Indicative solution thinking
- Prefer immutability.
- Model corrections as compensating events, not edits.
- Let consumers decide how to interpret history.

---

## 10. How do you prevent an event-driven system from becoming a distributed monolith over time?

### What the interviewer is probing
- Whether you understand that *decoupling can slowly rot*.

### Why this matters
- Many “event-driven” systems end up tightly coupled through implicit assumptions.

### Indicative solution thinking
- Enforce clear ownership of events.
- Avoid consumers relying on internal fields of other domains.
- Periodically review event contracts like public APIs.
