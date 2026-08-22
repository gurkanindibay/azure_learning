---
type: System Design Case
title: "Design a flash sale system"
description: "Black Friday is coming. Designing a system with extremely high concurrency, high availability and quick responsiveness needs to consider many aspects **all the way fromfrontend to backend**. See th..."
tags: [system-design]
timestamp: 2026-08-22T00:00:00Z
---

# Design a flash sale system

> **Source**: ByteByteGo — System Design compilation PDF

![Design a flash sale system](images/img-075.jpeg)

Black Friday is coming. Designing a system with extremely high concurrency, high availability and quick responsiveness needs to consider many aspects **all the way fromfrontend to backend**. See the below picture for details:

**Design principles**

: 1. Less is more - less element on the web page, fewer data queries to the database, fewer web requests, fewer system dependencies 2. Short critical path - fewer hops among services or merge into one service 3. Async - use message queues to handle high TPS 4. Isolation - isolate static and dynamic contents, isolate processes and databases for rare items 5. Overselling is bad. When Decreasing the inventory is important

6. User experience is important. We definitely don’t want to inform users that they have successfully placed orders but later tell them no items are actually available
