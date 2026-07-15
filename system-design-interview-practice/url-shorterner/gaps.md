---
type: System Design Review
title: "URL Shortener Interview Case — Open Gaps"
description: "Missing, unclear, or incomplete points for the latest URL shortener case revision"
timestamp: 2026-07-15T00:00:00Z
---

# URL Shortener Interview Case — Open Gaps

> **Source case**: [URL Shortener Interview Case](url-shorterner.md)
> **Companion review**: [URL Shortener Interview Case Review](review.md)

This file lists the points that are still missing, unclear, or incomplete in the latest revision of the URL shortener case. Use it as a checklist when preparing the next iteration.

## Correctness and concurrency

- [x] **Explain how the Snowflake-style generator assigns unique worker/region IDs.** Without explicit region-ID assignment, two regions could theoretically issue overlapping IDs after clock skew or misconfiguration.
- [x] **State the uniqueness guarantee for custom aliases.** Custom aliases cannot come from the regional Snowflake pool; they need an authoritative region or a global conditional write.
- [x] **Clarify the conditional-write strategy for custom aliases.** Is it a Cassandra LWT (`IF NOT EXISTS`), a global lock, or routing to a single owner region? What happens on collision?
- [x] **Correct the statement that `CL=ONE` assures uniqueness.** The consistency level only controls acknowledgment; uniqueness comes from the disjoint ID allocation for generated codes and from conditional writes for custom aliases.
- [x] **Describe creation idempotency.** If a client retries `POST /v1/urls` after a timeout, can it create two different short URLs for the same original URL? An idempotency key is needed.

## Latency and targets

- [x] **Split the 10 ms p99 target by scope.** Distinguish between CDN/edge response time, regional service-processing time, and global end-to-end latency.
- [x] **State what happens during a cache miss.** Quantify the expected latency when neither CDN nor Redis has the mapping.
- [x] **Define the acceptable creation latency.** The case says there is no hard metric, but an interview answer should still give a reasonable target.

## Storage and data model

- [x] **Update storage estimates.** 50 million × 90 bytes is ~4.5 GB raw, not 2.4 GB. Include replication, compaction, bloom filters, and indexes.
- [x] **Update click-stat estimates.** 100 million × 40 bytes is ~4 GB raw per day. With replication and overhead, monthly storage is likely 500 GB–1 TB before compression and archival.
- [x] **Drop or justify the auto-incrementing bigint `id`.** It is not natural for active-active Cassandra and duplicates `public_id`/`url_part`.
- [x] **Choose one public identifier.** `public_id`, `url_part`, and `id` overlap. If `url_part` is the external key, the others may be redundant.
- [ ] **Define the Cassandra table design.** Show partition keys, clustering columns, and how queries are satisfied.
- [x] **Explain day/hour bucket strategy for analytics.** Avoid one unbounded partition per short code.

## Caching and hot keys

- [x] **Add explicit CDN/edge cache placement.** Redis alone cannot absorb a viral link.
- [x] **Describe cache TTL strategy.** How long are redirects cached at the edge, in Redis, and in the browser?
- [x] **Add hot-key protection.** Include request coalescing, stale-while-revalidate, or hot-key replication for celebrity/campaign links.
- [ ] **Define cache-invalidation behavior.** What happens when a link is deleted, expires, or changes redirect type? *(Only `410` on expiry/delete is stated; CDN/Redis invalidation is not described.)*

## API and contracts

- [x] **Add HTTP methods and request/response bodies for all endpoints.**
- [x] **Define `404` vs `410` behavior.** A non-existent code returns `404`; an expired code should return `410 Gone` if the policy is never-reuse.
- [x] **Add `409 Conflict` semantics for custom-alias collisions.**
- [x] **Add idempotency-key support to URL creation.**
- [x] **Specify authorization rules for statistics.** Only the link owner (or an admin) should view stats; knowing the short code is not enough.
- [ ] **Clarify whether custom aliases share the same 8-character namespace.** If not, define the allowed format. *(Only “up to 50 chars” is stated; namespace relationship is unclear.)*

## Multi-region and failover

- [x] **Explain regional ownership of a mapping.** If a user creates a link in region A and region B receives a redirect, where is the authoritative record?
- [x] **Describe failover behavior.** If the home region of a short code fails, how does another region serve redirects without strong consistency?
- [x] **State how new codes are allocated during regional failover.** Does the failed region's generator stop? Is there a quorum check?

## Security and abuse

- [x] **Add destination URL validation.** Block unsafe schemes such as `javascript:`, `file:`, and private IP ranges. *(Threat-intelligence scanning is mentioned, but scheme/IP blocking is not explicit.)*
- [x] **Add rate limiting per identity type.** Anonymous users, authenticated users, and IPs should have different quotas.
- [x] **Add per-account creation quotas.**
- [x] **Add malware/phishing checks.** At least mention URL reputation scanning or user reporting.
- [x] **Add abuse-reporting flow.** How does a link get flagged, reviewed, and blocked? *(Scheduled revalidation and block/delete is described, but explicit user-reporting flow is missing.)*

## Observability

- [x] **Distinguish service metrics from business metrics.** Redirect latency is a service metric; clicks per URL is a business metric.
- [x] **Add alerting thresholds.** When do rate-limit, abuse-block, or hot-key alerts fire?
- [ ] **Add tracing across redirect, creation, and analytics paths.**

## Expiration semantics

- [x] **State the final reuse policy explicitly.** The case says never reuse after expiration, which is correct, but also mentions tombstone-based reuse as optional. Pick one for the MVP.
- [x] **Quantify the tombstone period if reuse is ever allowed.** It must exceed every possible cache lifetime.
- [x] **Align default TTL with redirect status code.** Default 30-day links should not use `301`; use `302`/`307` for expiring links and reserve `301` for explicitly permanent links.

## Interview presentation

- [x] **Lead with correctness invariants.** State explicitly: every active short code maps to exactly one destination; creation is idempotent; expired codes are not ambiguously reused; analytics cannot delay redirects.
- [x] **Estimate viral-link traffic.** A single popular link can create orders-of-magnitude higher per-key load than the average peak.
- [x] **Summarize MVP trade-offs.** What is kept for launch and what is deferred?
