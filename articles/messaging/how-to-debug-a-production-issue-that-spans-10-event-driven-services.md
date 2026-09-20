---
type: Article
title: "How to Debug a Production Issue That Spans 10 Event-Driven Services"
source: "https://codefarm0.medium.com/how-to-debug-a-production-issue-that-spans-10-event-driven-services-ac406cd5764f"
author:
  - "Arvind Kumar"
published: 2026-09-19
created: 2026-09-20
description: "How to debug production issues spanning multiple event-driven microservices using correlation IDs, causation IDs, distributed context propagation across message brokers, consumer lag analysis, and dead-letter topic inspection."
tags:
  - "event-driven-architecture"
  - "kafka"
  - "observability"
  - "distributed-tracing"
  - "messaging"
  - "system-design"
  - "debugging"
---

# How to Debug a Production Issue That Spans 10 Event-Driven Services

> **Series**: Part of the [10 Event-Driven Architecture Questions](10-event-driven-architecture-questions.md) series (Deep Dive on Question 8: *How do you debug a production issue when a single business flow spans 10 event-driven services?*)  
> **Author**: Arvind Kumar  
> **Source**: [Codefarm Medium](https://codefarm0.medium.com/how-to-debug-a-production-issue-that-spans-10-event-driven-services-ac406cd5764f)

A synchronous system gives you a call stack for free — one request, one thread, one trace, top to bottom. An event-driven flow spanning ten services gives you none of that by default: ten sets of logs, ten deploy timelines, and no shared thread to follow unless someone designed one in ahead of time. This question isn’t really about debugging technique — it’s about whether observability was built before the incident, because there’s no way to build it during one.

![Event-driven flow spanning multiple services](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*N0wEAWHo01dOfkTM34jlqQ.png)

---

## The Setup

*Incident bridge. A customer’s order has been stuck between "placed" and "shipped" for two hours. Kavya is on call. Ten services touch this flow somewhere.*

**Arvind:** Where do you start?

**Kavya:** Order ID from the support ticket. Let me grep the order service’s logs for it.

**Arvind:** That tells you Order Service did its job. It doesn’t tell you which of the other nine services is the one that dropped it.

**Kavya:** I could grep each service’s logs around the same timestamp…

**Arvind:** With what shared key? Nine different services, nine different log formats, and clocks that aren’t perfectly synced. You’re pattern-matching on timing, not on identity. That’s not debugging, that’s guessing with extra steps.

---

## The Missing Piece: A Thread Through the Whole Flow

**Arvind:** What should tie every log line and every event across all ten services back to this one order?

**Kavya:** A **correlation ID** — generated once, when the order is placed, and carried in every single event’s metadata from then on, no matter how many services it passes through or how many new events it triggers along the way.

**Arvind:** Is that the same thing as an event ID?

**Kavya:** No. **Event ID** is unique per event. **Correlation ID** is shared across every event in the same business flow. And there’s a third one worth having — **causation ID**, the specific event that directly caused this one — so you’re not just looking at a flat pile of events with the same correlation ID, you can reconstruct the actual cause-and-effect tree.

---

## The Envelope, Not Just the Payload

![Event Envelope Structure with Metadata and Payload](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*vqs8vPs7SRY-W7BelsGezw.png)

**Arvind:** None of this is optional metadata you add when things get complicated.

**Kavya:** Right — it has to be in the envelope from the first service that ever publishes an event in this flow, or every event upstream of when someone finally added it is permanently untraceable. You can’t retrofit a correlation ID onto history that was never recorded.

---

## The Flow, With and Without the Thread

![Timeline reconstruction with and without correlation thread](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*FYMwyliQ2hy8S-B7BCoscg.png)

**Arvind:** Querying every event with `correlation_id = abc123`, ordered by time, across all ten services' topics — what does that get you that grepping logs doesn't?

**Kavya:** A complete, ordered timeline of exactly what happened to this one order, regardless of which service or topic it touched — and just as importantly, where the timeline simply stops. Here it stops after `PaymentCharged`. Inventory Service consumed it and never published `InventoryReserved`. That's the entire search space narrowed from ten services to one, in one query.

---

## Tracing Across an Async Boundary

**Arvind:** Distributed tracing usually rides on the call stack — a synchronous HTTP call passes trace context in a header automatically. There’s no call stack here. How does a trace survive a hop through a broker?

**Kavya:** The producer has to propagate it manually — read the current trace context, write it into the outgoing event’s headers, and the next service’s consumer has to read those headers and continue the same trace instead of starting a new one. Nothing does this for you across a broker the way an HTTP framework does across a request.

```typescript
function publish(event: BusinessEvent, currentTraceContext: TraceContext): void {
    event.headers.traceparent = currentTraceContext.serialize();
    event.headers.correlation_id = currentTraceContext.correlationId;
    event.headers.causation_id = currentTraceContext.currentEventId;
    broker.send(event);
}

function onConsume(event: BusinessEvent): void {
    const traceContext = TraceContext.parse(event.headers.traceparent);
    const span = tracer.startSpan("handle " + event.type, { parent: traceContext });
    try {
        // ... process event ...
    } finally {
        span.end();
    }
}
```

**Arvind:** Miss that in one service, and?

**Kavya:** The trace just ends there and picks back up as a disconnected, orphaned trace in the next service — which looks exactly like the service doing nothing, even if it processed the event correctly. It has to be wired into every single hop, not most of them.

---

## Finding the Actual Fault

**Arvind:** Timeline says Inventory Service is where it stops. What’s next?

**Kavya:** **Consumer lag first** — is Inventory’s consumer group behind, meaning the event is just sitting unprocessed in the backlog? If lag is normal, it’s not a backlog problem, it already tried to process this specific event and something went wrong.

**Arvind:** And if lag is normal?

**Kavya:** Check its **dead-letter topic** for this event ID. If it’s there, the consumer already tried, failed — probably a downstream inventory database timeout or a schema validation error — and routed it there instead of blocking the rest of the topic.

![Triage path: Timeline stop -> Consumer Lag -> Dead-Letter Topic](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*VmJJ_K-HoNpNnqCG-Nf9ng.png)

---

## Kafka-Specific Notes

**Arvind:** What’s Kafka-specific in all of this?

**Kavya:** Trace context and correlation ID both ride as message headers, not payload fields, so they survive regardless of schema version. Consumer lag comes from the consumer group’s committed offset versus the log end offset — exported to whatever metrics stack you’re already using. And every consumer that can fail needs its own dead-letter topic, with enough of the original event and error context attached to explain why it landed there, not just that it did.

---

## The Answer, Compressed

**Kavya:** You can’t debug a ten-service flow with logs and clocks alone — you need:
1. A **correlation ID** generated once and carried through every event’s metadata.
2. A **causation ID** to reconstruct the actual cause-and-effect chain.
3. **Trace context** propagated manually through headers at every hop, since brokers don’t do that automatically.

Debugging becomes:
1. Query the whole timeline by correlation ID.
2. Find where it stops.
3. Check that service’s consumer lag and dead-letter topic to find out why.

None of this works if it’s bolted on after the first incident — the envelope has to carry these fields from the very first service that ever publishes into the flow.

---

## Conclusion

Ten services reacting to each other’s events is not inherently a black box — it becomes one only when nobody designed a way to see across the boundaries between them. Correlation IDs, causation IDs, and trace context turn a scattered pile of per-service logs into one ordered timeline, and consumer lag plus dead-letter topics turn “somewhere in there, something went wrong” into a specific event, in a specific service, with a specific reason. All of it has to be there before the incident starts — this is observability you design in, not tooling you reach for once things go wrong.

---

## Related Articles

- [10 Event-Driven Architecture Questions That Separate Architects from Framework Users](10-event-driven-architecture-questions.md)
- [How to Handle Event Loss, Duplicate Events, and Reprocessing in Event-Driven Architecture](how-to-handle-event-loss-duplicate-events-and-reprocessing-in-event-driven-architecture.md)
- [How to Guarantee Business Consistency in Event-Driven Architecture When Events Arrive Out of Order](how-to-guarantee-business-consistency-in-event-driven-architecture-when-events-arrive-out-of-order.md)
- [How to Design Event-Driven Consumers That Survive Replaying Millions of Old Events](how-to-design-event-driven-consumers-that-survive-replaying-millions-of-old-events.md)
- [What the Outbox Pattern Actually Solves — and What It Doesn't](what-the-outbox-pattern-actually-solves-and-what-it-doesnt.md)
