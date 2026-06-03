# 9. Stream Processing (Apache Flink)

> **Parent**: [System Design Interview Reference](README.md)  
> **Source**: [Apache Flink from 10,000 Feet](../articles/medium/apache-flink-10000-feet/01-apache-flink-from-10000-feet.md)

---

## flink-01: Lambda Architecture — Two Systems, Two Codebases

> **Source**: [Apache Flink from 10,000 Feet](../articles/medium/apache-flink-10000-feet/01-apache-flink-from-10000-feet.md) — "The Problem" & "The Key Insight"

| | |
|:---|:---|
| **Problem** | Maintaining separate batch and streaming systems for the same data, doubling operational complexity |
| **Root cause** | Streaming for real-time + batch for historical accuracy = two codebases, two pipelines, two sets of bugs |
| **Symptoms** | Same business logic written twice; batch and streaming results disagree; reconciliation is manual |

**Strategy**:

| Approach | Description | When to use |
|:---|:---|:---|
| **Lambda Architecture** | Fast path (streaming) + batch path (historical) + serving layer | Legacy — being replaced |
| **Kappa Architecture** | Single streaming pipeline (Kafka + Flink) for both real-time and batch | Modern standard |
| **Unified engine (Flink)** | Same operators, same codebase — just point at different time windows of the same stream | When you need to eliminate duality entirely |

**Key insight**: Batch data is just a stream that stopped flowing. Your 6-month historical data and your 6-second real-time data are the same JSON events at different time windows. One engine can handle both.

> **Azure**: Azure Stream Analytics (real-time) + Azure Data Lake Analytics (batch) → converging toward unified via Azure Synapse | **General**: [Lambda vs Kappa Architecture](../../architecture-general/04-data-analytics-ai-architecture/)

---

## flink-02: Batch as a Special Case of Streaming

> **Source**: [Apache Flink from 10,000 Feet](../articles/medium/apache-flink-10000-feet/01-apache-flink-from-10000-feet.md) — "On Unified Batch and Stream Processing"

| | |
|:---|:---|
| **Problem** | Confusion about why a "streaming" engine can also do "batch" |
| **Root cause** | Batch and streaming are seen as fundamentally different paradigms |
| **Symptoms** | Teams maintain Spark for batch and Flink/Storm for streaming unnecessarily |

**The core insight**:

```
Streaming (Pipelined):  Op1 ████ → Op2 ████ → Op3 ████   (all run simultaneously)
Batch (Blocked):        Op1 ████ DONE → Op2 ████ DONE → Op3 ████ DONE  (sequential)
```

| | Streaming | Batch |
|---|---|---|
| **Data exchange** | Records flow immediately (pipelined) | "Dam" between operators — all records held until upstream finishes |
| **Operators run** | Simultaneously | Sequentially |
| **Latency** | Milliseconds | Minutes (but more efficient for massive fixed datasets) |
| **Operator code** | `userActivity.aggregate(...)` | **Same code** — identical |
| **State, serialization** | Checkpointing to durable storage | Same checkpointing |

> **Analogy**: Assembly line (streaming) vs catering kitchen (batch). Same recipes, same ingredients — different timing of handoffs between stations.

**Key insight**: There is no separate batch engine in Flink. The **only** difference is how data moves between operators — pipelined (immediate) vs blocked (damed). Everything else is identical.

> **Azure**: Azure Stream Analytics for streaming; Azure Synapse Spark pools for batch — separate engines, unlike Flink's unified approach | **General**: [Stream Processing Patterns](../../architecture-general/04-data-analytics-ai-architecture/)

---

## flink-03: Stateful Stream Processing with Exactly-Once Guarantees

> **Source**: [Apache Flink from 10,000 Feet](../articles/medium/apache-flink-10000-feet/01-apache-flink-from-10000-feet.md) — "State" & "Fault Tolerance"

| | |
|:---|:---|
| **Problem** | Stream processors that treat each event in isolation cannot detect patterns over time |
| **Root cause** | Most early streaming systems (Storm, early Kafka Streams) were stateless |
| **Symptoms** | Cannot answer "what did this user do in the last 10 minutes?" — each event processed alone |

**Strategy**:

| Capability | How Flink Does It |
|:---|:---|
| **State** | Per-operator hash maps, counters, lists — declared explicitly, managed by Flink |
| **Fault tolerance** | Periodic distributed snapshots (checkpoints) to durable storage |
| **Exactly-once** | On crash: roll back to last snapshot + replay only events since that snapshot (partial re-execution) |
| **The mechanism** | Asynchronous Barrier Snapshotting (ABS) — barrier markers flow through the stream; operator snapshots state on receipt, forwards barrier, continues processing |

```
Events → [barrier] → Operator snapshots state → forwards barrier
                                                  ↓
                                     Continues processing records
                                     (no pause, no freeze)
```

**Key insight**: Flink's state feels as reliable as writing to a database, with the performance of an in-memory hash map. Counts won't be doubled after crash recovery.

> **Azure**: Azure Stream Analytics supports reference data joins (limited state); Cosmos DB change feed for stateful event sourcing | **General**: [Event Sourcing Pattern](../../architecture-general/04-data-analytics-ai-architecture/)

