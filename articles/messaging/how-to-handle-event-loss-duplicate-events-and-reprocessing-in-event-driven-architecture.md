---
type: Article
title: "How to Handle Event Loss, Duplicate Events, and Reprocessing in Event-Driven Architecture"
source: "https://codefarm0.medium.com/how-to-handle-event-loss-duplicate-events-and-reprocessing-in-event-driven-architecture-70b57dff6a2e"
author:
  - "Arvind Kumar"
published: 2026-09-10
created: 2026-09-12
description: "How to handle event loss, duplicate delivery, and historical reprocessing in event-driven architecture by separating producer durability, consumer idempotency, and deterministic replay."
tags:
  - "event-driven-architecture"
  - "kafka"
  - "messaging"
  - "idempotency"
  - "durability"
  - "system-design"
---

# How to Handle Event Loss, Duplicate Events, and Reprocessing in Event-Driven Architecture

> **Series**: Part of the [10 Event-Driven Architecture Questions](10-event-driven-architecture-questions.md) series (Deep Dive on Question 2: *How do you handle event loss, duplicate events, and reprocessing in event-driven architecture?*)  
> **Author**: Arvind Kumar  
> **Source**: [Codefarm Medium](https://codefarm0.medium.com/how-to-handle-event-loss-duplicate-events-and-reprocessing-in-event-driven-architecture-70b57dff6a2e)

"At-least-once delivery" sounds like one guarantee, so teams tend to build one mitigation for it and call the problem solved. In practice it unpacks into three separate failure modes — an event never arriving, an event arriving more than once, and an event (or a million of them) being replayed deliberately — and each one breaks a different part of the system if you don’t treat it as its own problem.

![Three failure modes: Event Loss, Duplicate Delivery, Reprocessing](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*JlB__YYqJP4AoMihMjT-cg.png)

This deep dive plays that distinction out as a conversation between an interviewer and a candidate, the same way question 1 did. It covers why event loss, duplicates, and reprocessing need three different fixes rather than one shared "retry and hope" strategy, what each fix actually looks like, how this maps onto Kafka’s specific knobs, and the harder follow-ups — dedup without a natural key, side effects that aren’t naturally idempotent, and replaying millions of events safely — that separate a rehearsed answer from real operational experience.

---

## The Question

**Arvind (Interviewer):** Event loss, duplicate events, reprocessing — people usually lump these together as "delivery problems." Are they the same problem?

**Kavya (Candidate):** No. They have different causes and different fixes. Treating them as one problem is usually why teams get surprised in production.

**Arvind:** Convince me. Give me one line on each.

**Kavya:** Event loss is an event that never makes it — a producer or broker failure. Duplicates are an event that makes it more than once — a retry or a redelivery. Reprocessing is deliberately replaying events you already have, usually after a bug fix or a migration.

**Arvind:** So three different failure surfaces. Let’s go through them one at a time.

---

## Problem 1: Event Loss

**Arvind:** Where does an event actually get lost?

**Kavya:** Two places, mainly. The producer sends it and never gets an acknowledgment — maybe the broker was unreachable and the producer didn’t retry. Or the broker accepted it but a leader failed before it replicated, so the write never survived.

**Arvind:** So the fix is "retry harder"?

**Kavya:** Retry on the producer side, yes, but that’s only half of it. The other half is broker durability — the write isn’t safe until enough replicas have it, not just the leader. If you configure the producer to move on after the leader acks but before replicas catch up, a leader failure loses the event even though the producer thinks it succeeded.

**Arvind:** So this is a producer-and-broker configuration problem, not a consumer problem.

**Kavya:** Exactly. By the time a consumer is involved, the event either exists durably or it doesn’t — the consumer can’t recover data that was never actually persisted.

---

## Problem 2: Duplicate Events

**Arvind:** Now duplicates. Where do those come from, if loss is already handled?

**Kavya:** Ironically, from the fix for event loss. At-least-once delivery means the producer or the broker will resend anything it isn’t sure was fully processed — so a consumer that crashes after processing an event but before committing its offset will see that same event again.

**Arvind:** So duplicates are the cost of guaranteeing no loss.

**Kavya:** Right — you can’t have zero loss and zero duplicates with simple retry-based delivery. You pick "at-least-once, possibly duplicated" and push the guarantee down to the consumer instead.

**Arvind:** How does the consumer push back?

**Kavya:** Idempotency. Every event carries a stable identifier, the consumer records which identifiers it’s already handled, and processing is a no-op the second time the same identifier shows up.

```c
FUNCTION handle(event):
    IF dedupStore.hasProcessed(event.id):
        RETURN                          // duplicate — safe no-op
    applyBusinessEffect(event)
    dedupStore.markProcessed(event.id)  // same transaction as the effect
```

**Arvind:** That last comment — "same transaction" — why does that matter?

**Kavya:** Because if marking the event as processed and applying its effect aren’t atomic, a crash between the two steps reopens the exact duplicate problem this was supposed to close. Either both happen or neither does.

---

## Problem 3: Reprocessing

**Arvind:** Last one — reprocessing. How is that different from a duplicate?

**Kavya:** A duplicate is accidental — the system redelivers something without being asked. Reprocessing is deliberate — someone resets a consumer offset and replays a whole history of events on purpose, usually to fix a bug or rebuild a read model.

**Arvind:** So the dedup store from problem two doesn’t help here?

**Kavya:** Not by itself, no — because the events aren’t unexpected duplicates, they’re the entire history being fed through again. What has to hold is that the consumer is deterministic: feeding it the same sequence of events twice produces the same final state both times.

**Arvind:** What breaks that determinism in practice?

**Kavya:** Anything that isn’t a pure function of the event stream — reading current wall-clock time inside the transition logic, calling out to another service’s live state, or worst of all, triggering an external side effect like sending an email or charging a card as part of the replay.

---

## Seeing the Three Side by Side

**Arvind:** Why is "discard" green in the duplicates lane but "same final state" is the green outcome in reprocessing, not "discard"?

**Kavya:** Because they’re solving different shapes of the same idea. Duplicates get discarded individually as they show up unexpectedly. Reprocessing re-applies everything on purpose — the win condition isn’t discarding, it’s that reapplying everything still lands you exactly where you started.

---

## Duplicates in Motion

**Arvind:** Walk me through an actual duplicate delivery end to end.

**Kavya:** Producer publishes a payment-captured event. Consumer picks it up, checks the dedup store — not seen before — processes it, charges nothing extra since this is the first time, and records the id. But it crashes right before committing its Kafka offset.

![Duplicate delivery timeline on consumer crash prior to offset commit](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*-huG_VHtpgaAZMKMx-tVJQ.png)

**Arvind:** So the offset being uncommitted is what causes the redelivery, and the dedup store is what makes the redelivery harmless.

**Kavya:** That’s the whole pattern in one sentence, yes.

---

## Now Make It Kafka-Specific

**Arvind:** Let’s ground all three in actual Kafka settings. Start with loss.

**Kavya:** `acks=all` on the producer, so it waits for the full in-sync replica set, not just the leader. Pair that with `min.insync.replicas` set above one on the broker side, so a single replica isn't considered "enough" to acknowledge a write. Enable producer retries with idempotence turned on so a retried send doesn't itself create a duplicate at the broker level.

**Arvind:** That idempotent producer setting — does that solve problem two for me automatically?

**Kavya:** Only for producer-to-broker duplicates on retry — it stops the same producer instance from writing the same message twice because of a retried request. It does nothing about a consumer processing the same message twice after redelivery, which is a completely different point in the pipeline. The consumer-side dedup store is still necessary.

**Arvind:** And reprocessing?

**Kavya:** That’s a consumer offset operation — seeking back to an earlier offset, or spinning up a new consumer group that starts from the beginning of the topic. Kafka is happy to replay as far back as retention allows; whether that’s safe is entirely about whether your consumer logic is deterministic, which is a design property, not a broker setting.

---

## "There’s No Natural Event ID — Now What?"

**Arvind:** Suppose the event doesn’t come with a clean unique identifier.

**Kavya:** Then I’d generate one from the content that has to be unique — a hash of the immutable fields, or a composite key like entity ID plus version, assuming that pair can’t legitimately repeat. Failing that, the producer should be the one assigning a UUID at creation time, because retrofitting uniqueness on the consumer side after the fact is much harder to get right.

**Arvind:** Does the dedup store grow forever?

**Kavya:** No — it only needs to remember as far back as redelivery can plausibly reach, so a TTL tied to your retry and rebalance windows keeps it bounded instead of an unbounded ledger of every event ever seen.

---

## "Side Effects Aren’t Naturally Idempotent"

**Arvind:** Charging a card or sending an email isn’t idempotent by nature. How does the dedup store help there?

**Kavya:** The dedup store prevents the consumer from re-triggering that call at all for an event it’s already handled — that’s the first line of defense. But belt-and-suspenders, the downstream call itself should carry an idempotency key too, if the provider supports one, so that even a gap in your own dedup logic doesn’t turn into a duplicate charge on their end.

**Arvind:** And for reprocessing specifically — replaying a million events that each used to send an email?

**Kavya:** That’s exactly why side effects need to be separated from state derivation. Rebuilding a read model from the full event history should be pure — no external calls. Anything that triggers a real-world action needs an explicit guard, like a flag marking "this is a replay, suppress side effects," or routing side-effect triggering through its own idempotent, already-deduped path that isn’t touched by a state-rebuild replay at all.

---

## The Answer, Compressed

**Arvind:** Give me the thirty-second version.

**Kavya:** Loss is a producer-and-broker durability problem — fixed with acknowledgment and replication settings, not consumer logic. Duplicates are the accepted cost of at-least-once delivery — fixed with an idempotent consumer that checks a dedup store before applying an effect, atomically with recording it. Reprocessing is intentional replay — safe only if the consumer is deterministic and side effects are kept separate from state rebuilding. Same broker, three different failure shapes, three different fixes.

**Arvind:** That’s the answer.

---

## Conclusion

The instinct to solve "delivery reliability" with a single retry-and-dedupe layer is understandable, but it collapses three genuinely different failure modes into one, and the fix for one doesn’t cover the other two:
- **Event loss** is closed at the producer and broker (`acks=all`, `min.insync.replicas > 1`, idempotent retries).
- **Duplicates** are closed at the consumer, with an atomic check-and-record step against a dedup store.
- **Reprocessing** is closed by consumer determinism and by keeping side effects out of the replay path entirely.

Get these three apart cleanly, and the idempotent-consumer discipline here plugs directly into the versioned-aggregate pattern from question 1 — the same aggregate that ignores stale versions is exactly what makes replayed history land safely.