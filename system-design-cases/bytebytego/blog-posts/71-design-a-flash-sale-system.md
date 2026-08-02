---
okf_version: "0.1"
type: concept
---

# Design a flash sale system

> **Source**: ByteByteGo — System Design compilation PDF

![Design a flash sale system](images/img-075.jpeg)

Black Friday is coming. Designing a system with extremely high
concurrency, high availability and quick responsiveness needs to
consider many aspects 𝐚𝐥𝐥 𝐭𝐡𝐞 𝐰𝐚𝐲 𝐟𝐫𝐨𝐦𝐟𝐫𝐨𝐧𝐭𝐞𝐧𝐝 𝐭𝐨 𝐛𝐚𝐜𝐤𝐞𝐧𝐝. See the
below picture for details:
𝐃𝐞𝐬𝐢𝐠𝐧 𝐩𝐫𝐢𝐧𝐜𝐢𝐩𝐥𝐞𝐬:
1. Less is more - less element on the web page, fewer data
queries to the database, fewer web requests, fewer system
dependencies
2. Short critical path - fewer hops among services or merge into
one service
3. Async - use message queues to handle high TPS
4. Isolation - isolate static and dynamic contents, isolate processes
and databases for rare items
5. Overselling is bad. When Decreasing the inventory is important

6. User experience is important. We definitely don’t want to inform
users that they have successfully placed orders but later tell
them no items are actually available