---

## flink-04: Windowing — Aggregating Infinite Streams

> **Source**: [Apache Flink from 10,000 Feet](../articles/medium/apache-flink-10000-feet/01-apache-flink-from-10000-feet.md) — "Windows"

| | |
|:---|:---|
| **Problem** | An infinite stream has no natural "end" — when do you emit an aggregation result? |
| **Root cause** | Batch processing has a natural completion point; streams don't |
| **Symptoms** | Can't compute "top 10 products in last 5 minutes" without knowing when "last 5 minutes" ends |

**Strategy** — Window Types:

| Window | Behavior | Example Use Case |
|:---|:---|:---|
| **Tumbling** | Fixed-size, non-overlapping (every 5 min) | "Top products each hour" |
| **Sliding** | Fixed-size, overlapping (last 5 min, recompute every 1 min) | "Trending right now" — recommendation engine |
| **Session** | Activity-based, gap timeout ends the window | "User session: from first click to 10 min of inactivity" |
| **Global** | All events, ended by custom trigger | Rare — full stream summarization |

**Key insight**: A window is a bounded chunk sliced from an infinite stream. You define the slice boundary, Flink groups events into it, and emits results when the window completes.

> **Azure**: Azure Stream Analytics supports tumbling, hopping (sliding), and session windows natively | **General**: [Windowed Aggregation Patterns](../../architecture-general/04-data-analytics-ai-architecture/)

---

## flink-05: Asynchronous Barrier Snapshotting (ABS) — Fault Tolerance Without Pausing

> **Source**: [Apache Flink from 10,000 Feet](../articles/medium/apache-flink-10000-feet/01-apache-flink-from-10000-feet.md) — "On Fault Tolerance"

| | |
|:---|:---|
| **Problem** | How do you snapshot distributed operator state without pausing the entire pipeline? |
| **Root cause** | Naive stop-the-world snapshots would break real-time latency SLAs |
| **Symptoms** | Streaming pipeline pauses every checkpoint interval — unacceptable for sub-second latency |

**How ABS Works**:

```
1. JobManager injects barrier into source stream
2. Barrier flows through operators like a regular record
3. When Op1 receives barrier → snapshots its state → forwards barrier to Op2
4. Op2 receives barrier → snapshots its state → forwards to Op3
5. All operators continue processing records during snapshot (non-blocking)
6. When all barriers reach sinks → checkpoint complete
```

| Property | How ABS Achieves It |
|:---|:---|
| **Non-blocking** | Barriers injected alongside data; processing continues uninterrupted |
| **Exactly-once** | Checkpoint contains offset + state; recovery replays from exact offset |
| **Partial re-execution** | Only operators downstream of the failure restart; upstream continues from snapshot |
| **Tunable** | Checkpoint interval controls max reprocessing window |

**Key insight**: ABS is what makes Flink's exactly-once guarantee practical at scale. Without it, you'd have to choose between correctness and performance.

> **Azure**: Azure Stream Analytics handles checkpointing transparently; Event Hubs capture provides durable replay | **General**: [Checkpointing & Recovery Patterns](../../architecture-general/07-reliability-performance-operations/)

---

## Mental Model: Stream Processing Architecture

| Concept | What It Is | Why It Matters |
|:---|:---|:---|
| **Unified engine** | Same code for batch and streaming | One codebase, no reconciliation |
| **Operators + Streams** | Processing nodes connected by data flows | The DAG is the program |
| **Managed state** | In-memory data that survives crashes | Context across events without a database |
| **Windows** | Bounded slices of infinite streams | Makes aggregation tractable |
| **Barrier snapshots** | Non-blocking distributed checkpointing | Exactly-once without pausing |

---

## Pattern Selection Guide

| Problem | Strategy | Ref |
|:---|:---|:---:|
| "Two systems, two codebases for same data" | Unified engine (Flink): same operators, batch or streaming mode | [`flink-01`](#flink-01-lambda-architecture--two-systems-two-codebases) |
| "How does 'streaming' engine do 'batch'?" | Blocked data exchange — same code, sequential execution | [`flink-02`](#flink-02-batch-as-a-special-case-of-streaming) |
| "Need to remember what happened before this event" | Managed state with checkpointing and exactly-once recovery | [`flink-03`](#flink-03-stateful-stream-processing-with-exactly-once-guarantees) |
| "When do I emit results from an infinite stream?" | Windows: tumbling, sliding, session, global | [`flink-04`](#flink-04-windowing--aggregating-infinite-streams) |
| "Snapshots pause my pipeline" | Asynchronous Barrier Snapshotting — non-blocking | [`flink-05`](#flink-05-asynchronous-barrier-snapshotting-abs--fault-tolerance-without-pausing) |

---

> **Azure mapping**: Azure Stream Analytics (managed Flink-like service) | Azure Event Hubs + Stream Analytics for Kafka-to-Flink equivalent | [Azure HDInsight Flink](https://learn.microsoft.com/en-us/azure/hdinsight/hdinsight-apache-flink-overview) for self-managed clusters