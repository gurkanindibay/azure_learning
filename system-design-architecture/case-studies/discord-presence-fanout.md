---
type: System Design
title: "Discord Presence at 200M Users — Key Takeaways"
description: "Presence is a fanout problem, not a storage problem: WebSocket gateways, pub/sub between gateways, lazy subscriptions, heartbeats, and gateway failure recovery with concrete math."
timestamp: 2026-07-04T00:00:00Z
---

# Discord Presence at 200M Users — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [How Discord Handles 200M Users Going Online at Once](../../articles/case-studies/discord-presence-200m-users.md) — by The Speedcraft Lab (Jul 2026)
> **Purpose**: Extract the presence system design pattern: why it's a fanout problem, the five-step architecture, lazy subscriptions as the scaling key, and the failure recovery strategy.

> **Also see**: [News Feed — Key Takeaways](news-feed.md), [Real-Time Messaging System Design](../messaging/real-time-messaging.md), [Message Brokers & Async](../messaging/message-brokers-async.md)
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md), [Messaging](../../reference-dictionary/messaging.md), [API Design](../../reference-dictionary/api-design.md)
> **Taxonomy Reference**: §3.3 Event-Driven & Messaging, §7.1 Reliability & Resilience

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`feed-06`](#feed-06-presence-is-a-fanout-problem-not-a-storage-problem) | Presence Is a Fanout Problem, Not a Storage Problem | 1 status flip × 100K watchers = billions of notifications/hour — optimize fanout before storage |
| [`feed-07`](#feed-07-the-five-step-presence-architecture) | The Five-Step Presence Architecture | Kill polling → Stateful gateways → Pub/sub → Heartbeats → Lazy subscriptions |
| [`feed-08`](#feed-08-lazy-subscriptions--bounding-fanout) | Lazy Subscriptions — Bounding Fanout | Subscribe to what's on screen (50–200 entities), not the entire social graph |
| [`feed-09`](#feed-09-the-presence-fanout-formula) | The Presence Fanout Formula | events/sec = users × toggles/hr ÷ 3600; fanout = events × (friends + server members); bound with lazy subs |
| [`feed-10`](#feed-10-gateway-failure-storms) | Gateway Failure Storms | 100K sessions migrating → presence storm; handle with exponential backoff + event deduplication |

---

## feed-06: Presence Is a Fanout Problem, Not a Storage Problem

| | |
|:---|:---|
| **Problem** | Candidates design presence as a database column (`is_online = true/false`) with polling, then discover at scale that 10M clients polling every 5 seconds = 2M requests/sec — 99% returning unchanged data. |
| **Root cause** | Treating presence as a CRUD state problem when it's fundamentally an event amplification problem: 1 user going online produces N notifications where N is everyone who cares. |

**Strategy — Reframe before designing:**

```
Presence = Fanout, not Storage

Polling approach (naive):
  10M clients × 1 poll/5s = 2M req/s → collapses at scale

Fanout approach (correct):
  1 status change → N push notifications
  N = friends + members of shared servers
  For Discord: N ≈ 100,000 watchers per active user
```

**The three-tier decision framework:**

| Social Graph Size | Update Rate | Strategy |
|:---|:---|:---|
| Small | Rare | Broadcast everything — simplest, works |
| Large | Moderate | Push only to active subscribers; lazy-subscribe based on what's rendered |
| Massive | High | Subscription management itself is the constraint; fanout is bounded by screen real estate |

**Tradeoff**: The fanout model trades storage simplicity for delivery efficiency. The database approach works at small scale (<10K concurrent) but the reframe to fanout is what unlocks 200M-user scale.

> **Also see**: [feed-01: Hybrid Fanout](news-feed.md#feed-01), [broker-01: Broker Selection](../messaging/message-brokers-async.md#broker-01)

---

## feed-07: The Five-Step Presence Architecture

| | |
|:---|:---|
| **Problem** | A presence system that works at 10K concurrent users collapses at 10M — each architectural shortcut has a different failure threshold. |
| **Root cause** | No single bottleneck; the system degrades layer by layer. Drop any one of the five steps and the system fails at a predictable scale boundary. |

**Strategy — Build in this order; each step removes one failure mode:**

| Step | Component | What It Solves | Failure If Skipped |
|:---|:---|:---|:---|
| 1. **Kill polling** | Persistent WebSocket per client to gateway | Eliminates 2M req/s polling overhead | Polling saturates API at ~100K concurrent users |
| 2. **Stateful gateways** | Gateway holds live sessions in memory (Elixir) | Knows who is connected, their status, their subscriptions | Stateless gateways force DB round-trips per event |
| 3. **Pub/sub between gateways** | Internal message bus (pub/sub system) | Gateway A publishes status change; Gateway B receives if it holds a subscriber | Gateways can't discover each other; events are siloed |
| 4. **Heartbeats** | Client pings every 30–60s; miss 2 = offline | Detects dead connections faster than TCP timeout | Online states leak for hours; users see "3 days online" |
| 5. **Lazy subscriptions** | Subscribe to visible entities only (50–200 on screen) | Bounds fanout to screen real estate, not social graph | Fanout grows with graph size, not concurrent users |

**Tradeoff**: Stateful gateways mean gateway failure is expensive (session migration storms). This is accepted because the operational simplicity of in-memory state is worth the failure-mode complexity — see [feed-10](#feed-10-gateway-failure-storms).

> **Also see**: [WebSocket](../../reference-dictionary/api-design.md#websocket), [Presence Service](../../reference-dictionary/architecture-patterns.md#presence-service), [API Gateway](../../reference-dictionary/networking.md#api-gateway)

---

## feed-08: Lazy Subscriptions — Bounding Fanout

| | |
|:---|:---|
| **Problem** | Naive fanout multiplies every status event by the full social graph: 833 events/s × 100 friends × 5,000 server members = millions of push messages per second. |
| **Root cause** | Subscribing to presence for every user the client might theoretically care about, rather than the small slice currently rendered on screen. |

**Strategy — Subscribe to what's visible, not what exists:**

```
Without lazy subscriptions:
  fanout = events/s × (avg_friends + avg_server_members)
  fanout = 833 × (100 + 5,000) = 4.2M pushes/s  ← collapses

With lazy subscriptions:
  fanout = events/s × entities_on_screen
  fanout = 833 × 150 = 125K pushes/s  ← comfortable
```

| Without Lazy Subs | With Lazy Subs |
|:---|:---|
| Subscribe to all friends + all server members | Subscribe to visible friends list + visible chunk of member list + active DMs |
| Fanout scales with social graph size | Fanout scales with concurrent user count |
| 1M users with large servers → millions of pushes/s | 1M users → ~125K pushes/s regardless of graph |
| Breaks at ~50K concurrent | Holds at millions of concurrent |

**When subscriptions update**: On scroll (member list pagination), on DM open/close, on friend list expand/collapse. The subscription set is dynamic and small.

**Tradeoff**: Lazy subscriptions add client-side subscription management complexity. The client must track what's visible and issue subscribe/unsubscribe calls as the viewport changes. This is accepted because it's the only way to decouple fanout from social graph size.

> **Also see**: [feed-02: Timeline Cache](news-feed.md#feed-02), [broker-10: Partition Key Selection](../messaging/message-brokers-async.md#broker-10)

---

## feed-09: The Presence Fanout Formula

| | |
|:---|:---|
| **Problem** | Engineers reach for a database without first doing the math on what happens when every status change fans out to every interested party. |
| **Root cause** | The arithmetic is simple but skipping it leads to architecture designed for the wrong order of magnitude. |

**Strategy — Apply this formula before choosing any architecture:**

```text
Step 1: Event rate
  events/sec = (concurrent_users × status_changes_per_hour) ÷ 3,600

  Example: 1M users × 3 toggles/hr ÷ 3,600 = 833 events/sec

Step 2: Naive fanout
  push_msgs/sec = events/sec × (avg_friends + avg_server_members)

  Example: 833 × (100 + 1,000) = 916K pushes/sec

Step 3: Lazy fanout (bounded)
  push_msgs/sec = events/sec × entities_on_screen

  Example: 833 × 150 = 125K pushes/sec
```

**Decision matrix:**

| events/sec | Naive fanout | Lazy fanout | Verdict |
|:---|:---|:---|:---|
| <100 | <10K | <1K | Polling or broadcast works |
| 100–1,000 | 10K–1M | 1K–100K | Fanout with lazy subscriptions |
| >1,000 | >1M | >100K | Subscription management is the bottleneck |

**The universal applicability**: Same math works for typing indicators, read receipts, live cursors (collaborative editors), and viewer counts (live streams).

**Tradeoff**: The formula is deliberately imprecise — it gives order-of-magnitude guidance, not exact numbers. Real systems need load testing, but the formula tells you which architectural tier you're in before you write a line of code.

> **Also see**: [sdi-05: Back-of-the-Envelope Math](../system-design-interview/interview-roadmap.md#sdi-05-back-of-the-envelope-math), [Back-of-the-Envelope Estimation](../../reference-dictionary/architecture-patterns.md#back-of-the-envelope-estimation)

---

## feed-10: Gateway Failure Storms

| | |
|:---|:---|
| **Problem** | When a gateway server dies, 100,000 sessions migrate to its neighbours simultaneously — every reconnect republishes status, every subscription rebuilds, creating a flood of events. |
| **Root cause** | Stateful gateways trade failure-mode complexity for operational simplicity; the trade is worth it, but the failure mode must be designed for. |

**Strategy — Two mechanisms, both required:**

| Mechanism | How It Works | What It Solves |
|:---|:---|:---|
| **Exponential backoff on reconnect** | Clients retry with jittered exponential backoff (100ms, 200ms, 400ms, 800ms…) | Prevents all 100K clients from hitting neighbours at the same millisecond |
| **Event deduplication on subscriber side** | Gateway tracks last-seen event ID per subscription; discards duplicates | Prevents a client seeing the same friend "come online" 3 times during the storm |

**The presence storm lifecycle:**

```text
Gateway dies
  → 100K sessions detect disconnection
  → Clients reconnect with exponential backoff (spread over seconds, not milliseconds)
  → Each reconnect republishes user status
  → Each reconnect rebuilds subscriptions
  → Subscriber gateways receive flood of events
  → Deduplication drops redundant events
  → Storm subsides within 10-30 seconds
```

**Tradeoff**: The storm is accepted as inevitable — you cannot prevent it, only manage its blast radius. Exponential backoff trades reconnect speed for system stability. Deduplication trades per-subscription state overhead (tracking last event ID) for correctness during failure.

> **Also see**: [resilience-01: Retry Storms](../resilience/resilience-patterns.md#resilience-01), [cb-01: Slow-Call Rate](../resilience/circuit-breaker-honesty.md#cb-01), [Bulkhead](../../reference-dictionary/resilience.md#bulkhead)
