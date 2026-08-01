---
type: Article
title: "Uber Surge Pricing During Rain — System Design Deep Dive on Real-Time Demand Supply and Dynamic Pricing"
description: "How Uber computes dynamic surge pricing in real time during rain events — Kafka pipelines, geohash partitioning, sliding windows, EMA smoothing, and Redis-based state management at planetary scale."
source: "https://codefarm0.medium.com/uber-surge-pricing-during-rain-system-design-deep-dive-on-real-time-demand-supply-and-dynamic-f71fd58fdb03"
author: "Arvind Kumar"
published: 2026-07-19
created: 2026-08-01
---

# Uber Surge Pricing During Rain — System Design Deep Dive on Real-Time Demand Supply and Dynamic Pricing

> **Source**: [Medium — Arvind Kumar](https://codefarm0.medium.com/uber-surge-pricing-during-rain-system-design-deep-dive-on-real-time-demand-supply-and-dynamic-f71fd58fdb03)

This is one of those system design questions where the user experience and the backend complexity are inversely related.

The user sees a simple notification: "Prices are higher due to increased demand." Behind that one line, a real-time pipeline processes millions of events per second, computes demand and supply ratios across thousands of geographic regions, adjusts prices dynamically, and pushes updates to hundreds of millions of devices — all within seconds.

Interviewers love this question because it connects stream processing to a visible business outcome and reveals whether you understand:

- How real-time data pipelines ingest and process high-velocity events
- Why demand and supply must be measured per geographic region, not globally
- How dynamic pricing algorithms balance efficiency with fairness
- The role of Kafka as the backbone of real-time event-driven systems
- How surge pricing prevents market failure during supply-demand mismatches

## The Scenario

**Arvind (Interviewer):** It starts raining heavily in a city. Within minutes, Uber ride prices in affected areas surge to 3x. Users complain. Some understand. Some do not. How does this system work under the hood? And what would you build if you had to design it from scratch?

**Raj (Candidate):** Let me first clarify what surge pricing is trying to solve.

When it rains, more people want rides. At the same time, fewer drivers are on the road — some stop driving in bad weather. Demand goes up. Supply goes down. Without price adjustment, most riders would not find a ride at all. The market would fail.

Surge pricing solves this by raising prices until some riders decide to wait or take alternative transport, while more drivers are incentivized to enter the area. The system reaches a new equilibrium.

The engineering challenge is computing this equilibrium in real time, per geographic region, with millions of events streaming in every second.

### Basic Data Flow

Every rider action and every driver location update is an event published to Kafka. The pricing engine consumes these events continuously, not in batches.

### Defining a Region for Pricing

The city is divided into small geographic cells using **geohashing**.

For every cell, the pricing engine maintains two counters in Redis:

- **Demand**: Number of riders who opened the app or requested a ride in the last 5 minutes
- **Supply**: Number of available drivers in the cell (online and not on a trip)

The **surge multiplier** is the demand-supply ratio mapped to a price multiplier.

### Three Core Challenges at Scale

**Velocity**: Uber processes millions of location updates per second. Every driver sends location every 4 seconds. Every rider action is an event. The pricing engine must consume this firehose without falling behind.

**Staleness**: A driver location from 30 seconds ago is useless for pricing. If a driver left the region, the supply count must drop immediately. The system needs low end-to-end latency — from event ingestion to price update — ideally under 10 seconds.

**Oscillations**: If the surge multiplier updates too aggressively, it can cause wild price swings. Drivers rush to a surge zone, supply overshoots, demand crashes, prices drop, drivers leave, and the cycle repeats. The algorithm must smooth these transitions.

### Preventing Oscillations

Multiple mechanisms work together:

**Sliding Window**: The demand and supply counters are computed over a 5-minute sliding window, not instantaneously. This smooths out short-term fluctuations. Even if 50 riders open the app in one second, the window captures them as a trend rather than a spike.

**EMA Smoothing**: The surge multiplier itself is dampened. The new multiplier is not applied directly. Instead:

```c
final_multiplier = (alpha * computed_multiplier) + ((1 - alpha) * previous_multiplier)
```

Alpha is typically between 0.3 and 0.5. This creates an exponential moving average. Prices change smoothly instead of jumping from 1x to 3x instantly.

**Cooldown Period**: Once a surge multiplier is set for a geohash, it cannot change more than once per pricing cycle (typically 2 to 5 minutes). This prevents rapid see-sawing.

**Adjacency Adjustment**: Adjacent geohash cells influence each other. If zone A has 3x surge but zone B next to it has 1x, drivers flood into A and supply normalizes quickly. The algorithm considers neighboring zones when computing the final multiplier to avoid extreme local spikes that immediately self-correct.

### Kafka as the Data Backbone

Every event — rider app open, ride request, driver location update, trip start, trip end — goes to a Kafka topic.

```text
Topics:
  rider.requests      - Partitioned by geohash
  driver.locations    - Partitioned by geohash
  driver.status       - online / offline / on-trip
  trip.events         - started / completed / cancelled
  surge.updates       - Output topic for price changes
```

Partitioning by geohash is critical. It ensures all events for the same geographic region go to the same Kafka partition, which means a single stream processor can consume them in order without cross-region coordination.

The stream processor (Kafka Streams, Flink, or Samza) reads from these topics, maintains per-geohash state in memory or Redis, and outputs surge updates to a downstream topic.

### User Experience

The rider sees the surge multiplier before confirming the ride. The price shown includes the multiplier. Uber also shows a notification explaining the surge — "demand is high in your area" — to set expectations.

For drivers, the app shows a **surge heatmap**. Areas with higher multipliers are highlighted. This guides drivers toward high-demand zones. The heatmap updates every few minutes based on the latest pricing computation.

There is also a behavioral feedback loop. If riders consistently reject rides during surge, the algorithm slowly reduces the multiplier until riders start accepting again. If drivers avoid a surge zone because of traffic, the algorithm increases the multiplier further. The system is constantly seeking equilibrium.

### Complete Architecture

Key decisions:

- **Kafka partitioning by geohash**: Ensures all events for a region are processed by the same consumer. Simplifies state management.
- **Redis for real-time state**: Per-geohash counters are stored in Redis with TTL-based expiry. If a geohash stops receiving events, its counters decay to zero naturally.
- **Sliding window**: Demand and supply are measured over a 5-minute sliding window, not instantaneous counts. This smooths noise.
- **EMA smoothing**: Surge multiplier changes are dampened using exponential moving average. Prevents price whiplash.
- **Adjacency adjustment**: A zone's multiplier is influenced by neighboring zones to prevent extreme local spikes.
- **Cooldown**: Multiplier cannot change more than once per pricing cycle (2–5 minutes).
- **Dual delivery**: Prices are pushed to rider apps via WebSocket for real-time display and written to the dispatch queue for trip pricing.

### Monitoring

Key metrics to track:

1. **Surge multiplier distribution** — What percentage of geohashes are at 1x, 1.5x, 2x, 3x+? Maps to overall market health.
2. **Rider acceptance rate** — Percentage of riders who accept the surge price and book a ride. Dropping acceptance means the surge is too high.
3. **Driver movement into surge zones** — Are drivers responding to the price signal? If not, the multiplier needs adjustment.
4. **End-to-end latency** — Time from a rider opening the app to seeing the surge price. Target: under 10 seconds.
5. **Stream processing lag** — How far behind real-time is the Kafka consumer? Growing lag means the system is falling behind.
6. **Surge oscillation frequency** — How often does the multiplier for a geohash change by more than 0.5x within 5 minutes? High oscillation indicates inadequate smoothing.
7. **False surge events** — Times when surge was triggered but demand was not actually high (e.g., a bug or data pipeline glitch).

## Conclusion

Surge pricing is not just an algorithm — it is a real-time market feedback system operating at planetary scale.

The system must ingest millions of events per second, compute regional supply and demand with low latency, adjust prices smoothly without oscillations, and communicate those prices to millions of users in real time.

**The winning architecture**:

- **Kafka** for high-throughput event ingestion, partitioned by geohash for locality
- **Stream processor** (Kafka Streams / Flink) for windowed aggregations
- **Redis** for low-latency per-geohash state with TTL-based decay
- **EMA smoothing and adjacency adjustment** to prevent price whiplash
- **WebSocket push** for real-time delivery to rider and driver apps
- **Feedback loops** from acceptance rates and driver movement to continuously calibrate the model

The result is a system that, within seconds of rain starting in a city, adjusts prices to match the new reality of supply and demand.
