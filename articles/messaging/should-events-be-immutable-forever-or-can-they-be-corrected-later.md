---
type: Article
title: "Should Events Be Immutable Forever, or Can They Be Corrected Later?"
source: "https://codefarm0.medium.com/should-events-be-immutable-forever-or-can-they-be-corrected-later-65867b2376ea"
author:
  - "Arvind Kumar"
published: 2026-09-20
created: 2026-09-20
description: "Deep dive on event immutability vs corrections: why editing historical events breaks downstream consumers and audits, how compensating events model corrections cleanly as new facts, consumer interpretation tradeoffs, and crypto-shredding for GDPR right to be forgotten."
tags:
  - "event-driven-architecture"
  - "kafka"
  - "event-sourcing"
  - "immutability"
  - "compensating-events"
  - "crypto-shredding"
  - "gdpr"
  - "system-design"
---

# Should Events Be Immutable Forever, or Can They Be Corrected Later?

> **Series**: Part of the [10 Event-Driven Architecture Questions](10-event-driven-architecture-questions.md) series (Deep Dive on Question 9: *Should events be immutable forever, or can they be corrected later?*)  
> **Author**: Arvind Kumar  
> **Source**: [Codefarm Medium](https://codefarm0.medium.com/should-events-be-immutable-forever-or-can-they-be-corrected-later-65867b2376ea)

An event isn’t a snapshot of the truth — it’s a record of what the system believed at a specific moment. Editing one after the fact doesn’t just fix a number; it rewrites history that other services already acted on, already reported to customers, and in a lot of industries, already handed to an auditor. The question isn’t really about mutability as a technical property — it’s about whether “what we recorded” and “what we now know” are allowed to be two different, both-true things.

![Should Events Be Immutable Forever, or Can They Be Corrected Later?](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*s8ak__gKLxlncf-LQn7uPg.png)

---

## The Setup

*Finance flags a tax miscalculation in an `InvoiceIssued` event from three weeks ago. Kavya has the event store open, about to update the row.*

**Arvind:** Before you run that — what else has already consumed that event?

**Kavya:** The ledger service booked it. The customer already got an invoice PDF with that number on it. Reporting rolled it into last month’s totals.

**Arvind:** So if you edit the stored event, what happens to all three?

**Kavya:** Nothing happens to them automatically — they already did their thing based on the wrong number and have no way of knowing it silently changed underneath them. And if anyone ever asks “what did the system say on that date,” the answer’s now been rewritten to match what we know today, not what we actually told the customer.

**Arvind:** That second part is the one that gets companies in front of auditors. Don’t edit it. What do you do instead?

---

## Compensating Events, Not Edits

**Kavya:** Publish a new event — `InvoiceCorrected` — that states the corrected tax amount as its own fact, with its own timestamp. The original `InvoiceIssued` event stays exactly as it was: wrong, but honestly wrong, on the record, at the time it happened.

**Arvind:** Why does the original need to stay wrong on the record instead of just… not existing anymore?

**Kavya:** Because “wrong at the time” is itself a fact. Accounting has done this forever — a bad ledger entry doesn’t get erased, it gets a reversing entry next to it. The history shows both what was originally recorded and what corrected it, and anyone reconstructing the timeline sees the same sequence of decisions the business actually made.

---

## One Timeline, Two Facts

![One Timeline, Two Facts](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*0RdW4ISFHSN3tX5HM6iVew.png)

**Arvind:** Both answers on the right are correct at the same time.

**Kavya:** That’s the point — immutability doesn’t mean pretending we were never wrong, it means never losing the record of what we believed and when we stopped believing it.

---

## Let Each Consumer Decide What “Current” Means

**Arvind:** Ledger, customer invoicing, and audit reporting — do they all react to `InvoiceCorrected` the same way?

**Kavya:** No, and that’s deliberate. Ledger applies it immediately, adjusting the current balance — it only ever cares about the latest truth. Audit reporting keeps both entries visible, because its whole job is showing what was known at each point in time, not just the ending state. Customer-facing invoicing probably needs a human-readable “corrected invoice” notice, not a silent number change, because the customer already saw the original.

![Let Each Consumer Decide What Current Means](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*8rlKTx5MCARrW0Gx3eHGrw.png)

**Arvind:** So the event stream stays one source of truth, but “truth” isn’t the same question for all three.

**Kavya:** Right — the aggregate that needs current state just applies the correction like any other version bump. The one that needs history keeps every version. Same stream, different question being asked of it.

---

## This Is Just Another Versioned Event

**Arvind:** Does this need special-case logic in the aggregate, on top of the version check from the consistency question?

**Kavya:** No — that’s what makes it clean. `InvoiceCorrected` is just the next version, applied through the same guard clause as anything else.

```python
def apply(aggregate, event):
    if event.version <= aggregate.current_version:
        return aggregate  # stale/duplicate — unchanged

    aggregate.state = transition(aggregate.state, event)  # correction is just another transition
    aggregate.current_version = event.version
    return aggregate
```

**Arvind:** So the versioning discipline from question one and the “don’t edit history” rule here are actually the same rule, applied to a different kind of event.

**Kavya:** Same rule. A correction isn’t a special case — it’s just the next fact in the sequence.

---

## The One Real Exception: The Right to Be Forgotten

**Arvind:** GDPR erasure requests don’t care about your audit philosophy. What happens when someone legally has to disappear from the event log?

**Kavya:** You don’t rewrite the log — you make the data in it unrecoverable instead. Encrypt personal fields per-user at write time, and when erasure is required, delete that user’s key rather than the events. The event shells stay immutable and structurally unchanged; the personal data inside them becomes permanently unreadable.

```python
def record_event(event, user_id):
    key = key_store.get_or_create_key(user_id)
    event.personal_fields = encrypt(event.personal_fields, key)
    append(event)

def erase_user(user_id):
    key_store.delete_key(user_id)  # event log untouched — payload now unrecoverable
```

**Arvind:** So immutability and erasure aren’t actually in conflict.

**Kavya:** Not once you stop thinking of “erase” as “delete the record” and start thinking of it as “delete the ability to ever read the record again.”

---

## Kafka-Specific Notes

**Arvind:** Does Kafka enforce any of this for us?

**Kavya:** Structurally, yes — a committed record in a Kafka log can’t be edited in place at all, so “just patch the old event” was never actually on the table technically, only conceptually, via some rebuild-and-republish workaround. Log compaction doesn’t change that — it only drops older records for the same key to save space, it doesn’t rewrite the ones it keeps. For anything with compliance requirements, that just means setting retention long enough — or using tiered storage — so the history compaction would otherwise reclaim is still there when someone needs to reconstruct it.

---

## The Answer, Compressed

**Kavya:** Prefer immutability — an event is a record of what was believed at a point in time, and editing it erases that fact for every consumer that already acted on it, plus anyone who’ll ever need to audit the decision. Corrections are new events, not edits, published as their own fact with their own timestamp, so both “what we believed then” and “what we know now” stay queryable. Consumers decide for themselves what “current” means — some apply corrections immediately, some keep the full history visible — and the one real exception, legally mandated erasure, is solved by destroying the decryption key, not the event.

---

## Conclusion

The instinct to “just fix” a bad event comes from treating the event log like a database row instead of a historical record. Once it’s treated as history, the right move stops being a mystery: you don’t edit history, you add to it. Compensating events keep the audit trail honest, let every consumer answer “what’s true now” without losing the ability to answer “what did we believe then,” and turn out to be the exact same versioning discipline the rest of this series already leans on.
