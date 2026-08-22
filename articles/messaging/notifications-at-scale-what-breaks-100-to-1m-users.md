---
type: Article
title: "Notifications at Scale: What Breaks When You Go From 100 Users to 1,000,000"
source: "https://medium.com/@niketl16/notifications-at-scale-what-breaks-when-you-go-from-100-users-to-1-000-000-63f45feafabe"
author: "Niket Lekariya"
published: 2026-07-30
created: 2026-08-22
description: "A system design walkthrough exploring what breaks when fanout operations scale from 100 to 1,000,000 users: asynchronous queues, worker autoscaling, provider rate limits, idempotency, batching, and DLQs."
---

# Notifications at Scale: What Breaks When You Go From 100 Users to 1,000,000

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*vOBeOtgFuqCBNVo0lMBZgA.png)

## A system design walkthrough for the moment “just send a notification” stops being simple

Every engineer has written this function at some point:

```python
for user in all_users:
    send_notification(user)
```

It works. It ships. It even survives a demo. Then one day someone asks you to send that same notification to a million users at once — a flash sale, a breaking-news alert, a midnight product launch — and the same code that worked fine in staging quietly takes down your API.

This isn’t really a story about notifications. It’s a story about what happens the moment a system moves from “handle one request” to “handle one request that fans out into a million follow-up actions.” The same lessons apply to bulk emails, report generation, video transcoding, or any workload where one user action triggers massive downstream work. Notifications are just a clean, relatable way to walk through it.

Here’s how the design evolves, one failure at a time.

## Attempt one: just loop and send

The naive version sends notifications synchronously, inside the same request that triggered the campaign. For ten users, this is invisible. For ten thousand, the request starts taking noticeably longer. For a million, it never finishes — the connection times out, the thread pool fills up, and every other request on that server starts queuing behind work it has nothing to do with.

The underlying mistake is subtle: the code conflates two very different jobs. **Deciding a notification needs to be sent** is fast and cheap. **Actually delivering it** — a network call to a push provider, retry handling, waiting on a response — is slow and unreliable. Bolting the second job onto the first means every request now inherits the worst-case latency of a third-party API multiplied by a million.

## Attempt two: separate acceptance from delivery

The fix is to stop doing the work in the request path at all. When a campaign is triggered, the API’s only job is to record that the campaign exists and hand off the actual delivery work to something else — typically a message queue like Kafka, RabbitMQ, or a managed option like SQS.

The API call now does almost nothing: validate the request, write a record, publish a message, return. It finishes in milliseconds regardless of whether the campaign targets ten people or ten million, because it’s no longer the thing doing the sending.

A separate pool of background workers pulls jobs off the queue at whatever pace it can sustain. If workers fall behind, the queue simply holds more messages — it doesn’t reject them, and it doesn’t slow down the API that’s still accepting new requests.

This single change — moving delivery out of the request/response cycle — is usually the biggest unlock in the whole design. Everything after this point is about tuning how the workers behave, not rethinking the API.

## Why a queue instead of just “more threads”

It’s tempting to think a thread pool would solve the same problem, but a queue gives you something threads don’t: a durable buffer that survives crashes and absorbs uneven load. If a worker dies mid-shift, an in-memory thread pool loses whatever it was holding. A message sitting in Kafka or SQS is still there when a new worker comes online.

It also decouples *how fast the queue fills* from *how fast the queue drains*. A traffic spike just makes the queue temporarily longer — it doesn’t make anything error out. That’s a much healthier failure mode than a spike making requests start timing out.

## Scaling the pieces independently

Once delivery lives in workers instead of the API, each part of the system can scale according to its own bottleneck instead of scaling together as one blob.

- The **API tier** only needs to handle incoming campaign requests, which is a small, predictable load. It rarely needs to grow.
- The **worker tier** needs to grow with queue depth. A quiet Tuesday might need five workers; a midnight flash sale might need five hundred. Autoscaling based on queue length handles this cleanly.

This separation also makes the system easier to reason about — a spike in campaign volume shows up as a longer queue and more workers, not as a mysteriously slow API.

## The next wall: the provider’s rate limit

Scaling workers solves the “our own infrastructure can’t keep up” problem. It does nothing for the next one: the push notification provider, SMS gateway, or email service you’re calling almost certainly enforces a rate limit of its own.

Adding more workers past that point doesn’t help — it just means more of them get rejected or throttled at the same time. It’s the equivalent of adding more cashiers to a store that only has one exit door; the bottleneck was never at the registers.

