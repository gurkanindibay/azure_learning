---
type: Article
title: "When Microservices Become Distributed Monoliths: Warning Signs and Recovery"
description: "How good intentions quietly turn into the worst of both worlds — tightly coupled services that carry the operational complexity of microservices without the primary benefit of deployment independence — and how to recover."
source: "https://medium.com/@erwindev/when-microservices-become-distributed-monoliths-warning-signs-and-recovery-65af6086da3a"
author: "Erwin Hermanto"
published: 2026-04-03
timestamp: 2026-04-03T00:00:00Z
---

# When Microservices Become Distributed Monoliths: Warning Signs and Recovery

> **Author**: Erwin Hermanto  
> **Published**: 2026-04-03  
> **Source**: [Medium](https://medium.com/@erwindev/when-microservices-become-distributed-monoliths-warning-signs-and-recovery-65af6086da3a)  
> **Takeaways**: [Microservices & Service Design — Key Takeaways](../../system-design-architecture/48-svc-distributed-monolith-key-takeaways.md)

---

How good intentions quietly turn into the worst of both worlds — and what to do about it.

## I Didn't Know I Was Building the Wrong Thing

My first "microservices" job was at a fintech startup around 2018. We had nine
services, Kubernetes, Helm charts, Prometheus dashboards on a big TV in the
office — the works. We felt modern. We felt like engineers at Google.

Then our on-call rotation started.

Every Saturday night like clockwork, a payment timeout would cascade across the
entire platform. To fix the `payment-service`, you had to redeploy `notification-service` first. To redeploy `notification-service`, someone from the `user-service` team had to approve the migration because they shared a Postgres schema. It took three engineers and a Slack war room to push what should have been a two-line config change.

It was only months later, deep in a post-mortem, that a senior engineer said the quiet part out loud: "We didn't build microservices. We built a distributed monolith."

That phrase hit like a diagnosis. Suddenly everything made sense — all the pain, the 2 AM pages, the deployment spreadsheets. We had taken a monolith, cut it into pieces, spread it across a network, and kept all the coupling that made the monolith painful in the first place.

> **Note**: This is a Medium members-only story. The excerpt above is from the publicly visible preview. Full article requires a Medium membership.