---
type: Reference
title: "System Design Diagram Enrichment Progress"
description: "Per-document status tracker for Archify diagram enrichment."
timestamp: 2026-08-30T00:00:00Z
---

# System Design Diagram Enrichment Progress

Status legend: `Not started` means no artifact exists; `Spec validated` means the Archify JSON passed showcase validation; `Complete` means JSON, HTML, PNG embed, interactive link, and source-document validation are complete.

## Original Cases

| Document | Primary diagram | Secondary diagram | Status |
|:---|:---|:---|:---|
| `part-2-url-shortener-system-design.md` | Global redirect architecture | Redirect and analytics sequence | Complete (primary) |
| `part-2-news-feed-system-design.md` | Hybrid fan-out architecture | — | Complete |
| `part-3-e-commerce-platform-system-design.md` | Checkout saga | — | Complete |
| `part-3-real-time-messaging-system-design.md` | Event-driven messaging architecture | Message delivery sequence | Complete (primary) |

## ByteByteGo Chapters

| Chapter | Primary diagram | Status |
|:---|:---|:---|
| 02 Scale From Zero To Millions Of Users | Scale evolution architecture | Complete |
| 05 Design A Rate Limiter | Distributed rate limiting workflow | Complete |
| 06 Design Consistent Hashing | Ring membership and request routing | Complete |
| 07 Design A Key-Value Store | Partitioned key-value architecture | Complete |
| 08 Design A Unique ID Generator | Distributed ID generation workflow | Complete |
| 09 Design A URL Shortener | Redirect architecture | Complete |
| 10 Design A Web Crawler | Crawl frontier and worker pipeline | Complete |
| 11 Design A Notification System | Notification delivery architecture | Complete |
| 12 Design A News Feed System | Fan-out architecture | Complete |
| 13 Design A Chat System | Real-time chat architecture | Complete |
| 14 Design A Search Autocomplete System | Suggestion generation pipeline | Complete |
| 15 Design YouTube | Upload and video delivery architecture | Not started |
| 16 Design Google Drive | File synchronization architecture | Not started |
| 17 Proximity Service | Geo-index query architecture | Not started |
| 18 Nearby Friends | Location-update and discovery flow | Not started |
| 19 Google Maps | Map-tile and routing architecture | Not started |
| 20 Distributed Message Queue | Producer, broker, and consumer architecture | Not started |
| 21 Metrics Monitoring and Alerting System | Metrics ingestion and alert evaluation | Not started |
| 22 Ad Click Event Aggregation | Stream aggregation data flow | Not started |
| 23 Hotel Reservation System | Reservation consistency workflow | Not started |
| 24 Distributed Email Service | Email delivery pipeline | Not started |
| 25 S3-like Object Storage | Object metadata and blob storage architecture | Not started |
| 26 Real-time Gaming Leaderboard | Ranking update architecture | Not started |
| 27 Payment System | Payment processing architecture | Complete |
| 28 Digital Wallet | Wallet ledger and transfer workflow | Complete |
| 29 Stock Exchange | Order matching architecture | Complete |

## Source Articles

| Document | Primary diagram | Secondary diagram | Status |
|:---|:---|:---|:---|
| `million-notifications-system-design.md` | Notification architecture | Delivery and retry sequence | Not started |
| `amazon-interview-question-design-a-delayed-job-scheduler.md` | Durable scheduler architecture | Job state and lease lifecycle | Not started |
| `customer-support-ai-platform-system-design-interview.md` | Support platform architecture | Ticket to AI or human escalation | Not started |
| `resumable-uploads-chunking-large-files.md` | Resumable-upload architecture | Upload session lifecycle | Not started |
| `real-time-leaderboard-design.md` | Leaderboard architecture | — | Not started |
| `design-system-interviews.md` | Seven-phase interview workflow | — | Not started |
| `complete-system-design-interview-guide-2026.md` | Constraint-driven decision workflow | — | Not started |
| `real-world-system-design-scenarios-part-1.md` | Scenario-family decision map | — | Not started |
| `22-design-interview-questions/01-22-scenario-based-system-design-questions.md` | Scenario-family decision map | — | Not started |