The fix is for workers to self-throttle to match what the provider actually allows, and to treat a growing queue as acceptable back-pressure rather than a problem to be solved by adding capacity. A queue that’s temporarily long is fine. A provider that starts blocking your account because you ignored its limits is not.

## Making retries safe: idempotency

Distributed systems fail in ordinary, boring ways — a worker restarts mid-job, a network call times out after the provider already processed it, a queue redelivers a message it thinks failed. None of this is exotic; it happens constantly at scale.

The dangerous version of this problem is a worker that successfully sends a notification, then crashes before it can record that success. From the queue’s point of view, the job failed and gets retried — and now the same person gets the same notification twice.

The standard fix is giving every job a unique ID and having the worker check, before doing anything, whether that ID has already been completed. If it has, the worker skips it. This turns a retry from “maybe duplicate the side effect” into “safely do nothing.” It’s the same pattern that payment systems rely on, for exactly the same reason — a duplicate notification is annoying, but a duplicate charge is a real problem.

## Doing less work: batching

Most notification providers accept batched requests — hundreds of messages in a single API call instead of one call per message. Sending a million notifications one at a time means a million round trips. Batching in groups of a few hundred can turn that into a few thousand.

This is one of those optimizations that has nothing to do with clever code and everything to do with simply asking the network to do less. Fewer calls means lower latency, lower cost, and less exposure to whatever rate limit the provider enforces.

## Not every failure deserves a retry

Some failures are temporary — a brief network blip, a provider having a bad minute. Others are permanent — a device token that no longer exists because the app was uninstalled months ago. Treating both the same way wastes resources chasing a delivery that will never happen.

A more deliberate approach uses exponential backoff for genuine transient errors, spacing out retry attempts instead of hammering the provider immediately. When a job has failed enough times, it gets moved into a dead letter queue instead of being retried forever. That queue becomes something a human — or a separate cleanup process — can inspect later, without holding up everything else moving through the pipeline.

Production systems aren’t designed assuming nothing goes wrong. They’re designed so that when something does, the failure stays small and contained instead of spreading.

## What changes at 100 million instead of 1 million

At some point, even “publish everything to the queue up front” becomes the wrong move. Pushing 100 million messages onto a queue in one burst is technically possible, but it creates exactly the kind of traffic spike the whole design was trying to avoid — just moved one layer over.

A steadier approach is to store the campaign as a definition rather than as a pile of individual jobs, and have a background process generate and enqueue those jobs gradually over time. The queue stays at a manageable depth throughout, and the system makes continuous progress instead of trying to do everything in one instant. This is a recurring pattern in large-scale systems: rather than handling the biggest possible case all at once, they handle a steady stream of the same case indefinitely.

## Delivery is not the same question as “did it work”

Sending the notification is only half of what people actually want to know. Marketing teams ask how many messages were delivered, how many opened, and how many failed — and that reporting shouldn’t live inside the same pipeline responsible for sending.

Most providers emit delivery status callbacks, which can feed a separate, asynchronous analytics pipeline. Keeping that pipeline independent means a burst of reporting events doesn’t compete for the same resources as the actual sending path — the same separation-of-concerns idea that shows up everywhere else in this design.

## Putting it together

Laid end to end, the pattern looks like this:

1. The API accepts a campaign request and immediately hands it off — it does no sending itself.
2. A message queue absorbs the job and buffers against spikes.
3. An independently scaled pool of workers pulls jobs and does the actual delivery.
4. Workers throttle themselves to match the notification provider’s limits, letting the queue grow rather than overwhelming the provider.
5. Every job is idempotent, so retries after a crash never cause duplicate sends.
6. Delivery calls are batched wherever the provider supports it, cutting the number of network round trips dramatically.
7. Permanent failures get exponential backoff and eventually land in a dead letter queue instead of retrying forever.
8. Extremely large campaigns are drip-fed into the queue by a background generator instead of dumped in all at once.
9. Delivery status and analytics run through their own asynchronous pipeline, separate from sending.

None of these nine ideas is complicated on its own. What makes the system work is that each one solves a specific, narrow failure mode, and none of them depend on simply buying bigger servers. That’s really the core shift: scaling a system like this isn’t about raw compute, it’s about giving each part of the pipeline room to fail and recover without taking the rest down with it.

The hard part was never sending one notification. It’s making sure a million of them don’t bring down everything else along the way.