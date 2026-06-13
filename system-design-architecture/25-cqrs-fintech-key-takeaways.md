# 25. CQRS for Fintech — Key Takeaways

> **Parent**: [System Design Interview Reference](README.md)
> **Source**: [CQRS For Fintech In 2026: Ledgers, Limits, Risk, And The Fight Over Truth](https://medium.com/@the_atomic_architect/cqrs-fintech-2026-ledger-truth-bdbbcfeb65dc) — The Atomic Architect, Apr 2026 · [Local copy](../articles/medium/cqrs-for-fintech-2026.md)
> **Purpose**: Extract practical CQRS boundaries for money-facing systems — separating command authority from query flexibility, protecting the ledger as the single source of financial truth, and preventing one model from becoming a junk drawer for the whole company.
> **Also see**: [Concurrency & Transactions](02-concurrency-transactions.md), [Message Brokers & Async](05-message-brokers-async.md), [Resilience Patterns](10-resilience-patterns.md), [Async & Concurrency Patterns](08-async-concurrency-patterns.md)
> **Dictionary**: [Reference Dictionary](../reference-dictionary/) — definitions for [projection](../reference-dictionary/cqrs-event-driven.md#projection), [read model](../reference-dictionary/cqrs-event-driven.md#read-model), [ledger](../reference-dictionary/cqrs-event-driven.md#ledger), [CQRS](../reference-dictionary/cqrs-event-driven.md#cqrs), [idempotency](../reference-dictionary/cqrs-event-driven.md#idempotency), [outbox pattern](../reference-dictionary/cqrs-event-driven.md#outbox-pattern), and other key terms
> **Taxonomy Reference**: §3.3 Event-Driven & Messaging, §7.1 Reliability & Resilience

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`cqrs-01`](#cqrs-01-commands-protect-truth-queries-explain-truth) | One model answering too many questions | Commands protect truth; queries explain truth — never confuse the two |
| [`cqrs-02`](#cqrs-02-the-ledger-is-truth-balance-is-a-derived-view) | Balance table treated as source of truth | The ledger records movement; balance is a derived projection |
| [`cqrs-03`](#cqrs-03-idempotency-before-the-ledger-command) | Retries become duplicate money movement | Idempotency guard must sit before the ledger, not after |
| [`cqrs-04`](#cqrs-04-limits-belong-on-the-command-side) | Display limits used for approval decisions | Command-side reserves limits; query-side displays remaining allowance |
| [`cqrs-05`](#cqrs-05-risk-creates-actions-never-rewrites-history) | Risk decisions silently mutating history | Post corrections as new entries; never delete or mutate original events |
| [`cqrs-06`](#cqrs-06-outbox-pattern-for-transaction-event-atomicity) | Ledger committed but event never published | Save ledger entries and outbox events in the same database transaction |
| [`cqrs-07`](#cqrs-07-read-models-are-replaceable-the-ledger-is-sacred) | Product changes requiring ledger redesign | Read models can be rebuilt; the ledger must never be compromised |
| [`cqrs-08`](#cqrs-08-the-balance-screen-is-a-story-not-authority) | Read model used for final transfer approval | Display data informs humans; command data decides money movement |
| [`cqrs-09`](#cqrs-09-events-dont-fix-a-confused-ledger) | "Let's make it event-driven" without truth clarity | Events amplify confusion; the ledger must commit before events describe it |
| [`cqrs-10`](#cqrs-10-reconciliation-as-a-first-class-concern) | Reconciliation treated as a nightly afterthought | Design operations views for mismatch detection and explanation |
| [`cqrs-11`](#cqrs-11-language-precision--domain-modeling-through-words) | "Success" meaning different things to different teams | Financial states must mean one precise thing across the system |
| [`cqrs-12`](#cqrs-12-the-one-rule-command-data-vs-display-data) | Engineers unsure where to place new data | If it decides money movement → command side; if it helps humans understand → query side |
| [`cqrs-13`](#cqrs-13-command-side-boring-query-side-helpful) | Command endpoints doing ten unrelated things | Write path narrow and strict; read path wide and flexible |
| [`cqrs-14`](#cqrs-14-almost-correct-is-the-most-dangerous) | "Most transfers work" hiding systemic fragility | Architecture judged by the ugly day, not the happy path |
| [`cqrs-15`](#cqrs-15-dont-overdo-or-underdo-cqrs) | Every feature becoming a distributed system | Separate money decisions from money displays first; grow from there |

---

## cqrs-01: Commands Protect Truth, Queries Explain Truth

> **Source**: [Article §"CQRS Is Not Fancy Here"](../articles/medium/cqrs-for-fintech-2026.md#cqrs-is-not-fancy-here)

| | |
|:---|:---|
| **Problem** | One endpoint, one table, one entity, one response model is asked to answer nine different questions — from "can this money move?" to "can compliance audit it?" — and the system begins to lie. Politely. With clean JSON. |
| **Root cause** | The endpoint is no longer an endpoint — it is a courtroom with HTTP headers. Each new team (risk, fraud, support, compliance) adds their concern to the same response path. |

### The Core Boundary

| Side | Responsibility | Personality | Must NOT |
|:---|:---|:---|:---|
| **Command** | Protect financial truth | Strict, almost boring, almost rude | Depend on read models for approval |
| **Query** | Explain financial truth | Flexible, fast, human-shaped | Become the source of financial truth |

### Command Side Questions (Narrow)

```
Can this request be accepted?
Is it a duplicate?
Is the customer allowed?
Is the account active?
Is the limit available?
Is the risk acceptable?
Can the ledger entries balance?
Can this decision be defended later?
```

### Query Side Flexibility (Wide)

```
Dashboards, caching, denormalized views, timelines, mobile screens,
support search, operations investigation, risk analytics, finance reports
```

> **Key insight**: The command path is narrow. The read path is wide. That is the point. The command side protects correctness. The query side protects experience. If the read model is delayed, that is a product and communication problem. If the ledger is wrong, that is a trust problem. Those two problems are not equal.

**Cross-reference**: This is the foundational boundary that `cqrs-03` through `cqrs-12` build upon. See also [Async & Concurrency Patterns](08-async-concurrency-patterns.md) for command processing patterns.

---

## cqrs-02: The Ledger Is Truth; Balance Is a Derived View

> **Source**: [Article §"The Ledger Is Not A Balance Table"](../articles/medium/cqrs-for-fintech-2026.md#the-ledger-is-not-a-balance-table)

| | |
|:---|:---|
| **Problem** | A balance table (`account_id`, `balance`, `updated_at`) is treated as the source of truth, but fintech doesn't live in simple updates — money moves. |
| **Root cause** | Confusing "current state" with "financial history" — one is a snapshot, the other is evidence.

> 📖 **Dictionary**: [Projection](../reference-dictionary/cqrs-event-driven.md#projection) · [Ledger](../reference-dictionary/cqrs-event-driven.md#ledger)

### Balance Table vs Proper Ledger

| Aspect | Balance Table | Proper Ledger |
|:---|:---|:---|
| **Operation** | Overwrite a number | Append balanced entries |
| **Correction** | Quietly edit the past | Post a reversal entry |
| **Deletion** | Casual row removal | Never delete — post a correction |
| **Auditability** | Last value only | Full movement history |
| **Debit = Credit** | Not enforced | Every entry must balance |
| **Reconciliation** | Compare two numbers | Trace every movement |

### Ledger Principles

1. **One side debited, another side credited** — the total must balance
2. **Every movement leaves evidence** — immutable append-only
3. **Corrections are new entries** — never edit the past, post reversals
4. **History is evidence, not garbage** — needed by support, reconciliation, finance, compliance, customer, and engineers debugging at 2 AM

> **The sentence every money-facing team should have on their wall**: "The ledger is the truth. The balance is a derived view."

**Cross-reference**: See [Concurrency & Transactions](02-concurrency-transactions.md) for transaction isolation levels that protect ledger integrity.

---

## cqrs-03: Idempotency Before the Ledger Command

> **Source**: [Article §"Idempotency Is A Fintech Seatbelt"](../articles/medium/cqrs-for-fintech-2026.md#idempotency-is-a-fintech-seatbelt)

| | |
|:---|:---|
| **Problem** | Retries (user double-tap, mobile network failure, provider timeout, load balancer retry, worker crash) become duplicate money movement. |
| **Root cause** | Idempotency checks placed after the dangerous operation, or tied to HTTP requests rather than business intent. |

### Idempotency Check Placement

```
WRONG:  Command → Risk → Limits → Ledger → THEN check idempotency
RIGHT:  Command → IDEMPOTENCY GUARD → Risk → Limits → Ledger
```

| Principle | Detail |
|:---|:---|
| **Key belongs to the business action** | Not the HTTP request, not the session, not the customer — the exact transfer intent |
| **Server remembers the key** | And the original result (accepted or rejected) |
| **Sits before the dangerous part** | Before money moves, before the ledger command |
| **Uses `SELECT FOR UPDATE`** | Prevents race conditions on idempotency key lookup |

### The Idempotency Contract

```
I have seen this exact transfer request before.
I already accepted it. / I already rejected it.
I already know the result.
I will not move money again.
```

> **Key insight**: Idempotency is not a best-effort log check. It is a financial seatbelt that must be fastened before the engine starts.

**Cross-reference**: See [Resilience Patterns](10-resilience-patterns.md) for retry strategies and idempotency in distributed systems.

---

## cqrs-04: Limits Belong on the Command Side

> **Source**: [Article §"Limits Are Not Just Numbers"](../articles/medium/cqrs-for-fintech-2026.md#limits-are-not-just-numbers)

| | |
|:---|:---|
| **Problem** | A displayed remaining limit is used for final transfer approval, but the display may be stale, cached, or computed from a lagging projection. |
| **Root cause** | Treating a read-side calculation as the final authority for money movement. |

### Limit Decision Boundaries

| Side | Responsibility | Mechanism |
|:---|:---|:---|
| **Command** | Reserve limit atomically | `SELECT FOR UPDATE`, strong consistency |
| **Query** | Display remaining allowance | Eventually consistent, cacheable |

### Real-World Limit Questions the Command Side Must Handle

| Question | Example |
|:---|:---|
| Does a pending transfer consume the limit? | Yes — reserve immediately |
| Does a failed transfer release it? | Yes — release on deterministic failure |
| Does a reversed transfer restore it? | Yes — restore as a new limit event |
| Does a scheduled transfer reserve it? | Yes — reserve at scheduling time |
| Do card payments, bank transfers, and wallet payouts share the same limit? | Configurable per product |
| What if two transfers arrive simultaneously? | Lock on customer limit row |
| What if risk rejects after limit reservation? | Release the reservation |

> **Key insight**: The read model can inform the customer. The command model must protect the system. That boundary matters.

**Cross-reference**: See [Concurrency & Transactions](02-concurrency-transactions.md) for pessimistic locking patterns on limit rows.

---

## cqrs-05: Risk Creates Actions, Never Rewrites History

> **Source**: [Article §"Risk Is Not The Ledger"](../articles/medium/cqrs-for-fintech-2026.md#risk-is-not-the-ledger)

| | |
|:---|:---|
| **Problem** | Risk later discovers something suspicious and silently mutates or deletes the original financial event. |
| **Root cause** | Confusing "risk decision" with "financial history" — risk is a new action, not a rewrite. |

### Risk Actions as New Entries (Never Mutations)

```
Original event:     TRANSFER_POSTED   (immutable)
Risk detection:     FRAUD_SUSPECTED   (new entry, new timestamp)
Risk decision:      ACCOUNT_FROZEN    (new entry, new timestamp)
Correction:         TRANSFER_REVERSED (new entry, new timestamp)
```

| Wrong Approach | Right Approach |
|:---|:---|
| Delete the original transfer | Post a reversal entry |
| Mutate status to "fraudulent" | Add `FRAUD_SUSPECTED` as a separate event |
| Hide uncomfortable history | Make the mess explainable |
| Pretend the original event never happened | Tell the story: *This happened → then this was detected → then this decision was made → then this correction was posted* |

> **Key insight**: A system that deletes or mutates uncomfortable financial history is not clean. It is unsafe. Fintech systems earn trust not by hiding mess, but by making the mess explainable.

**Cross-reference**: See the ledger principles in [`cqrs-02`](#cqrs-02-the-ledger-is-truth-balance-is-a-derived-view).

---

## cqrs-06: Outbox Pattern for Transaction-Event Atomicity

> **Source**: [Article §"The Outbox Is Boring Until It Saves You"](../articles/medium/cqrs-for-fintech-2026.md#the-outbox-is-boring-until-it-saves-you)

| | |
|:---|:---|
| **Problem** | The ledger entry is saved but the service crashes before publishing the event — the read model never updates, dashboards are wrong, support is confused. Or worse: the event is published but the database transaction rolls back — the read side believes in a transfer that never became ledger truth. |
| **Root cause** | Dual-write problem: database write and message publish are not atomic. |

### The Dual-Write Gap

```
DANGEROUS:  Save ledger → Publish event → Return success
            ↑                                    ↑
            Crash here: ledger knows,            Or rollback here: event published,
            read model doesn't                   ledger doesn't have it
```

### The Outbox Fix

```
SAFE:       Save ledger entries + Save outbox event  (same DB transaction)
            ↓
            Separate process reads outbox → publishes to Kafka/Queue
            ↓
            Read models consume and update
```

| Principle | Detail |
|:---|:---|
| **Same transaction** | Ledger entries and outbox event committed atomically |
| **Separate publisher** | A dedicated process reads the outbox table and publishes safely |
| **At-least-once** | Publisher handles retries; consumers must be idempotent |
| **Order preserved** | Events published in transaction commit order |

> **Key insight**: The event is not the source of truth. The ledger transaction is. The event tells other systems what the ledger already accepted. That order matters. A lot.

**Cross-reference**: See [Message Brokers & Async](05-message-brokers-async.md) for Kafka integration patterns and exactly-once semantics.

---

## cqrs-07: Read Models Are Replaceable; The Ledger Is Sacred

> **Source**: [Article §"The Read Model Can Be Ugly"](../articles/medium/cqrs-for-fintech-2026.md#the-read-model-can-be-ugly)

| | |
|:---|:---|
| **Problem** | Product changes (new dashboard, new support screen, new risk view, new mobile timeline) force changes to the ledger design or pollute financial records with display fields. |
| **Root cause** | Treating read models as equally important as the ledger — they are not.

> 📖 **Dictionary**: [Projection](../reference-dictionary/cqrs-event-driven.md#projection) · [Read Model](../reference-dictionary/cqrs-event-driven.md#read-model)

### Sacred vs Replaceable

| Sacred (Ledger) | Replaceable (Read Models) |
|:---|:---|
| Cannot be rebuilt from scratch | Can be rebuilt from the ledger |
| Must be correct at all times | Can be eventually consistent |
| Never polluted with display fields | Optimized for specific screens |
| Single source of truth | Multiple purpose-built views |
| Changes require migration planning | Changes are low-risk |

### What Read Models Can Do

```
Duplicate data, store display-friendly status, precompute balances,
keep transaction timelines, store merchant names, maintain daily spending summaries,
maintain support search fields, keep risk exposure snapshots,
be rebuilt, be replaced, be optimized for one screen.
```

> **Key insight**: Once you accept that read models are not sacred, product changes become less scary. A new dashboard card does not require changing ledger design. A new support screen does not require polluting the command model. You build the view that humans need — but you do not let that view become the authority.

**Cross-reference**: See [Caching Architecture](03-caching-architecture.md) for read-model materialization strategies.

---

## cqrs-08: The Balance Screen Is a Story, Not Authority

> **Source**: [Article §"The Balance Screen Is A Story"](../articles/medium/cqrs-for-fintech-2026.md#the-balance-screen-is-a-story)

| | |
|:---|:---|
| **Problem** | Teams build a fast read model → use it for display (good) → use it for support (still okay) → use it for limit checks (danger) → use it for final transfer approval (now the read side has become a hidden authority and CQRS collapses). |
| **Root cause** | The boundary erodes incrementally — each step feels reasonable in isolation.

> 📖 **Dictionary**: [Projection](../reference-dictionary/cqrs-event-driven.md#projection) — a balance screen is a projection; the command side is the truth.

### The Erosion Path

```
Display  →  Support  →  Limit Checks  →  Transfer Approval
  ✓           ✓            ✗                 ✗✗
Safe        Tolerable     Dangerous          Catastrophic
```

| What the Customer Sees | What Actually Decides |
|:---|:---|
| Available balance | ← Display only |
| Pending amount | ← Display only |
| Recent transaction | ← Display only |
| Hold amount | ← Display only |
| Failed transfer | ← Display only |
| Reversed payment | ← Display only |
| Daily limit remaining | ← Display only |
| **Final debit decision** | ← **Command side only** |

> **Key insight**: A balance screen is a useful, customer-friendly, possibly very accurate story — but it is still a story built from financial facts. The screen itself should not decide money movement. That decision belongs to the command side.

**Cross-reference**: This is the natural consequence of [`cqrs-04`](#cqrs-04-limits-belong-on-the-command-side) — limits displayed are stories; limits reserved are decisions.

---

## cqrs-09: Events Don't Fix a Confused Ledger

> **Source**: [Article §"Kafka Does Not Fix A Confused Ledger"](../articles/medium/cqrs-for-fintech-2026.md#kafka-does-not-fix-a-confused-ledger)

| | |
|:---|:---|
| **Problem** | Teams say "Let's make it event-driven" thinking it will fix financial correctness, but if the ledger model is confused, events spread that confusion faster. |
| **Root cause** | Confusing transport correctness (events delivered reliably) with business correctness (events describe valid financial decisions). |

### Events: Amplifier, Not Fixer

| Scenario | Result |
|:---|:---|
| Clear command boundary + events | ✅ Events spread trusted decisions |
| Confused command boundary + events | ❌ Events spread confusion faster and harder to debug |

### The Right Order

```
CORRECT:   Ledger commits  →  Event describes what already happened
WRONG:     Event fires     →  Ledger records as side effect
```

> **Key insight**: A bad event is not better than a bad API response. It is just easier to distribute. The better question is: "What exactly is the source of truth?" If the answer is unclear, adding events will not help. In fintech, the ledger should not be a side effect of a random event. The event should describe a ledger decision that already happened.

**Cross-reference**: See [`cqrs-06`](#cqrs-06-outbox-pattern-for-transaction-event-atomicity) for how events should be emitted — from the outbox, after the transaction commits.

---

## cqrs-10: Reconciliation as a First-Class Concern

> **Source**: [Article §"Reconciliation Is Where Architecture Meets Reality"](../articles/medium/cqrs-for-fintech-2026.md#reconciliation-is-where-architecture-meets-reality)

| | |
|:---|:---|
| **Problem** | Every architecture diagram looks perfect before reconciliation. Then reality arrives: provider timeouts, late settlement files, pending transactions, reversals after success, external success but internal worker failure, delayed events, stale projections. |
| **Root cause** | Reconciliation treated as a nightly batch job rather than a continuous architectural capability. |

### Reconciliation Questions the System Must Ask Itself

```
Do my records match the outside world?
Does my ledger match the payment rail?
Do my customer-visible states match my financial states?
Do my reversals make sense?
Do my failed transactions have clear final outcomes?
Do my pending transactions eventually resolve?
```

### Architecture for Reconciliation

| Layer | Reconciliation View |
|:---|:---|
| **Customer view** | Designed for clarity — "where is my money?" |
| **Operations view** | Designed for reconciliation — mismatch detection, failure reasons, settlement references, correction history |
| **Ledger** | Remains the source of truth — never compromised for reconciliation convenience |

> **Key insight**: A serious fintech system should expect mismatch — not because engineers are careless, but because distributed systems are messy. The goal is not to pretend mismatch will never happen. The goal is to detect it, explain it, and correct it without damaging ledger truth.

**Cross-reference**: See [Resilience Patterns](10-resilience-patterns.md) for failure detection and recovery strategies.

---

## cqrs-11: Language Precision — Domain Modeling Through Words

> **Source**: [Article §"The Words Matter Too"](../articles/medium/cqrs-for-fintech-2026.md#the-words-matter-too)

| | |
|:---|:---|
| **Problem** | Product, engineering, support, and operations use the same words differently — "success," "failed," "pending," "posted," "settled," "reversed," "available" mean different things to different teams. |
| **Root cause** | Treating terminology as copywriting rather than domain modeling. |

### Words That Must Mean One Thing

| Word | Must NOT Mean | Must Mean |
|:---|:---|:---|
| **Success** | "We accepted the request but settlement may fail" | "The financial transaction is complete and settled" |
| **Available** | "Available unless a delayed hold arrives" | "Available for immediate use with no pending claims" |
| **Failed** | "Failed for the customer but maybe still pending externally" | "Definitively not processed; no money moved" |
| **Reversed** | "Deleted" | "A new correcting entry was posted; original remains" |
| **Pending** | "We have no idea" | "Awaiting a specific, named external confirmation" |

> **Key insight**: A fintech system with unclear words becomes unclear code. Unclear code becomes unclear behavior. Unclear behavior becomes customer mistrust. The command side should define financial states. The query side should translate those states for humans. But translation should never become fiction.

**Cross-reference**: This is domain-driven design (DDD) applied to fintech — the ubiquitous language must be precise and binding.

---

## cqrs-12: The One Rule — Command Data vs Display Data

> **Source**: [Article §"The One Rule I Trust"](../articles/medium/cqrs-for-fintech-2026.md#the-one-rule-i-trust)

| | |
|:---|:---|
| **Problem** | Engineers debate where to place new data — should the new field go in the command model or the query model? |
| **Root cause** | No simple heuristic for the boundary decision. |

### The One Rule

| If the data... | It belongs on... | Example |
|:---|:---|:---|
| **Can decide whether money moves** | **Command side** | Final debit decision, ledger posting, risk approval, limit reservation |
| **Helps humans understand what happened** | **Query side** | Available balance display, transaction timeline, risk dashboard, remaining limit screen |

### Applying the Rule

| Data | Side | Reason |
|:---|:---|:---|
| Available balance display | Query | Helps the customer understand |
| Final debit decision | Command | Decides whether money moves |
| Transaction timeline | Query | Helps support investigate |
| Ledger posting | Command | Records the financial truth |
| Risk dashboard | Query | Helps analysts assess |
| Risk approval | Command | Decides whether to allow |
| Remaining limit screen | Query | Informs the customer |
| Limit reservation | Command | Protects the system |
| Customer notification | After command result | Informs, does not decide |

> **Key insight**: This rule stops a dashboard from becoming a bank. It stops a cache from becoming a judge. It stops a projection from becoming the ledger. And it gives engineers a simple way to discuss architecture without turning every meeting into theory.

---

## cqrs-13: Command Side Boring, Query Side Helpful

> **Source**: [Article §"The Command Side Should Be Boring" and "The Query Side Should Be Helpful"](../articles/medium/cqrs-for-fintech-2026.md#the-command-side-should-be-boring)

| | |
|:---|:---|
| **Problem** | Command endpoints become exciting — doing ten unrelated things because "the data is already there." Query endpoints become rigid — forcing every consumer to parse ledger entries. |
| **Root cause** | Not giving each side a distinct personality and set of constraints. |

### Command Side Personality: Boring

```
Receive command → Check duplicate → Validate account → Check risk →
Reserve limit → Create ledger entries → Validate debit = credit →
Commit transaction → Save outbox event → Return clear result
```

| Must Do | Must NOT Do |
|:---|:---|
| Be understandable in a single read-through | Build rich dashboard responses |
| Use the strongest consistency available | Perform search queries |
| Make decisions with authoritative data | Return every customer summary field |
| Return a clear, minimal result | Depend on a read model for approval |
| Be boring in the best possible way | Ask a cache whether money can move |

### Query Side Personality: Helpful

| Consumer | Needs | NOT |
|:---|:---|:---|
| **Customer** | Is it pending, successful, failed, reversed, under review? | Raw ledger entries |
| **Support agent** | Clear timeline of what happened | Five-table inspection |
| **Risk analyst** | Exposure by account, customer, device, beneficiary, region, behavior | Mobile dashboard |
| **Operations** | Reconciliation status, failure reason, settlement reference, correction history | Customer app response |
| **Finance** | Reporting-friendly aggregates | Operational detail |

> **Key insight**: A good fintech command side should not be exciting. It should not be clever. It should be the kind of boring that lets people sleep. Fast and wrong is still wrong.

**Cross-reference**: See the full command flow code in the [source article](../articles/medium/cqrs-for-fintech-2026.md#the-code-i-would-put-near-the-money).

---

## cqrs-14: Almost-Correct Is the Most Dangerous

> **Source**: [Article §"The Most Dangerous Architecture Is Almost Correct"](../articles/medium/cqrs-for-fintech-2026.md#the-most-dangerous-architecture-is-almost-correct)

| | |
|:---|:---|
| **Problem** | "Most transfers work. Most balances look right. Most retries are fine. Most events publish. Most read models catch up. Most customers never complain." — The "most" is where the danger lives. |
| **Root cause** | Architecture validated only against the happy path, never against the ugly day. |

### What the Ugly Day Tests

| Scenario | What Breaks Without CQRS Boundaries |
|:---|:---|
| Retry storms | Duplicate money movement |
| Provider timeouts | Half-committed states |
| Duplicate requests | Double debit |
| Partial failures | Read/write inconsistency |
| Delayed events | Dashboard-showing-wrong-balance |
| Reconciliation mismatch | No way to trace what happened |
| Fraud review | History silently mutated |
| Reversal flows | Original event deleted |
| Audit questions | Five different answers from five teams |

> **Key insight**: Architecture is not judged by the happy path. It is judged by the day when everything is half-working and everyone wants an answer. That is the day your CQRS boundary either protects you or exposes you.

**Cross-reference**: See [Resilience Patterns](10-resilience-patterns.md) for designing systems that survive the ugly day.

---

## cqrs-15: Don't Overdo or Underdo CQRS

> **Source**: [Article §"Where Teams Overdo CQRS" and "Where Teams Underdo CQRS"](../articles/medium/cqrs-for-fintech-2026.md#where-teams-overdo-cqrs)

| | |
|:---|:---|
| **Problem** | Teams either turn every feature into a distributed system with twelve projections, or avoid CQRS entirely and keep everything in one Account entity until it becomes a junk drawer. |
| **Root cause** | All-or-nothing thinking about CQRS adoption. |

### The Two Extremes

| Overdo CQRS | Underdo CQRS |
|:---|:---|
| Every feature becomes a distributed system | One Account entity does everything |
| Every change needs an event | One Transaction table for all concerns |
| Every table gets a projection | One service for command and query |
| Every query gets its own database | One response object for every screen |
| Every service owns a version of truth | One balance field carrying too much meaning |
| Every developer needs three diagrams for one button | Every new feature becomes risky |

### What Actually Matters (Start Here)

```
1. Separate money decisions from money displays
2. Protect the ledger
3. Make retries safe (idempotency)
4. Make limits consistent
5. Make risk decisions traceable
6. Make read models rebuildable
7. Make customer states honest
```

> **Key insight**: Most fintech teams do not need full event sourcing on day one. They do not need to replay the universe before they have clean ledger entries. They do not need twelve projections before they have one reliable command boundary. Do not start by building a cathedral when the front door is missing. But also do not wait until one model has become a junk drawer for the whole company.

**Cross-reference**: See [`cqrs-12`](#cqrs-12-the-one-rule-command-data-vs-display-data) for the simple heuristic that keeps CQRS adoption pragmatic.

---

## Quick Reference Card

| ID | Decision | Answer |
|:---|:---|:---|
| `cqrs-01` | Where does truth live? | Command side protects it; query side explains it |
| `cqrs-02` | What is the source of financial truth? | The ledger — balance is a derived view |
| `cqrs-03` | Where does idempotency go? | Before the ledger, not after |
| `cqrs-04` | Who reserves limits? | Command side, with strong consistency |
| `cqrs-05` | Can risk delete history? | Never — post new actions, never mutate originals |
| `cqrs-06` | How to publish events safely? | Outbox pattern — same DB transaction as ledger |
| `cqrs-07` | Can I rebuild the read model? | Yes — read models are replaceable |
| `cqrs-08` | Does the balance screen decide? | No — it tells a story; the command side decides |
| `cqrs-09` | Will events fix my ledger? | No — they'll spread confusion faster |
| `cqrs-10` | When do I reconcile? | Continuously — design views for mismatch detection |
| `cqrs-11` | Does "success" mean one thing? | It must — unclear words become unclear code |
| `cqrs-12` | Where does this new field go? | Decides money → command; helps humans → query |
| `cqrs-13` | Should my command endpoint do more? | No — boring is safe; fast and wrong is still wrong |
| `cqrs-14` | Is "most transfers work" enough? | No — the ugly day is the only day that matters |
| `cqrs-15` | Do I need full event sourcing? | Not on day one — start with the seven fundamentals |
