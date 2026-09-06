---
type: System Design
title: "Netflix Edge Caching — Key Takeaways"
description: "How Netflix pre-positions content at the ISP edge and uses buffer-aware adaptive bitrate streaming to eliminate buffering at 260M+ scale."
generated: { by: process:okf-migrate, at: 2026-07-17T00:00:00Z }
---

# 31. Netflix Edge Caching — Key Takeaways

> **Parent**: [System Design Architecture](../index.md)
> **Source**: [How Netflix Handles 260 Million Concurrent Streams Without Buffering](../../articles/caching/netflix-open-connect-edge-caching.md)
> **Related**: [Caching Architecture](index.md), [Redis Internals](redis-internals.md), [Hot Keys & Skewed Workloads](hot-keys-skewed-workloads.md)
> **Dictionary**: [CDN](../../reference-dictionary/networking.md#cdn), [Edge Pre-positioning](../../reference-dictionary/caching.md#edge-pre-positioning), [Buffer-based Bitrate Adaptation](../../reference-dictionary/media-processing.md#buffer-based-bitrate-adaptation), [Quality Ladder](../../reference-dictionary/media-processing.md#quality-ladder)
> **Azure Services**: [Azure Front Door](../../architecture-azure/networking/front-door/), [Azure CDN](../../architecture-azure/networking/)
> **Taxonomy Reference**: §7.3 Caching Strategies

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [cache-26](#cache-26-pull-through-cdn-collapses-under-premiere-load) | Pull-through CDN collapses under premiere load | Pre-position at ISP edge |
| [cache-27](#cache-27-first-users-pay-the-cache-miss-tax) | First users pay the cache-miss tax | Quiet-hours pre-warming |
| [cache-28](#cache-28-cloud-egress-costs-break-the-business-model) | Cloud egress costs break the business model | Control-plane / data-plane split |
| [cache-29](#cache-29-throughput-only-abr-guesses-wrong-under-variance) | Throughput-only ABR guesses wrong under variance | Buffer-aware adaptation |
| [cache-30](#cache-30-reacting-to-demand-is-already-too-late) | Reacting to demand is already too late | Predict and pre-compute |

---

## cache-26: Pull-through CDN collapses under premiere load

| | |
|:---|:---|
| **Problem** | A pull-through CDN holds none of a new release when millions of users request it simultaneously. Every request is a cache miss, and all of them hammer the origin at once — the system fails hardest at peak demand. |
| **Root cause** | On-demand cache population couples the cache-fill event to the first user request. The cache is coldest when demand is hottest. |

**Strategy**: Pre-position content at ISP-level edge appliances before demand arrives. Netflix ships physical Open Connect Appliances into ISP data centers and fills them during nightly quiet hours based on predicted regional demand. When a premiere drops, it is already warm on thousands of distributed caches — there is no single origin to overwhelm.

**Tradeoff**: Requires physical hardware deployment and maintenance across thousands of ISP sites; demand prediction must be accurate to avoid wasting storage on unpopular titles. The operational complexity of managing a global fleet of appliances is significant, but it eliminates the central bottleneck and reduces transit costs for both Netflix and ISPs.

---

## cache-27: First users pay the cache-miss tax

| | |
|:---|:---|
| **Problem** | In a lazy-filled cache, the first users to request new content experience the worst performance — they pay the cold-start penalty while the cache warms up. At scale, this means your most eager users get the worst experience. |
| **Root cause** | Cache population is reactive rather than predictive. The fill event is gated on the first request, so early adopters always hit the slow path. |

**Strategy**: Fill caches proactively during quiet hours before users arrive. Predict tomorrow's demand and pre-load content so that the cache is warm before the first request. This applies beyond video: warm CDN caches at deploy time, pre-compute dashboard aggregates on a schedule, and pre-render expensive pages.

**Tradeoff**: Proactive filling consumes storage and bandwidth during off-peak hours for content that may never be requested. Prediction accuracy directly affects efficiency — over-predicting wastes resources; under-predicting leaves cold spots. The scheduling window (quiet hours) imposes a latency floor on content availability.

---

## cache-28: Cloud egress costs break the business model

| | |
|:---|:---|
| **Problem** | Serving 300+ Tbps of video from cloud data centers would generate egress costs far exceeding any viable subscription revenue. The public internet backbone cannot economically carry that volume from a few central locations. |
| **Root cause** | Cloud pricing models charge for egress bandwidth, and peering links have finite capacity. A centralized data plane concentrates both cost and congestion at the same bottleneck. |

**Strategy**: Split the architecture into a cloud-hosted control plane (authentication, recommendations, DRM, steering) and an edge-hosted data plane (video delivery from ISP-local appliances). The control plane lives where flexibility and elasticity are cheap (AWS); the data plane lives where the bytes are (Open Connect Appliances inside ISP networks). Netflix moved everything to AWS by 2016 but deliberately kept its heaviest workload out of the cloud.

**Tradeoff**: Two distinct infrastructure domains to manage with different operational models, deployment cadences, and failure modes. The edge hardware must be self-designed and self-maintained rather than relying on cloud abstractions. However, the cost savings from eliminating cloud egress at petabyte scale justify the operational investment.

---

## cache-29: Throughput-only ABR guesses wrong under variance

| | |
|:---|:---|
| **Problem** | Adaptive bitrate streaming that only measures throughput picks the wrong quality level when network conditions fluctuate rapidly — a brief dip causes a quality downgrade that takes too long to recover from, or worse, causes rebuffering. |
| **Root cause** | Throughput is a point-in-time measurement that does not capture the playback buffer's ability to absorb short-term variance. Without buffer awareness, the player overreacts to transient conditions. |

**Strategy**: Use buffer-based bitrate adaptation — monitor both real throughput and the playback buffer depth (seconds of video queued). Start playback at a conservative bitrate, climb within seconds as the buffer fills, and step down only when the buffer actually runs low, not when throughput momentarily dips. Netflix's SIGCOMM 2014 research with Stanford showed this cuts rebuffering sharply compared to throughput-only adaptation.

**Tradeoff**: More complex client logic that must track buffer state in addition to throughput. The algorithm needs per-title encoding ladders so that bitrate steps correspond to meaningful quality differences. Codec efficiency (e.g., AV1 rollout) compounds the benefit — fewer bits needed per quality rung means the buffer drains slower under poor conditions.

---

## cache-30: Reacting to demand is already too late

| | |
|:---|:---|
| **Problem** | Systems designed around request-triggered work — compute on request, fetch on request, cache on miss — degrade at scale because peak demand coincides with peak system load. The busiest moment is also the moment the system does the most work. |
| **Root cause** | The request is treated as the start of work rather than the final step in a pre-computed pipeline. This couples load to latency: more users means more work per user. |

**Strategy**: Invert the timeline — move work to before the request. Netflix chooses the file, encodes it into a per-title quality ladder, and copies it to an edge appliance all before the user presses play. The request triggers only a small API call, a manifest fetch, and a short local transfer. The general pattern: predict demand, pre-position data, pre-compute results, then let the client adapt to whatever residual variance remains.

**Tradeoff**: Requires prediction infrastructure and scheduled processing pipelines. Pre-computed results may be slightly stale — acceptable for video catalog metadata and read-heavy dashboards, unacceptable for transactional systems. The storage footprint grows with pre-positioned content, and prediction errors waste capacity. But at scale, the gap between reactive and proactive is the difference between serving 65M concurrent streams and collapsing under them.
